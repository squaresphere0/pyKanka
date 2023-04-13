<a id="KankaHandler"></a>

# KankaHandler

<a id="KankaHandler.KankaHandler"></a>

## KankaHandler Objects

```python
class KankaHandler()
```

<a id="KankaHandler.KankaHandler.set_endpoints"></a>

#### set\_endpoints

```python
def set_endpoints(endpoints)
```

Setter function to change the locally tracked endpoints. Use this to
change what parts of your Kanka Wiki you want to have locally tracked.
It is possible to change this on the run if you want to inspect
subsections of your wiki in detail.

Inputs:

    endpoints: a list of strings containing the endpoints you wish to
    track

<a id="KankaHandler.KankaHandler.kanka_get"></a>

#### kanka\_get

```python
def kanka_get(query)
```

This function issues a GET request to Kanka given the query. It
supports both full http urls as well as local query inside the
campaign.

This method automatically listens for a 429 response from the server
and throttles itself in that instance. This will lead to considerable
wait time if this function is called frequently.

Inputs:

    query: a string either containing the local endpoint as seen on the
    Kanka api doc or a full api url.

<a id="KankaHandler.KankaHandler.kanka_sync_endpoint"></a>

#### kanka\_sync\_endpoint

```python
def kanka_sync_endpoint(endpoint, force=False)
```

For a given endpoint fetch all entries from Kanka that have been
updated since the last fetch.

Inputs:

    endpoint: a string containing the category of entries you wish to
    retrieve e.g. 'characters'

    force: If this is set to true all entries are redownloaded even if
    no changes have occured since the last fetch.

<a id="KankaHandler.KankaHandler.get_posts"></a>

#### get\_posts

```python
def get_posts(entity)
```

Internal function which if given an entry will fetch all posts attached
to the passed entity.

Inputs:

entity: a python dictionary containing an entities data as they are
used throughout this code

**Returns**:

  
  The input entity with the posts inserted into the dict at 'posts'

<a id="KankaHandler.KankaHandler.kanka_sync"></a>

#### kanka\_sync

```python
def kanka_sync(force=False)
```

This function syncs all endpoints in self.endpoints at once.

Inputs:

    force: if set to True this will download all remote entities even
    if they have not been updated since the last fetch

<a id="KankaHandler.KankaHandler.generate_mentions"></a>

#### generate\_mentions

```python
def generate_mentions(force=False)
```

This method should go through the local json files and generate a new
field, which contains a list of mentions inside the entitys entry or
posts.

Inputs:

    force if set to True this method will generate mentions even for
    entries that already contain 'my_mention' attribute

<a id="KankaHandler.KankaHandler.generate_adjecency_list"></a>

#### generate\_adjecency\_list

```python
def generate_adjecency_list()
```

This method generates an adjacency list of entity names for the tracked
endpoints.

**Returns**:

  
  a dictionary of lists where each dictionary key is a entity name
  and each dictionary value is a list of entity names mentioned in
  the keys entry and posts.

<a id="KankaHandler.KankaHandler.get_index"></a>

#### get\_index

```python
def get_index()
```

construct a dictionary for each entpoint mapping ids to names

**Returns**:

  
  a dictionary mapping entity IDs to their names.

<a id="KankaHandler.KankaHandler.get_endpoint_path"></a>

#### get\_endpoint\_path

```python
def get_endpoint_path(endpoint)
```

Function to generate endpoint path from enpoint name

<a id="KankaHandler.KankaHandler.iter_entities_endpoint"></a>

#### iter\_entities\_endpoint

```python
def iter_entities_endpoint(endpoint)
```

Generator function that will yield all entries locally stored at a
given endpoint

<a id="KankaHandler.KankaHandler.iter_entities"></a>

#### iter\_entities

```python
def iter_entities()
```

Generator function that yields all locally tracked entities.

<a id="KankaHandler.parse_mention"></a>

#### parse\_mention

```python
def parse_mention(mention)
```

helperfunction that takes a string like '[character:3618246' and returns a
tuple containing the catefory and entity ID seperatly.

