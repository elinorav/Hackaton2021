import selectors
import socket
import types
from time import sleep
from threading import Thread
import time
from Hackaton2021.config import *
import random

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )


sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('Server started, listening on IP address ', host)
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

team_map ={'group 1': [],'group 2': []}
group1_ips = []
group2_ips = []
couter_group1 = 0
couter_group2 = 0

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def client_to_team(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024).decode("utf-8")  # Should be ready to read
        if recv_data:
            if(len(team_map.get('group 1'))< len(team_map.get('group 1'))):
                team_map['group 1'].append((recv_data,key,mask))
                group1_ips.append(data.addr[0])
            elif (len(team_map.get('group 1'))>len(team_map.get('group 1'))):
                team_map['group 2'].append((recv_data,key,mask))
                group2_ips.append(data.addr[0])
            else:
                group, arr = random.choice(list(team_map.items()))
                team_map[group].append((recv_data, key, mask))
                print(group)
                if group == 'group 1':
                    group1_ips.append(data.addr[0])
                else:
                    group2_ips.append(data.addr[0])
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()

def send_start_game(key, mask,group1, group2):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        data.outb += """Welcome to Keyboard Spamming Battle Royale.
                        Group 1:
                        ==
                        {}
                        Group 2:
                        ==
                        {}
                        Start pressing keys on your keyboard as fast as you can!!""".format(group1,group2)\
                        .encode('ascii')
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def service_connection(key, mask):
    global couter_group1
    global couter_group2
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print(data.addr[0])
            if(data.addr[0] in group1_ips):
                print(couter_group1)
                couter_group1 =couter_group1+1
                print(couter_group1)
            elif (data.addr[0] in group2_ips):
                print(couter_group2)
                couter_group2 =couter_group2+1
                print(couter_group2)
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]



def send_udp_invaite():
    msg = b'hello hello hello'
    t_end = time.time() + 10
    while time.time() < t_end:
        for ip in ip_range_list:
            # print(f'sending on {ip}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # sock.bind((ip,0))
            sock.sendto(msg, (ip, port))
            sock.close()
    logging.debug("end send invaite")





def main():

    t1 = Thread(name='udp', target=send_udp_invaite)
    t1.setDaemon(True)
    t1.start()
    t_end = time.time() + 10
    while time.time() < t_end:
        # print("try to get conection")
        events = sel.select(timeout=(t_end-time.time()))
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                client_to_team(key, mask)
    t1.join()
    print(group1_ips)
    print(group2_ips)

    group1 = '\n'.join([i[0] for i in team_map.get('group 1')])
    group2 = '\n'.join([i[0] for i in team_map.get('group 2')])
    for client in team_map.get('group 1'):
        send_start_game(client[1],client[2],group1,group2)
    for client in team_map.get('group 2'):
        send_start_game(client[1],client[2],group1,group2)


    t_end = time.time() + 10
    while time.time() < t_end:
        # print("try to get conection")
        events = sel.select(timeout=(t_end-time.time()))
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)

    print('group1: ',couter_group1)
    print('group2: ', couter_group2)

    print("endddd")

main()