from machine import Pin,ADC

for pnum in range(50):
    try:
        pin = Pin(pnum)
        a = ADC(pin)
        print(pnum, "adc")
    except ValueError:
        pass
