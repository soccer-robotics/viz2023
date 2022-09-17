import serial, time

# Set up commlink
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()

print("available ports:")
for port, desc, hwid in sorted(ports):
    print("{}: {} [{}]".format(port, desc, hwid))

# If there is more than one port, ask user to choose
if len(ports) > 1:
    port = input("select port> ")
    if port == "": port = sorted(ports)[0][0]
else:
    ports = []
    while len(ports) == 0:
        ports = serial.tools.list_ports.comports()
    port = ports[0][0]
print("establishing connection...")
time.sleep(1)
zircon = serial.Serial(port=port, baudrate=9600, timeout=.1)

def readline():
    data = zircon.readline().rstrip()
    r = data.decode('UTF-8').split()
    #print(r)
    return {"type":r[0], "info":list(map(float,r[1:]))}

def reconnect():
    global zircon
    try:
        zircon = serial.Serial(port=port, baudrate=9600, timeout=.1)
    except:
        pass