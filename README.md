# Multi process monitor

This is a small helper library intended for monitoring multiple processes outputting the same data set, visualizing it in a ncurses table.

> Example: Multiple scrapers processing different URLs logging their progress to one central monitoring entity.

## Installation
```bash
pip install clientmonitor
```

## Usage
This library consists of a server and a client. The Server accepts connections from clients and prints data received from the clients.

The clients expect the server to be running before connecting.

### Running the server
Port and secret are mandatory, host is optional and only relevant if server and client are not being run on the same machine.

```python
from clientmonitor.Server import Server

server = Server(6666, "secret", host="localhost")
server.set_columns([
  {
    "key": "key1",
    "label": "Label for Key 1"
  },
  {
    "key": "key2",
    "label": "Label for Key 2"
  }
])
server.start()

# CTRL-C to stop
```

The columns being set are the columns that are expected to be received as data from the clients and are what the server will print.

### Running the client
```python
import time
from clientmonitor.Client import Client

client = Client("client-1", 6666, "secret")
client.connect()

for i in range(0, 5):
  client.send({
    "key1": 100 + i,
    "key2": 200 + i,
  })

  time.sleep(5)

client.close()
```

## Development
Pull request are welcome, pleas address them against the develop branch.

### Publish
```bash
python -m build
python3 -m twine upload --repository testpypi dist/*
```
