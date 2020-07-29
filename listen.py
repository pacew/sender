#! /usr/bin/env python3

import socket
import struct
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

multicast_addr = "239.152.143.62"
multicast_port = 28077

mreq = struct.pack('=4sl', 
                   socket.inet_aton(multicast_addr), 
                   socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
sock.bind((multicast_addr, multicast_port))

last = time.time()
while True:
    msg_raw, raddr = sock.recvfrom(4096)
    msg = msg_raw.decode('utf-8')
    fields = []
    for elt in msg.split():
        fields.append("{:5d}".format(int(elt)))

    now = time.time()
    delta = now - last
    last = now

    print(f"{delta*1000:8.3f}", " ".join(fields))
