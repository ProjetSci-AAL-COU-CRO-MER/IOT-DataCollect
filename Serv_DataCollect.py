import time
import argparse
import signal
import sys
import socket
import socketserver
import threading
import serial
import pymongo
import json
import time
import paho.mqtt.client as mqtt


# binding information
HOST           = "0.0.0.0"
UDP_PORT       = 10000
FILENAME        = "values.txt"
LAST_VALUE      = ""
SERV_BDD_PHY    = ""
SERV_DASH       = ""
PORT            = 1883
IP_MQTT         = "10.0.2.5"

# Listen serial interface
SERIALPORT = "/dev/ttyACM0"
BAUDRATE = 115200
ser = serial.Serial()

def handle():        
        # ser = serial.Serial(SERIALPORT, BAUDRATE)
        ser.port=SERIALPORT
        ser.baudrate=BAUDRATE
        ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        ser.parity = serial.PARITY_NONE #set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        ser.timeout = None          #block read

        # ser.timeout = 0             #non-block read
        # ser.timeout = 2              #timeout block read
        ser.xonxoff = False     #disable software flow control
        ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        ser.writeTimeout = 0     #timeout for write
        print ('Starting Up Serial Monitor')
        try:
                ser.open()
        except serial.SerialException:
                print("Serial {} port not available".format(SERIALPORT))
                exit()

#send UDP data
def sendUDP():
    byte_message = bytes("data", "utf-8")
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    opened_socket.sendto(byte_message, (SERV_BDD_PHY, UDP_PORT))

# send MQTT Data
# Callback Function on Connection with MQTT Server
def on_connect( client, userdata, flags, rc):
    print ("Connected with Code :" +str(rc))

# Callback Function on Receiving the Subscribed Topic/Message
def on_message( client, userdata, msg):
    # print the message received from the subscribed topic
    print ( str(msg.payload) )
 

if __name__ == '__main__':
        handle()
        print ('Press Ctrl-C to quit.')
        sendUDP()
        #server = ThreadedUDPServer((HOST, UDP_PORT), ThreadedUDPRequestHandler)
        #server_thread = threading.Thread(target=server.serve_forever)
        #server_thread.daemon = True
        
        #Communication via mqtt
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        # client.username_pw_set("login", "mdp")
        client.connect(IP_MQTT, PORT, 60)
        client.loop_start()
        try:
                while ser.isOpen() : 
                        time.sleep(2)
                        if (ser.inWaiting() > 0): # if incoming bytes are waiting 
                                data_str = ser.read(ser.inWaiting()).decode("utf-8")
                                print (data_str)
                                client.publish("sensors",data_str)
                                print ("Message envoyé")

        except (KeyboardInterrupt, SystemExit):
                server.shutdown()
                server.server_close()
                ser.close()
                client.loop_stop()
                client.disconnect()
                exit()
