import socket
import time
from random import randint
from threading import Thread, Event
import scapy.all as scapy


class Server:
    def __init__(self, tcp_port):
       
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
        self.CVIOLET2 = '\33[95m'

        self.network = 'eth1'

        self.looking_port = 13117
        self.tcp_port = tcp_port

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        self.ip = socket.gethostbyname(socket.gethostname())
        self.msg = 0xabcddcba.to_bytes(byteorder='big', length=4) + 0x2.to_bytes(byteorder='big',
                                                                                 length=1) + tcp_port.to_bytes(
            byteorder='big', length=2)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(("", tcp_port))

        self.client1 = None
        self.client1_name = None
        self.client2 = None
        self.client2_name = None

    #we broadcast offer packets on the UDP socket until we get two TCP connections from 2 clients
    def broadcast(self):
        while not (self.client1 is not None and self.client2 is not None):  #check if we get 2 clients
            self.udp_socket.sendto(self.msg, ('255.255.255.255', self.looking_port))
            time.sleep(1)


    #start listening on the servers TCP socket, the UDP socket will send broadcast offers and get clients
    def waiting_for_clients(self):
        print(self.YELLOW + "Server started, listening on IP address " + self.ip + self.CEND)
        self.tcp_socket.listen()
        broad = Thread(target=self.broadcast)
        broad.start()
        players_lst = []
        self.tcp_socket.listen(2)
        while not self.players_ready():
            if self.client1 is None:
                try:
                    self.client1, address = self.tcp_socket.accept()
                    if address is None:
                        print("issue with address")
                    self.client1_name = self.client1.recv(1024).decode('UTF-8')
                except:
                    self.client1 = None

            elif self.client2 is None:
                try:
                    self.client2, address = self.tcp_socket.accept()
                    if address is None:
                        print("issue with address")
                    self.client2_name = self.client2.recv(1024).decode('UTF-8')
                except:
                    self.client2 = None

        broad.join()


    #the server is waiting for answers of the clients
    def wait_for_answer(self, reset_event, client, res, times, i):
        current_time = time.time()
        client.setblocking(0)   #the socket is put in non-blocking mode. no timeout
        while not reset_event.is_set():
            try:
                res[i] = client.recv(1024).decode('UTF-8')
                if res[i] is None:
                    print("issue with res[i]")
            except socket.error as msg:
                if msg.errno == 10054: #an error that usually occurs when an existing connection is forcibly closed by the remote host
                    raise Exception("One of the clients has disconnected")
                else:
                    pass

            if time.time() > current_time + 10:
                reset_event.set()
            if res[i] != 767:
                if limit < 0:
                    print("issue with timing")
                times[i] = time.time() - current_time
                reset_event.set()


    def game_mode(self):
        num1 = randint(0, 9)
        num2 = randint(0, 9 - num1)
        sum_result = num1 + num2
        msg = self.CGREEN + "Welcome to Quick Maths!!\n" \
                          f"Player 1: {self.client1_name} \n" \
                          f"Player 2: {self.client2_name} \n==\n" \
                          "Please answer the following question as fast as you can:\n" \
                          f"How much is {num1} + {num2}?" + self.CEND
        try:
            self.client1.send(bytes(msg, 'UTF-8'))
            self.client2.send(bytes(msg, 'UTF-8'))
        except:
            raise Exception(self.CRED + "could not send to players the welcome message" + self.CEND)

        results = [999, 999]
        wins_count_T1 = 0
        wins_count_T2 = 0
        times = [10, 10]
        reset_event = Event()
        try:
            t1 = Thread(target=self.wait_for_answer, args=[reset_event, self.client1, results, times, 0])
            if t1 is None:
                print("issue threading Check doc")
            t2 = Thread(target=self.wait_for_answer, args=[reset_event, self.client2, results, times, 1])
            if t2 is None:
                print("issue threading Check doc")
            t1.start()
            t2.start()
        except Exception as e:
            print(e)

        while not reset_event.is_set():
            time.sleep(0.3)

        end_msg = self.CBEIGE + f"Game over!\nThe correct answer was {sum_result}!\n"

        if (results[0] == 999 and results[1] == 999):
            return end_msg + "No one responded"

        elif (times[0] < times[1]):
            if (results[0] == sum_result):
                return end_msg + f"Congratulations to the winner: {self.client1_name}" + self.CEND
            else:
                return end_msg + f"Congratulations to the winner: {self.client2_name}" + self.CEND

        elif (times[0] > times[1]):
            if (results[1] == sum_result):
                return end_msg + f"Congratulations to the winner: {self.client2_name}" + self.CEND
            else:
                return end_msg + f"Congratulations to the winner: {self.client1_name}" + self.CEND


    def start(self):
        while True:

            self.waiting_for_clients()
            print(
                self.BLUE + f"Received offer from {self.client1_name} and {self.client2_name}, attempting to connect..." + self.CEND)
            time.sleep(5)
            try:
                summary = self.game_mode()
                self.client1.send(bytes(summary, 'UTF-8'))
                self.client2.send(bytes(summary, 'UTF-8'))
                self.tcp_socket.close()
                print(self.CVIOLET2 + "Game over, sending out offer requests...\n" + self.CEND)

            except:
                print(self.CRED + "the game has been interrupted due to one of the clients disconnecting" + self.CEND)
                print(self.CRED + "Game over, sending out offer requests..." + self.CEND)
            self.__init__(self.tcp_port)


if __name__ == "__main__":
    server = Server(15000)
    server.start()

