import network
import socket
import time

# creds looks like: networks = { b'NETNAME': 'PASSWORD', ... }
import creds

from machine import ADC, Pin, deepsleep

pin0 = Pin(0, Pin.IN)
pin5 = Pin(5, Pin.OUT)


def led(val):
    if val:
        pin5.on()
    else:
        pin5.off()


led(True)

wifi = network.WLAN(network.STA_IF)


def do_connect():
    if not wifi.isconnected():
        print('scanning network...')
        wifi.active(True)
        nets = wifi.scan()
        for net in nets:
            net_name = net[0]
            password = creds.networks.get(net_name)
            if password is not None:
                print(net)
                print(password)
                wifi.connect(net_name, password)
                break
        while not wifi.isconnected():
            pass
    print('network config:', wifi.ifconfig())


class adc_chan:
    def __init__(self, pnum):
        self.pnum = pnum
        self.adc = ADC(Pin(pnum))
        self.adc.atten(ADC.ATTN_11DB)

    def read(self):
        return self.adc.read()


chans = []


for pnum in [32, 33, 34, 35, 36, 37, 38, 39]:
    chans.append(adc_chan(pnum))


multicast_addr = "239.152.143.62"
multicast_port = 28077


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pcount = 0
    while True:
        if pin0.value() == 0:
            led(False)
            deepsleep()

        led(False)
        pcount += 1
        if pcount > 50:
            pcount = 0
            led(True)

        vals = []
        vals.append(str(time.ticks_ms() & 0xffff))
        for chan in chans:
            vals.append(str(chan.read()))
        msg = " ".join(vals)
        try:
            sock.sendto(bytes(msg, 'utf-8'), (multicast_addr, multicast_port))
        except OSError:
            try:
                sock.close()
            except OSError:
                pass
            do_connect()

        time.sleep_ms(10)


do_connect()

print("sending data...")
main()
