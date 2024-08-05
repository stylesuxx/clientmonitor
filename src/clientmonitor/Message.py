class Message:
  def __init__(self, client_id: str, version: str, payload: dict):
    self.client_id = client_id
    self.version = version
    self.payload = payload

  def get_client_id(self):
    return self.client_id

  def get_version(self):
    return self.version

  def get_payload(self):
    return self.payload

class DataMessage(Message):
  def __init__(self, client_id: str, version: str, payload: dict):
    super().__init__(client_id, version, payload)

class CloseMessage(Message):
  def __init__(self, client_id: str, version: str):
    super().__init__(client_id, version, {})
