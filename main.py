import network
import socket
from machine import Pin, PWM, I2C
import time
import ssd1306


SSID = "YOUR_WIFI_NAME" #Currentlty in station mode, not acccess point
PASSWORD = "YOUR_WIFI_PASSWORD"


esc = PWM(Pin(10), freq=50)

def set_esc_pulse(us):
    duty = int(us * 1023 / 20000)
    esc.duty(duty)


i2c = I2C(0, scl=Pin(6), sda=Pin(5), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
x_offset = 30
y_offset = 30

def update_oled(power_percent):
    oled.fill(0)
    oled.text("Power Level:", x_offset, y_offset)
    oled.text("{}%".format(power_percent), x_offset + 10, y_offset + 12)
    oled.show()


def calibrate_esc():
   
    set_esc_pulse(2000)
    time.sleep(2)
    set_esc_pulse(1000)
    time.sleep(2)
  

def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="ESP32-ESC", password="12345678")
    while not ap.active():
        pass
    print("Access Point started:", ap.ifconfig())
    return ap.ifconfig()[0]


def start_server():
    with open("esc_web.html", "r") as f:
        html = f.read()

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Web server listening on http://%s:80" % ip)

    while True:
        cl, addr = s.accept()
        print("Client connected:", addr)
        request = cl.recv(1024).decode()
        print("Request:", request)

       
        if "/?speed=" in request:
            try:
                idx = request.find("/?speed=")
                value = int(request[idx+8:].split(" ")[0])
                pulse = 1000 + (value * 10)  
                print("Setting speed to", value, "% →", pulse, "us")
                set_esc_pulse(pulse)
                update_oled(value)
            except Exception as e:
                print("Error:", e)

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()

set_esc_pulse(1000)      
calibrate_esc()          
update_oled(0)         
ip = start_ap()         
start_server()          

