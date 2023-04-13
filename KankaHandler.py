import time
import requests
import json
import re
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

    def kanka_get(self, query):
        '''
        This function issues a GET request to Kanka given the query. It
        supports both full http urls as well as local query inside the
        campaign.
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
        query = 'entities/' + str(entity['entity_id']) + '/posts'
        entity['posts'] = self.kanka_get(query)['data']
        return entity

    def kanka_sync(self, force=False):
        '''
        This function syncs all endpoints in self.endpoints at once.
        '''
        for e in self.endpoints:
            self.kanka_sync_endpoint(e, force=force)

    def generate_mentions(self, force=False):
        '''
        This method should go through the local json files and generate a new
        field, which contains a list of mentions inside the entitys entry or
        posts.
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


    def get_index(self):
        '''
        construct a dictionary for each entpoint mapping ids to names
        '''
        index = {}
        for endpoint in self.endpoints:
            epp = self.get_endpoint_path(endpoint)
            with (epp / '_INDEX').open(mode='r') as f:
                index.update(json.loads(f.read()))
        return index

    def get_endpoint_path(self, endpoint):
        return self.path_stem / 'campaign' / endpoint


    def iter_entities_endpoint(self, endpoint):
        epp = self.path_stem / 'campaign' / endpoint
        for file in epp.glob('*.json'):
            with file.open(mode='r') as f:
                entity = json.loads(f.read())
            yield entity

    def iter_entities(self):
        for endpoint in self.endpoints:
            epp = self.path_stem / 'campaign' / endpoint
            for file in epp.glob('*.json'):
                with file.open(mode='r') as f:
                    entity = json.loads(f.read())
                yield entity


def parse_mention(mention):
    split = mention[1:].split(':')
    return split[0], int(split[1])
