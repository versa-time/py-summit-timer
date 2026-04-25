from typing import Iterator
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
        if self.port:
            if self.connection is None or not self.connection.is_open:
                self.connection = serial.Serial(
                    self.port, self.baudrate, timeout=self.timeout
                )
        else:
            raise ValueError("Port must be specified to open transport.")

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

    def set_port(self, port: str):
        self.port = port

    def clear_input_buffer(self):
        if self.connection and self.connection.is_open:
            self.connection.reset_input_buffer()
        else:
            raise ConnectionError("Transport connection is not open.")

    def send(self, data: str | Packet):
        if self.connection and self.connection.is_open:
            if isinstance(data, Packet):
                data = str(data)
            self.connection.write(data.encode() + b"\r\n")
        else:
            raise ConnectionError("Transport connection is not open.")

    def receive(self) -> Iterator[Packet]:
        if self.connection and self.connection.is_open:
            while self.connection.in_waiting > 0:
                line = self.connection.readline().decode(encoding="ascii")
                yield Packet.from_string(line.rstrip("\r\n"))
        else:
            raise ConnectionError("Transport connection is not open.")

    def read_packet(self, timeout: float | None = None) -> Packet | None:
        if self.connection and self.connection.is_open:
            original_timeout = self.connection.timeout
            try:
                if timeout is not None:
                    self.connection.timeout = timeout
                line = self.connection.readline().decode(encoding="ascii")
            finally:
                self.connection.timeout = original_timeout

            if not line:
                return None

            return Packet.from_string(line.rstrip("\r\n"))

        raise ConnectionError("Transport connection is not open.")
