all:

upload:
	ampy --port /dev/ttyUSB0 put boot.py
	ampy --port /dev/ttyUSB0 put creds.py

reset:
	ampy --port /dev/ttyUSB0 reset

erase-flash:
	esptool.py --port /dev/ttyUSB0 erase_flash

flash-python:
	esptool.py --port /dev/ttyUSB0 --chip esp32 write_flash -z 0x1000 esp32-idf3-20191220-v1.12.bin
