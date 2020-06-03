import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import paho.mqtt.client as paho
mqttc = paho.Client()

host = "192.168.0.189"
topic = "velocity"
port = 1883

t = np.arange(0, 20, 1)
samps = []
x = []
y = []
z = []
tilt = []

def on_connect(self, mosq, obj, rc):
    print("Connected rc: " + str(rc))


def on_message(mosq, obj, msg):
	print("[Received] Topic: " + msg.topic + ", Message: " + str(msg.payload) + "\n")
	tilt.append(int(msg.payload))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed OK")


def on_unsubscribe(mosq, obj, mid, granted_qos):
    print("Unsubscribed OK")

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe
print("Connecting to " + host + "/" + topic)
mqttc.connect(host, port=1883, keepalive=60)
mqttc.subscribe(topic, 0)



# XBee setting
serdev = '/dev/ttyUSB0'
s = serial.Serial(serdev, 9600, timeout=3)

s.write("+++".encode())
char = s.read(2)
print("Enter AT mode.")
print(char.decode())

s.write("ATMY 0x123\r\n".encode())
char = s.read(3)
print("Set MY 0x123.")
print(char.decode())

s.write("ATDL 0x234\r\n".encode())
char = s.read(3)
print("Set DL 0x234.")
print(char.decode())

s.write("ATID 0x17\r\n".encode())
char = s.read(3)
print("Set PAN ID 0x17.")
print(char.decode())

s.write("ATWR\r\n".encode())
char = s.read(3)
print("Write config.")
print(char.decode())

s.write("ATMY\r\n".encode())
char = s.read(4)
print("MY :")
print(char.decode())

s.write("ATDL\r\n".encode())
char = s.read(4)
print("DL : ")
print(char.decode())

s.write("ATCN\r\n".encode())
char = s.read(3)
print("Exit AT mode.")
print(char.decode())

print("start sending RPC")
while len(samps) < 20:
	s.flushInput()
	s.write("/getData/run\r".encode())		// send rpc fucntion 
	char = s.read(3)						// read line on screen
	print(char.decode())
	if len(char) == 3:
		val = int(char)
		samps.append(val)
		for i in range(0, val):
			line = s.readline()
			print(line)
			sline = line.decode().split(",")	
			xval = float(sline[0])				// get velocity from line
			x.append(xval)
			print(mqttc.publish(topic, 0))		// publish MQTT
			mqttc.loop()

	time.sleep(1)



fig, ax = plt.subplots(2, 1)

ax[0].plot(t, samps)
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Number')

ax[1].plot(t, x[-20:], 'r', label="X")
ax[1].set_xlabel('Time')
ax[1].set_ylabel('Horizontal Velocity Vector')
ax[1].legend()


plt.show()


s.close()