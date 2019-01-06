from enum import IntEnum

encoding = 'ISO-8859-1'
byte_order = 'big'

class SystemCommand(IntEnum):
    """Top-Level Command values, encoded in the CAN-ID"""
    SYSTEM = 0x00
    LOCO_DISCOVERY = 0x01
    MFX_BIND = 0x02
    MFX_VERIFY = 0x03
    LOCO_SPEED = 0x04
    LOCO_DIRECTION = 0x05
    LOCO_FUNCTION = 0x06
    READ_CONFIG = 0x07
    WRITE_CONFIG = 0x08
    ACCESSORY_SWITCH = 0x0B
    ACCESSORY_CONFIG = 0x0C
    S88_POLL = 0x10
    S88_EVENT = 0x11
    SX1_EVENT = 0x12
    PING = 0x18
    OFFER_UPDATE = 0x19
    READ_CONFIG_DATA = 0x1A
    BOOTLOADER_CAN_SERVICE = 0x1B
    BOOTLOADER_RAIL_SERVICE = 0x1C
    STATUSDATA_CONFIGURATION = 0x1D
    CONFIG_DATA_QUERY = 0x20
    CONFIG_DATA_STREAM = 0x21
    CONNECT_DATA_STREAM = 0x20


class SystemSubCommand(IntEnum):
    """Subcommand values for the SystemCommand.SYSTEM command. Encoded in the payload."""
    SYSTEM_STOP = 0x00
    SYSTEM_GO = 0x01
    SYSTEM_HALT = 0x02
    LOCO_EMERGENCY_STOP = 0x03
    LOCO_CYCLE_STOP = 0x04
    LOCO_DATAPROTOCOL = 0x05
    ACCESSORY_SWITCH_TIME = 0x06
    MFX_FAST_READ = 0x07
    ENABLE_RAIL_PROTOCOL = 0x08
    SYSTEM_SET_MFX_REGISTRATION_COUNTER = 0x09
    SYSTEM_OVERLOAD = 0x0A
    SYSTEM_STATUS = 0x0B
    SYSTEM_IDENTIFIER = 0x0C
    MFX_SEEK = 0x30
    SYSTEM_RESET = 0x80


def decompose_marklin_identifier(identifier_bytes):
    identifier = int.from_bytes(identifier_bytes, byte_order)

    hash_value = identifier & 0xFFFF
    response = (identifier & 0x010000 != 0)
    command = identifier >> 17
    command = command & 0xFF

    return SystemCommand(command), response, hash_value


class Message(object):

    def __init__(self):
        self.command = SystemCommand.SYSTEM
        self.response = False
        self.hash = 0
        self.dlc = 0
        self.data = bytes(0)

    @classmethod
    def make_message(cls, command, response, hash=0):
        """

        :param command: 8-bit command value
        :param response: 1-bit (boolean) response flag
        :return:
        """
        obj = cls()
        obj.command = command
        obj.response = response
        obj.hash = hash
        return obj

    @classmethod
    def from_bytes(cls, messageBytes):
        obj = cls()

        identifier = messageBytes[0:4]
        obj.dlc = messageBytes[4]
        obj.data = messageBytes[5:5 + obj.dlc]

        obj.command, obj.response, obj.hash = decompose_marklin_identifier(identifier)
        return obj

    def __make_message_header(self):
        """

        :return: a 4-byte byte array containing the header. Priority is always set to 0.
        """

        result = int(self.command) << 17
        if self.response:
            result = result | 0x100

        result = result | self.hash
        return result.to_bytes(4, byte_order)

    def to_bytes(self):
        """Serialize this message to a 13-byte byte array.
        """
        result = bytearray()
        result.extend(self.__make_message_header())
        result.append(self.dlc)
        result.extend(self.data)

        # extend to 13 bytes with 0-bytes

        result.extend([0] * (13 - len(result)))

        return result

    def __str__(self):
        text = "Command: {0:24s}, Response: {1:5s}, Hash: {2:6s}, DLC: {3}, Data: '{4}'".format(self.command.name,
                                                                                                str(self.response),
                                                                                                hex(self.hash),
                                                                                                self.dlc,
                                                                                                self.data.hex())

        if self.command in [SystemCommand.CONFIG_DATA_QUERY, SystemCommand.CONFIG_DATA_STREAM]:
            plaintext = ' ("{0}")'.format(self.data.decode(encoding))
            plaintext = plaintext.replace("\n", "\\n")
            text += plaintext

        return text

    def set_payload(self, data):
        data = bytes(data)
        self.dlc = len(data)
        self.data = data

    def get_payload(self):
        return self.data
