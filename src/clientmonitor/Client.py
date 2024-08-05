#import time

from multiprocessing.connection import Client as MultiProcessingClient

from clientmonitor.Message import DataMessage, CloseMessage

class Client():
  def __init__(self, id: str, port: int, authkey: str, host: str = "localhost"):
    self.id = id
    self.authkey = authkey.encode("utf-8")
    self.address = (host, port)
    self.version = "1.0.0"

  def connect(self) -> None:
    self.conn = MultiProcessingClient(self.address, authkey=self.authkey)

  def close(self) -> None:
    close_message = CloseMessage(self.id, self.version)
    self.conn.send(close_message)
    self.conn.close()

  def send(self, payload: dict) -> None:
    data_message = DataMessage(self.id, self.version, payload)
    self.conn.send(data_message)

"""
client = Client("client-1", 6666, "foobar23")
client.connect()

for i in range(0, 5):
  client.send({
    "queueLength": 100 + i,
    "internalLinkCount": 200 + i,
    "externalLinkCount": 300 + i,
  })

  time.sleep(5)

client.close()
"""