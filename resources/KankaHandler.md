<a id="KankaHandler"></a>

# KankaHandler

<a id="KankaHandler.KankaHandler"></a>

## KankaHandler Objects

```python
class KankaHandler()
```

<a id="KankaHandler.KankaHandler.kanka_get"></a>

#### kanka\_get

```python
def kanka_get(query)
```

This function issues a GET request to Kanka given the query. It
supports both full http urls as well as local query inside the
campaign.

<a id="KankaHandler.KankaHandler.kanka_sync_endpoint"></a>

#### kanka\_sync\_endpoint

```python
def kanka_sync_endpoint(endpoint, force=False)
```

For a given endpoint fetch all entries from Kanka that have been
updated since the last fetch.

<a id="KankaHandler.KankaHandler.kanka_sync"></a>

#### kanka\_sync

```python
def kanka_sync(force=False)
```

This function syncs all endpoints in self.endpoints at once.

<a id="KankaHandler.KankaHandler.generate_mentions"></a>

#### generate\_mentions

```python
def generate_mentions(force=False)
```

This method should go through the local json files and generate a new
field, which contains a list of mentions inside the entitys entry or
posts.

<a id="KankaHandler.KankaHandler.get_index"></a>

#### get\_index

```python
def get_index()
```

construct a dictionary for each entpoint mapping ids to names

