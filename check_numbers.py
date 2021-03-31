from time import sleep

import json
import serial

def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)


        found_numbers = []
        configured_numbers = []
        for entry in config['numbers']:
            configured_numbers.append(entry['number'])

        interface_mapping = {}
        for interface in config['modems']:
            interface_mapping[interface] = None
            for i in range(4):
                try:
                    ser = serial.Serial(interface, 115200, timeout=5)
                    ser.write('AT\r'.encode())
                    ser.write('AT+CMGF=1\r'.encode())
                    ser.write('AT+CNUM\r'.encode())
                    data = ser.readlines()
                    number = data[5].decode().split(',')[1].replace('"', '')
                    found_numbers.append(number)
                    interface_mapping[interface] = number
                    break
                except Exception:
                    sleep(10)

    not_found_numbers = list(set(configured_numbers) - set(found_numbers))

    if len(not_found_numbers) >= 1 :
        print('2 Configured_Numbers - CRITICAL: Number/s not found: {}'.format(
            not_found_numbers
        ))
    else:
        print('0 Configured_Numbers - OK: all configured Numbers found')

    for interface in interface_mapping.keys():
        if interface_mapping[interface] is None:
            print('2 {} - CRITICAL: no modem found on this port'.format(
                interface
            ))
        else:
            print('0 {} - OK: modem has Number: {}'.format(
                interface, interface_mapping[interface]
            ))


if __name__ == '__main__':
    main()