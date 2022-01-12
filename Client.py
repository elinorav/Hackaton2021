import msvcrt
import socket
import time
import os

# System call
os.system("")

class Client:

    def __init__(self):

        self.CRED = '\033[91m'
        self.CBOLD = '\33[1m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.CGREEN = '\33[32m'
        self.CBLINK = '\33[5m'
        self.CREDBG = '\33[41m'
        self.CGREENBG = '\33[42m'
        self.CYELLOWBG = '\33[43m'
        self.CBLUEBG = '\33[44m'
        self.CEND = '\033[0m'
        self.CBEIGE  = '\33[36m'
        self.CVIOLET = '\33[35m'

        self.looking_port = 13117

        self.server_found = False
        self.tcp_port = None
        self.ip = None

        self.name = "Tom & Elinor"

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('', self.looking_port))

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.magic_cookie = 0xabcddcba
        self.offer_message_type = 0x2


    def looking_for_a_server(self):
        while True:
            verifaction_tcp, adress = self.udp_socket.recvfrom(1024)
            recieved_cookie = hex(int(verifaction_tcp.hex()[:8], 16))
            recieved_type = verifaction_tcp.hex()[9:10]
            recieved_port = verifaction_tcp.hex()[10:]

            if (recieved_cookie == hex(self.magic_cookie) and int(recieved_type) == self.offer_message_type):
                self.tcp_port = int(recieved_port, 16)
                if self.tcp_port == 17670:
                    self.ip = adress[0]
                    print(self.CVIOLET +"Recieved offer from " + str(self.ip) + ", attempting to connect...\n" + self.CEND)
                    break


    def connecting_to_a_server(self):
        try:
            self.tcp_socket.connect((self.ip, self.tcp_port))
        except:
            print(self.CRED + "Couldn't connect to server, listening for offer requests..."+ self.CEND)
            return False
        team_msg = bytes(self.name, 'UTF-8')
        try:
            self.tcp_socket.send(team_msg)
            welcome = self.tcp_socket.recv(1024)
            print(welcome.decode('UTF-8'))
            return True
        except:
            print(self.CRED + "Couldn't connect to server, listening for offer requests..." + self.CEND )
            return False


    def game_mode(self):
        while msvcrt.KBHit().kbhit():
            msvcrt.KBHit().getch()
        current = time.time()
        self.tcp_socket.setblocking(0)  #the socket is put in non-blocking mode. no timeout
        msg = None
        while not msvcrt.KBHit().kbhit():
            msg = self.expect_message()
            if msg:
                break
            #timeout in case the server has disconnected
            if current + 11 <= time.time():
                raise Exception("Server disconnected")

        if not msg:
            char = msvcrt.KBHit().getch()
            self.tcp_socket.send(char)
            while not msg:
                msg = self.expect_message()
                if current + 11 <= time.time():
                    raise Exception("Server disconnected")
        return msg


    def expect_message(self):
        msg = None
        try:
            msg = self.tcp_socket.recv(1024)
        except:
            time.sleep(0.1)
        return msg


    def start(self):
        print(self.BLUE + "Client started, listening for offer requests..." + self.CEND)
        while True:
            self.looking_for_a_server()
            if self.connecting_to_a_server():
                try:
                    msg = self.game_mode()
                except:
                    print(self.CRED + "Server disconnected duo to error, listening for offer requests..." + self.CEND)
                else:
                    print(self.BLUE + msg.decode('UTF-8') + self.CEND)
                    print(self.BLUE + "Server disconnected, listening for offer requests..." + self.CEND)
            self.__init__()




if __name__ == "__main__":
    client = Client()
    client.start()