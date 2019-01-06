import sys
from optparse import OptionParser
import socket
import select
import MarklinCAN.System, MarklinCAN.Message
import threading

bufferSize = 1024


def parse_args(args):
    parser = OptionParser()

    parser.add_option("--cs2-ip", type=str, default="192.168.178.36")
    parser.add_option("--cs2-port", type=int, default=15731)
    parser.add_option("--broadcast-ip", type="str", default="")
    parser.add_option("--broadcast-port", type=int, default=15730)

    return parser.parse_args(args)


class ReceiveThread(threading.Thread):

    def __init__(self, sock, mm_system):
        super(ReceiveThread, self).__init__(target=ReceiveThread.loop, name="Receiver Thread", args=[self])
        self.sock = sock
        self.mm_system = mm_system
        self.do_run = True  # Not synchronized, cannot be truly triggered from the outside. Bad!

    def loop(self):
        while self.do_run:
            active_sockets = select.select([self.sock], [], [])
            input_msg = active_sockets[0][0].recv(bufferSize)
            input_msg = MarklinCAN.Message.Message.from_bytes(input_msg)
            self.mm_system.process_message(input_msg)


def user_io_loop(sock, mm_system, sendto_address):
    while True:
        offset = input("Offset? ")
        count = 2 # input("Count? (MS2 always returns 2)")

        #output_message = mm_system.make_message(MarklinCAN.Message.SystemCommand.ACCESSORY_SWITCH, False)
        #output_message.set_payload(bytes([0x00, 0x00, 0x30, 0x00, 0x00, 0x01]))


        # output_message = mm_system.make_message(MarklinCAN.Message.SystemCommand.CONFIG_DATA_QUERY, False)
        # output_message.set_payload(bytes("loknamen", MarklinCAN.Message.encoding))
        #
        # output_message_bytes = output_message.to_bytes()
        # print("Sending Message to {1}:{2}: {0} ".format(output_message, sendto_address[0], sendto_address[1]))
        # sock.sendto(output_message_bytes, sendto_address)
        #
        # output_message = mm_system.make_message(MarklinCAN.Message.SystemCommand.CONFIG_DATA_QUERY, False)
        # output_message.set_payload(bytes("{0} {1}".format(offset, count), MarklinCAN.Message.encoding))
        #
        # output_message_bytes = output_message.to_bytes()
        # print("Sending Message to {1}:{2}: {0} ".format(output_message, sendto_address[0], sendto_address[1]))
        # sock.sendto(output_message_bytes, sendto_address)




        output_message = mm_system.make_message(MarklinCAN.Message.SystemCommand.CONFIG_DATA_QUERY, False)
        output_message.set_payload(bytes("lokinfo\0", MarklinCAN.Message.encoding))
        # file name must be an 8-byte payload, padded with 0-bytes if necessary

        output_message_bytes = output_message.to_bytes()
        print("Sending Message to {1}:{2}: {0} ".format(output_message, sendto_address[0], sendto_address[1]))
        sock.sendto(output_message_bytes, sendto_address)

        output_message = mm_system.make_message(MarklinCAN.Message.SystemCommand.CONFIG_DATA_QUERY, False)
        output_message.set_payload(bytes("ET 515\0\0".format(offset, count), MarklinCAN.Message.encoding))

        output_message_bytes = output_message.to_bytes()
        print("Sending Message to {1}:{2}: {0} ".format(output_message, sendto_address[0], sendto_address[1]))
        sock.sendto(output_message_bytes, sendto_address)

        output_message = mm_system.make_message(MarklinCAN.Message.SystemCommand.CONFIG_DATA_QUERY, False)
        output_message.set_payload(bytes("\0\0\0\0\0\0\0\0".format(offset, count), MarklinCAN.Message.encoding))
        # We always need to send the loco name in two zero-padded packets.

        output_message_bytes = output_message.to_bytes()
        print("Sending Message to {1}:{2}: {0} ".format(output_message, sendto_address[0], sendto_address[1]))
        sock.sendto(output_message_bytes, sendto_address)


def main(args):
    options, args = parse_args(args)

    print("Listening for Broadcasts on '{0}:{1}'".format(options.broadcast_ip, options.broadcast_port))
    print("Sending unicast to '{0}:{1}'".format(options.cs2_ip, options.cs2_port))

    mm_system = MarklinCAN.System.System(15)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((options.broadcast_ip, options.broadcast_port))

    receive_thread = ReceiveThread(s, mm_system)
    receive_thread.start()

    sendto_address = (options.cs2_ip, options.cs2_port)
    user_io_loop(s, mm_system, sendto_address)

    receive_thread.do_run = False
    receive_thread.join()
    s.close()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
