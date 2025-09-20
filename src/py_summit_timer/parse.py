from crc import Calculator, Crc16, Configuration
from .protocol import Packet

CRC_CONFIG = Configuration(
    width=16,
    polynomial=0x8005,
    init_value=0x0000,
    final_xor_value=0x0000,
    reverse_input=True,
    reverse_output=True,
)
CRC_CALCULATOR = Calculator(CRC_CONFIG)

def validate_crc(data: str, crc: str) -> bool:
    """Validate the CRC format."""
    try:
        crc_int = int(crc, 16)
        return CRC_CALCULATOR.verify(data.encode(), crc_int)
    except ValueError:
        return False
    

def data_from_string(data: str) -> list[str] | None:
    """Strings follow the format:
    {data}CRC CR-LF
    """
    # Does the packet fit the format?
    if data.startswith("{"):
        end = data.find("}")
        if end != -1:
            content = data[1:end]
            crc = data[end + 1:]
            if validate_crc(content, crc.strip()) and "\t" in content:
                return content.split("\t")

    return None

def parse_packet(raw_packet: str) -> Packet | None:
    parts = data_from_string(raw_packet)
    if parts:
        return Packet.from_parts(parts)
    return None