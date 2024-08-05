import sys
sys.path.append('./src')

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
