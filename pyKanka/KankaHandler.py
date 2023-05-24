import time
import requests
import json
import re
import os
from pathlib import Path

class KankaHandler:
    stem = "https://kanka.io/api/1.0/"
    campaign = "campaigns/81441/"
    path_stem = Path.cwd()
    with open(path_stem / 'key.txt', 'r') as f:
        key = f.read()

    headers = {"Authorization": ("Bearer " + key),
               "Content-type": "application/json"}

    endpoints = ['characters', 'locations', 'families', 'organisations', 'items',
                 'notes', 'events', 'creatures', 'races', 'maps']

    def set_campaign(self, campaign_id):
        '''
        Change which Kanka campaign is being tracked by ID.
        '''
        self.campaign = "campaigns/" + str(campaign_id)

    def set_endpoints(self, endpoints):
        '''
        Setter function to change the locally tracked endpoints. Use this to
        change what parts of your Kanka Wiki you want to have locally tracked.
        It is possible to change this on the run if you want to inspect
        subsections of your wiki in detail.

        Inputs:

            endpoints: a list of strings containing the endpoints you wish to
            track
        '''
        self.endpoints = endpoints

    def kanka_get(self, query):
        '''
        This function issues a GET request to Kanka given the query. It
        supports both full http urls as well as local query inside the
        campaign.

        This method automatically listens for a 429 response from the server
        and throttles itself in that instance. This will lead to considerable
        wait time if this function is called frequently.

        Inputs:

            query: a string either containing the local endpoint as seen on the
            Kanka api doc or a full api url.
        '''
        if not "https://" in query:
            query = self.stem + self.campaign + query
        # send the get request
        response = requests.get(query, headers=self.headers)

        # if the server is throtteling
        if not response.ok:
            print("recieved error code: " + str(response.status_code) +
                   " at query: " + query )
            if response.status_code == 404:
                return {'data':[]}
            elif response.status_code == 429:
                print('waiting...')
                time.sleep(60)
                return self.kanka_get(query)

        # if all ok we return the json
        return response.json()

    def kanka_sync_endpoint(self, endpoint, force=False):
        '''
        For a given endpoint fetch all entries from Kanka that have been
        updated since the last fetch.

        Inputs:

            endpoint: a string containing the category of entries you wish to
            retrieve e.g. 'characters'

            force: If this is set to true all entries are redownloaded even if
            no changes have occured since the last fetch.
        '''
        # Make sure this endpoint has already been set up
        epp = self.get_endpoint_path(endpoint)
        if not epp.is_dir() or force:
            # Generate the endpoints directory and don't pass a synctime
            epp.mkdir(parents=True, exist_ok=True)
            fetch_request = endpoint + "?related=1"
        else:
            # Load local sync time  to hand to our GET request
            sync_time = ''
            with (epp / 'sync_time').open(mode='r') as f:
                sync_time = f.read()
            fetch_request = endpoint + "?realted=1&&lastSync=" + sync_time

        # Fetch updated entries from Kanka
        resp = self.kanka_get(fetch_request)

        entities = resp['data']
        link = resp['links']['next']
        while link != None:
            resp = self.kanka_get(link)
            entities += resp['data']
            link = resp['links']['next']

        # Update the sync time locally to the one returned from Kanka
        with (epp / 'sync_time').open(mode='w') as f:
            f.write(resp['sync'])

        # Load the local index so we can update it
        try:
            with (epp / '_INDEX').open(mode='r') as f:
                index = json.loads(f.read())
        except:
            index = {}

        # Iterate over the changed entries to store the changes and update the
        # index.
        for e in entities:
            e_p = self.get_posts(e)
            with (epp / (e['name'] + '.json')).open(mode='w') as f:
                f.write(json.dumps(e_p, indent=4))
            index[e['entity_id']] = e['name']

        # Store the updated index
        with (epp / '_INDEX').open(mode='w') as f:
            f.write(json.dumps(index))

    def get_posts(self, entity):
        '''
        Internal function which if given an entry will fetch all posts attached
        to the passed entity.

        Inputs:

            entity: a python dictionary containing an entities data as they are
            used throughout this code

        Returns:

            The input entity with the posts inserted into the dict at 'posts'
        '''
        query = 'entities/' + str(entity['entity_id']) + '/posts'
        entity['posts'] = self.kanka_get(query)['data']
        return entity

    def kanka_sync(self, force=False):
        '''
        This function syncs all endpoints in self.endpoints at once.

        Inputs:

            force: if set to True this will download all remote entities even
            if they have not been updated since the last fetch
        '''
        for e in self.endpoints:
            self.kanka_sync_endpoint(e, force=force)

    def generate_mentions(self, force=False):
        '''
        This method should go through the local json files and generate a new
        field, which contains a list of mentions inside the entitys entry or
        posts.

        Inputs:

            force if set to True this method will generate mentions even for
            entries that already contain 'my_mention' attribute
        '''
        # Iterate over tracked endpoints
        for endpoint in self.endpoints:
            epp = self.path_stem / 'campaign' / endpoint

            # Iterate over all files in this category
            for file in epp.glob('*.json'):
                entity = {}
                with file.open(mode='r') as f:
                    entity = json.loads(f.read())

                # If we already have a mentions entry we don't need to
                # recalculate it
                if ('my_mentions' in entity) and not force:
                    continue

                # Concat all the posts to the main entry
                content = str(entity['entry'])
                for p in entity['posts']:
                    content += p['entry']

                # This regexp should find all mentions
                matches = re.findall('\[\w*:\w*', content)
                entity['my_mentions'] = [parse_mention(x) for x in matches]
                with file.open(mode='w') as f:
                    f.write(json.dumps(entity, indent = 4))

    def generate_adjecency_list(self):
        '''
        This method generates an adjacency list of entity names for the tracked
        endpoints.

        Returns:

            a dictionary of lists where each dictionary key is a entity name
            and each dictionary value is a list of entity names mentioned in
            the keys entry and posts.
        '''
        self.generate_mentions()

        index = self.get_index()
        graph = {}
        for e in self.iter_entities():
            name = e['name']
            mentions = e['my_mentions']

            graph[name] = []
            for t, i in mentions:
                try:
                    graph[name] += [index[str(i)]]
                except:
                    pass
        return graph


    def generate_global_index(self):
        '''
        generate a global index file for all entities.
        '''
        index = {}
        for endpoint in self.endpoints:
            for entity in self.iter_entities_endpoint(endpoint):
                index[entity['entity_id']] = (endpoint, entity['name'])
        with (self.path_stem / '_INDEX').open(mode='w') as f:
            f.write(json.dumps(index, indent = 4))

        return index


    def get_index(self):
        '''
        construct a dictionary for each entpoint mapping ids to names

        Returns:
            
            a dictionary mapping entity IDs to their names.
        '''
        index = {}
        for endpoint in self.endpoints:
            epp = self.get_endpoint_path(endpoint)
            with (epp / '_INDEX').open(mode='r') as f:
                index.update(json.loads(f.read()))
        return index

    def get_endpoint_path(self, endpoint):
        '''
        Function to generate endpoint path from enpoint name
        '''
        return self.path_stem / 'campaign' / endpoint


    def iter_entities_endpoint(self, endpoint):
        '''
        Generator function that will yield all entries locally stored at a
        given endpoint
        '''
        epp = self.path_stem / 'campaign' / endpoint
        for file in epp.glob('*.json'):
            with file.open(mode='r') as f:
                entity = json.loads(f.read())
            yield entity

    def iter_entities(self):
        '''
        Generator function that yields all locally tracked entities.
        '''
        for endpoint in self.endpoints:
            epp = self.path_stem / 'campaign' / endpoint
            for file in epp.glob('*.json'):
                with file.open(mode='r') as f:
                    entity = json.loads(f.read())
                yield entity

    def kanka_cleanup(self):
        '''
        Method checks for entries that have been remotely deleted and also
        deletes them locally.
        '''
        fetch_request = 'entities'

        # Fetch updated entries from Kanka
        resp = self.kanka_get(fetch_request)

        entities = resp['data']
        link = resp['links']['next']
        while link != None:
            resp = self.kanka_get(link)
            entities += resp['data']
            link = resp['links']['next']

        # extract entity_id name pairs
        remote_names = { e['id']:e['name'] for e in entities}

        # get local pairs
        local_names = self.generate_global_index()

        # iterate over all local keys
        for e_id in local_names.keys():
            if e_id in remote_names:
                if local_names[e_id][1] == remote_names[e_id]:
                    continue
            print(local_names[e_id])
            os.remove(self.path_stem / 'campaign' / local_names[e_id][0] /
                      (local_names[e_id][1] + '.json'))



def parse_mention(mention):
    '''
    helperfunction that takes a string like '[character:3618246' and returns a
    tuple containing the catefory and entity ID seperatly.
    '''
    split = mention[1:].split(':')
    return split[0], int(split[1])

