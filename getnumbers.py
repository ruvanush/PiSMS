import json
import serial


with open('config.json', 'r') as config:
    interfaces = json.load(config)['modems']
    for interface in interfaces:
        ser = serial.Serial(interface, 115200, timeout=5)
        ser.write('AT\r'.encode())
        ser.write('AT+CMGF=1\r'.encode())
        ser.flush()
        ser.write('AT+CNUM\r'.encode())
        data = ser.readlines()
        print(data[3].decode().split(',')[1].replace('"', ''))