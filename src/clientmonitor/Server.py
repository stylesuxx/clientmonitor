import signal
import threading
import time
import curses
import math
import logging

from datetime import datetime

from multiprocessing.connection import Listener, Connection

from clientmonitor.Message import CloseMessage, DataMessage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("monitor.server")

class MessageRow():
  def __init__(self, message: DataMessage):
    self.message = message
    self.last_received = datetime.now()
    self.first_received = self.last_received

  def get_message(self) -> DataMessage:
    return self.message

  def get_age(self):
    return datetime.now() - self.first_received

  def update_message(self, message: DataMessage):
    self.last_received = datetime.now()
    self.message = message

class Server:
  def __init__(self, port: int, authkey: str, host: str = "localhost"):
    self.port = port
    self.host = host

    address = (self.host, self.port)
    self.listener = Listener(address, authkey=authkey.encode("utf-8"))
    self.running = True
    self.connections = {}

    self.columns = []
    self.rows = {}

    self.message_queue = []
    self.message_queue_processing = False

    self.start_time = datetime.now()

    signal.signal(signal.SIGINT, self.stop)

  def set_columns(self, columns: list[dict]) -> None:
    self.columns = columns

  def process_message(self, message: DataMessage) -> None:
    client_id = message.get_client_id()
    if client_id not in self.rows:
      message_row = MessageRow(message)
      self.rows[client_id] = message_row
    else:
      self.rows[client_id].update_message(message)

  def process_message_queue(self) -> None:
    if not self.message_queue_processing:
      self.message_queue_processing = True
      while len(self.message_queue) > 0:
        message = self.message_queue.pop(0)
        self.process_message(message)

      self.message_queue_processing = False

  def update_monitor(self) -> None:
    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(True)

    while self.running:
      now = datetime.now()
      delta = now - self.start_time
      hours = str(math.floor(delta.seconds / 3600)).zfill(2)
      minutes = str(math.floor((delta.seconds % 3600) / 60)).zfill(2)
      seconds = str(delta.seconds % 60).zfill(2)
      uptime = f"Uptime: {hours}:{minutes}:{seconds} | Server: {self.host}:{self.port}"

      age_length = 0
      client_id_length = 0
      rows = []
      for client_id in self.rows:
        if len(client_id) > client_id_length:
          client_id_length = len(client_id)

        row: MessageRow = self.rows[client_id]
        age = row.get_age()

        hours = str(math.floor(age.seconds / 3600)).zfill(2)
        minutes = str(math.floor((age.seconds % 3600) / 60)).zfill(2)
        seconds = str(age.seconds % 60).zfill(2)
        age = f"{hours}:{minutes}:{seconds}"

        if len(age) > age_length:
          age_length = len(age)

        row_columns = [client_id, age]
        for column in self.columns:
          row_data = row.get_message().get_payload()
          key = column["key"]
          length = len(column["label"])
          row_columns.append(str(row_data[key]).ljust(length))

        rows.append(row_columns)

      fields = ["ID".ljust(client_id_length), "Age".ljust(age_length)]
      for column in self.columns:
        fields.append(column["label"])

      head = " | ".join(fields)

      stdscr.clear()
      stdscr.addstr(0, 0, uptime)
      stdscr.addstr(1, 0, head)
      stdscr.addstr(2, 0, "-" * len(head))

      row_index = 3
      for row in rows:
        row_string = " | ".join(row)
        stdscr.addstr(row_index, 0, row_string)

        row_index += 1

      stdscr.refresh()
      time.sleep(1)

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()

  def start(self):
    # Start Monitoring
    monitor_thread = threading.Thread(target=self.update_monitor)
    monitor_thread.start()

    # Spawn new connections in a separate thread
    while self.running:
      try:
        conn = self.listener.accept()

        fileno = conn.fileno()
        self.connections[fileno] = conn

        t = threading.Thread(target=self.handle_connection, args=(conn,))
        t.start()
      except OSError:
        # On CTRL-C
        pass

  def stop(self, signal, frame):
    self.running = False
    self.listener.close()

  def handle_connection(self, conn: Connection) -> None:
    """
    Poll connection for new data.

    Check if message is a closing message, if so delete client ID from log and
    shut down the connection.

    Otherwise timestamp the received message and add to the queue.
    """
    while self.running:
      try:
        if conn.poll():
          message = conn.recv()
          if isinstance(message, CloseMessage):
            del self.rows[message.get_client_id()]
            break
          elif isinstance(message, DataMessage):
            self.message_queue.append(message)
            self.process_message_queue()
      except EOFError:
        # Client went away
        break

    del self.connections[conn.fileno()]
    conn.close()
