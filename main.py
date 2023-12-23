import machine, time, requests, network, socket, wlan
from pimoroni import RGBLED, Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, rotate=0)
display.set_font("bitmap8")

ssid = wlan.ssid
password = wlan.password
ipAddress = ''
signal = ''
battery = ''

wlan = network.WLAN(network.STA_IF)

def connect():
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        #Check every second
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    global ipAddress
    ipAddress = ip
    global signal
    signal = wlan.status('rssi')
    
def signalStrength():
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        #Check every second
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    global ipAddress
    ipAddress = ip
    global signal
    signal = wlan.status('rssi')
    
def disconnect():
    wlan.disconnect()
    wlan.active(False)
    wlan.deinit()
    
def batteryLevel():
    Vsys = machine.ADC(29)
    conversion_factor = (3.3 / (65535)) * 3
    reading = Vsys.read_u16() * conversion_factor
    global battery
    battery = round(reading, 2)
    
def info(ip, signal):
    display.clear()
    pleaseWait()
    signalStrength()
    display.clear()
    clear()
    display.set_pen(WHITE)
    display.text('ip: ' + ip, 10, 10, 320, 4)
    display.text('signal: ', 10, 50, 320, 4)
    if signal > -90 and signal <= -70:
        display.set_pen(RED)
    elif signal > -70 and signal <= -60:
        display.set_pen(AMBER)
    elif signal > -60 and signal <= -50:
        display.set_pen(YELLOW)
    elif signal > -50 and signal <= -1:
        display.set_pen(GREEN)
    else:
        display.set_pen(WHITE)
    display.text(str(signal) + 'dBm', 150, 50, 320, 4)
    batteryLevel()
    display.set_pen(WHITE)
    display.text('battery: ' + str(battery) + 'v', 10, 90, 320, 4)
    display.update()
    time.sleep(5)
    clear()
    pleaseWait()
    refreshData()
    
def clear():
    display.set_pen(BLACK)
    display.clear()
    display.update()
    
def pleaseWait():
    display.set_pen(WHITE)
    display.text('Please wait...', 40, 100, 320, 4)
    display.update()
    display.set_pen(BLACK)
    
def backlight():
    #open backlight.config
    f = open('backlight.config', 'r')
    backlight = f.readline()
    f.close()
    return(backlight)

def writeBacklight(backlight):
    f = open('backlight.config', 'w')
    f.write(str(backlight))
    f.close

    
button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
GREY = display.create_pen(175, 175, 175)
GREEN = display.create_pen(51, 255, 50)
YELLOW = display.create_pen(255, 254, 0)
DARKYELLOW = display.create_pen(175, 175, 0)
AMBER = display.create_pen(254, 153, 0)
DARKAMBER = display.create_pen(175, 75, 0)
RED = display.create_pen(254, 0, 0)
DARKRED = display.create_pen(175, 0, 0)

WIDTH, HEIGHT = display.get_bounds()

bar_width = 10

backlight = float(backlight())
#backlight = 0.6

led = RGBLED(6, 7, 8)

pleaseWait()

try:
    connect()
except KeyboardInterrupt:
    machine.reset()

def refreshData():
    display.clear()
    pleaseWait()
    connect()
    display.clear()
    display.set_pen(BLACK)
    dataURL = "https://aurorawatch.lancs.ac.uk/api/0.1/activity.txt"
    headers = {'User-Agent': 'PicoPi-rora: Aurora Activity on Pico Display 2 (https://github.com/Boughen1975/PicoPi-rora)'}
    data = requests.post(dataURL, headers=headers)

#When loading data, set the LED to red

    display.set_backlight(backlight)

    led.set_rgb(1, 0, 0)

    #Draw control button icons
    #4 circle adjacent to buttons
    display.set_pen(GREY)
    display.circle(20, 60, 14)
    display.circle(20, 180, 14)
    display.circle(300, 60, 14)
    display.circle(300, 180, 14)
    
    display.set_pen(BLACK)
    display.circle(20, 60, 13)
    display.circle(20, 180, 13)
    display.circle(300, 60, 13)
    display.circle(300, 180, 13)
    
    display.set_pen(WHITE)
    display.circle(20, 60, 8)
    
    display.set_pen(BLACK)
    display.circle(20, 60, 5)
    display.rectangle(19, 52, 3, 17)
    
    display.set_pen(WHITE)
    display.line(14, 51, 19, 52)
    display.line(26, 69, 21, 68)
    
    display.set_pen(WHITE)
    display.rectangle(294, 59, 12, 3)
    display.rectangle(299, 54, 3, 12)
    display.rectangle(294, 179, 12, 3)
    display.triangle(294,80,300,160,306,80)
    display.circle(20, 173, 2)
    display.rectangle(18, 178, 4, 12)
    
    lines = data.text.split('\n')

    highest = 0
    for line in lines:
        if line.find("ACTIVITY") != -1:
            part = line.split()
            value = part[2]
            if float(value) > highest:
                highest = float(value)
                
    #Draw background lines to show where the yellow, amber and red levels start
    if highest > 50:
        display.set_pen(DARKYELLOW)
        yellowPixels = round((180 / highest) * 50)
        display.line(40, HEIGHT - yellowPixels - 30, 280, HEIGHT - yellowPixels - 30)
    if highest > 100:
        display.set_pen(DARKAMBER)
        amberPixels = round((180 / highest) * 100)
        display.line(40, HEIGHT - amberPixels - 30, 280, HEIGHT - amberPixels - 30)
    if highest > 200:
        display.set_pen(DARKRED)
        redPixels = round((180 / highest) * 200)
        display.line(40, HEIGHT - redPixels - 30, 280, HEIGHT - redPixels - 30)
        
    x = 40
    for line in lines:
        if line.find("ACTIVITY") != -1:
            part = line.split()
            value = part[2]
            if value != "nan":
                pixels = round((180 / highest) * float(value))
            colour = part[3]
            if colour == "green":
                display.set_pen(GREEN)
            elif colour == "yellow":
                display.set_pen(YELLOW)
            elif colour == "amber":
                display.set_pen(AMBER)
            elif colour == "red":
                display.set_pen(RED)
            else:
                display.set_pen(BLACK)
            display.rectangle(x + 4, HEIGHT - pixels - 30, bar_width - 8 , 210 - (HEIGHT - pixels - 30))

            x += bar_width

    led.set_rgb(0, 1, 0)

    display.update()
    display.set_pen(BLACK)
    disconnect()

refreshData()    
countdown = 300
while True:
    if button_a.read():
        refreshData()
    elif button_b.read():
        info(ipAddress, signal)
    elif button_x.read():
        if backlight < 0.9:
            backlight += 0.1
        display.set_backlight(backlight)
        writeBacklight(backlight)
    elif button_y.read():
        if backlight > 0.21:
            backlight -= 0.1
        display.set_backlight(backlight)
        writeBacklight(backlight)
    time.sleep(0.1)
    countdown = countdown - 0.1
    if countdown < 0.1:
        countdown = 300
        refreshData()
        

