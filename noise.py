#! /usr/bin/env python3

import socket
import struct
import math
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


class chan:
    def __init__(self):
        self.raw = 0
        self.raw_smoothed = 0
        self.hist = [0] * 100
        self.hist_idx = 0
        self.sd = 0

    def new_val(self, raw):
        self.raw = raw
        factor = .99
        self.raw_smoothed = self.raw_smoothed * factor + raw * (1-factor)

        supply = 3.3
        v = (raw / 4096.0) * math.exp(1.1)
        self.voltage = v
        r1 = 1000
        r2 = 10 * 1000

        R = (v * r1) / (supply - v)

        self.val = R / r2 * 100
        self.val = min(self.val, 99.9)
        self.val = max(self.val, 0)

        self.hist[self.hist_idx] = self.val
        self.hist_idx += 1
        if self.hist_idx == len(self.hist):
            n = len(self.hist)
            sum = 0
            sumsq = 0
            for i in range(n):
                x = self.hist[i]
                sum += x
                sumsq += x * x
            var = (sumsq - sum*sum/n) / (n-1)
            self.sd = math.sqrt(var)
            self.hist_idx = 0


chans = [chan(), chan(), chan(), chan()]

last_ts = None
start = time.time()
while True:
    msg_raw, raddr = sock.recvfrom(4096)
    msg = msg_raw.decode('utf-8').split()
    ts = int(msg[0])
    if last_ts is None:
        last_ts = ts
        continue
    dt = ((ts - last_ts) & 0xffff) / 1000.0

    out = ""
    for cnum in range(4):
        chan = chans[cnum]
        chan.new_val(int(msg[cnum+1]))
        
    runtime = time.time() - start
    
    for c in chans:
        print(f"{c.raw:5d}", end=' ')
    print()


