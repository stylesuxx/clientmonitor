import sys
sys.path.append('./src')

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
