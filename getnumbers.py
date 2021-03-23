import json
import serial

def main():
    with open('config.json', 'r') as config:
        interfaces = json.load(config)['modems']
        for interface in interfaces:
            try:
                ser = serial.Serial(interface, 115200, timeout=5)
                ser.write('AT\r'.encode())
                ser.write('AT+CMGF=1\r'.encode())
                ser.write('AT+CNUM\r'.encode())
                data = ser.readlines()
                print(data)
                number = data[5].decode().split(',')[1].replace('"', '')
                print('{}: {}'.format(interface, number))
            except Exception:
                print('{} unavailable'.format(interface))


if __name__ == '__main__':
    main()