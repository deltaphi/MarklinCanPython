from .Message import Message

class Accessory(object):
    def __init__(self, address):
        self.address = address
        self.power = None
        self.direction = None

    def print(self, indent=""):
        print("{0}Accessory {1}: Power {2}, Direction {2}".format(indent, self.address, self.power, self.direction))

class System(object):
    marklinPrivateBaseUUID = 0x00001800

    def __init__(self, id_offset):
        self.systemStatus = None
        self.uuid = self.marklinPrivateBaseUUID + id_offset
        self.hash = self._get_hash()
        self.locos = {}
        self.accessories = {}

    def __maskUUID(self):
        highpart = self.uuid
        highpart = highpart >> 3
        highpart = highpart & 0xFFFFFF00

        lowpart = self.uuid
        lowpart = lowpart & 0x7F

        result = highpart | lowpart

        return result

    def _get_hash(self):
        marklinuid = self.__maskUUID()
        lowbytes = marklinuid & 0xFFFF
        highbytes = (marklinuid >> 16)
        hashvalue = lowbytes ^ highbytes

        return hashvalue

    def process_message(self, marklin_message):
        """

        :param marklin_message: A MarklinCAN.Message.Message object
        :return:
        """
        print("Received Message: {0}".format(marklin_message))

    def make_message(self, command, response):
        return Message.make_message(command, response, self.hash)

    def print(self, indent=""):
        print("{0}MarklinCAN.System (UUID {1}) Information:".format(indent, self.uuid))
        indent = indent + "  "
        print("{0}Rail Power: {1}".format(indent, self.systemStatus))
        for accessory in self.accessories:
            accessory.print(indent)
        for loco in self.locos:
            loco.print(indent)

