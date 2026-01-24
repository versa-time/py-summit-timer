import serial

from summit_timer.protocol import Packet


class Transport:
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        if self.connection is None or not self.connection.is_open:
            self.connection = serial.Serial(
                self.port, self.baudrate, timeout=self.timeout
            )

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

    def send(self, data: str | Packet):
        if self.connection and self.connection.is_open:
            if isinstance(data, Packet):
                data = str(data)
            self.connection.write(data.encode() + b"\r\n")
        else:
            raise ConnectionError("Transport connection is not open.")

    def receive(self) -> Packet:
        if self.connection and self.connection.is_open:
            line = self.connection.readline()
            return Packet.from_string(line.decode().rstrip("\r\n"))
        else:
            raise ConnectionError("Transport connection is not open.")
