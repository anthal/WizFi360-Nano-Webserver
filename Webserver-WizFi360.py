#
import network
from secrets import secrets
import time
from machine import Pin
import uasyncio as asyncio

# Load login data from different file for safety reasons
ssid = secrets['ssid']
key = secrets['key']


# Function to load in html page
def get_html(html_name):
    with open(html_name, 'r') as file:
        html = file.read()
    return html


led0 = machine.Pin(25, machine.Pin.OUT)
led0.value(0)
# led = Pin(15, Pin.OUT)
# onboard_led = Pin("LED", Pin.OUT, value=0)
stateis = "LED is unknown"

html = get_html('index.html')

wlan = network.WLAN(network.STA)
wlan.active(True)
retval = wlan.connect(ssid, key)
# print(retval)

# Wait for connect or fail
max_wait = 10
print("Waiting to connect")
while max_wait > 0:
    if wlan.isconnected():
        # and wlan.status() < 0:
        break
    max_wait -= 1
    print(".", end='')
    time.sleep(1)

if wlan.isconnected():
    print("WLAN Connected")
    print(wlan.ifconfig())

    retval = wlan.tcp_server(80)
    if retval: 
        print("Server Ready, wait of Client ...")
    while retval:
        linkID, s, request_line = wlan.ReceiveData()
        # print(linkID, s)
        if linkID is not None and request_line:
            request = str(request_line)
            print("request_line: {}".format(request_line))            
            led_on1 = request.find('/led1/on')
            led_off1 = request.find('/led1/off')
            print( 'led_on1 : {}'.format(led_on1))
            print( 'led_off1: {}'.format(led_off1))

            stateis1 = ""
            if led_on1 >= 4:
                print("led 1 on")
                led0.value(1)
                stateis1 = "ON"

            if led_off1 >= 4:
                print("led 2 off")
                led0.value(0)
                stateis1 = "OFF"
                
            wlan.send_data(linkID, html % (stateis1))
            # Wait of 'SEND OK':
            wlan.wait_ack('SEND OK')
            # End the TCP Connection:
            wlan.tcp_close(linkID)
else:
    print("No WLAN Connection!")
