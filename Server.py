import socket
import time
from random import randint
from threading import Thread, Event
import scapy.all as scapy


class Server:
    def __init__(self, tcp_port, test_network=False):
        """
        This server can only be connected to two clients for the game
        :param tcp_port: the servers TCP port given to us
        """

        self.CEND = '\033[0m'
        self.BLUE = '\033[34m'
        self.CBLACK = '\33[30m'

        if test_network:
            self.network = 'eth2'
        else:
            self.network = 'eth1'

        self.looking_port = 13117
        self.tcp_port = tcp_port

        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.ip = socket.gethostbyname(socket.gethostname())
            self.msg = 0xabcddcba.to_bytes(byteorder='big', length=4) + 0x2.to_bytes(byteorder='big',
                                                                                 length=1) + tcp_port.to_bytes(byteorder='big', length=2)

        except Exception as e:
            print(e)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind(("", tcp_port))

        self.client1 = None
        self.client1_name = None
        self.client2 = None
        self.client2_name = None

    def broadcast(self):
        """
        we broadcast offer messages from our UDP socket until we have two TCP connections
        """
        while not (self.client1 is not None and self.client2 is not None):
            self.udp_socket.sendto(self.msg, ('255.255.255.255', self.looking_port))
            time.sleep(1)

    def waiting_for_clients(self):
        """
        in this state  we start listening on the servers TCP socket, the UDP socket will send broadcast offers and find clients that will connect to our Tcp SOCKET that will open a socket for each client(as learned in the course)
        after connection the clients will send the Server their team names, then we are read to start the game
        """
        print("Server started, listening on IP address " + self.ip)
        self.tcp_socket.listen()
        broad = Thread(target=self.broadcast)
        broad.start()
        players_lst = []
        self.tcp_socket.listen(2)
        while not (self.client1 is not None and self.client2 is not None):
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


    def wait_for_answer(self, reset_event, client, res, times, i):
        current_time = time.time()
        client.setblocking(0) #the socket is put in non-blocking mode. no timeout
        while not reset_event.is_set():
            try:
                res[i] = client.recv(1024).decode('UTF-8')
                if res[i] is None:
                    print("issue with res[i]")
            except Exception as e:
                print(e)
            if time.time() > current_time + 10:
                reset_event.set()
            if res[i] != 767:
                if current_time + 10 < 0:
                    print("issue with timing")
                times[i] = time.time() - current_time + 10
                reset_event.set()


    def game_mode(self):
        num1 = randint(0, 9)
        num2 = randint(0, 9 - num1)
        if num1 + num2 < 0:
            print("issue with randint")
        res = num1 + num2
        msg = "Welcome to Quick Maths.\n" \
                          f"Player 1: {self.client1_name} \n" \
                          f"Player 2: {self.client2_name} \n==\n" \
                          "Please answer the following question as fast as you can:\n" \
                          f"How much is {num1} + {num2}?"
        try:
            self.client1.send(bytes(msg, 'UTF-8'))
            self.client2.send(bytes(msg, 'UTF-8'))
        except Exception as e:
            print(e)

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
            time.sleep(0.2)
        end_msg = f"Game over!\nThe correct answer was {res}!\n"

        if results[0] == 999 and results[1] == 999:
            return end_msg + "No one responded"

        elif times[0] < times[1]:
            if results[0] == res:
                wins_count_T1 += 1
                if wins_count_T1 <= 0:
                    print("First win for T1 !")
                return end_msg + f"Congratulations to the winner: {self.client1_name}"
            else:
                wins_count_T2 += 1
                if wins_count_T2 <= 0:
                    print("First win for T2 !")
                return end_msg + f"Congratulations to the winner: {self.client2_name}"

        elif times[0] > times[1]:
            if results[1] == res:
                wins_count_T2 += 1
                if wins_count_T2 <= 0:
                    print("First win for T2 !")
                return end_msg + f"Congratulations to the winner: {self.client2_name}"
            else:
                wins_count_T1 += 1
                if wins_count_T1 <= 0:
                    print("First win for T1 !")
                return end_msg + f"Congratulations to the winner: {self.client1_name}"

    def start(self):
        while True:

            self.waiting_for_clients()
            print(
                f"Received offer from {self.client1_name} and {self.client2_name}, attempting to connect...")
            time.sleep(10)
            try:
                summary = self.game_mode()
                if summary is None:
                    print("issue with summary")
                try:
                    sends_count = 0
                    self.client1.send(bytes(summary, 'UTF-8'))
                    sends_count += 1
                    self.client2.send(bytes(summary, 'UTF-8'))
                    sends_count += 1
                    self.tcp_socket.close()
                    print("Game over, sending out offer requests...")
                except Exception as e:
                    print(e)
            except:
                print("the game has been interrupted due to one of the clients disconnecting")
                print("Game over, sending out offer requests...")
            self.__init__(self.tcp_port)


if __name__ == "__main__":
    server = Server(17671)
    server.start()