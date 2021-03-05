#!/usr/bin/python
import serial
import time
import sys
import requests
import json
from smspdu.codecs import UCS2


class Modem(object):

    def __init__(self, interface):
        self.interface = interface
        self.number = self.get_number()
        self.webhook = self.get_webhook()

    def open(self):
        self.ser = serial.Serial(self.interface, 115200, timeout=5)
        self.send_command('AT\r'.encode())					# Modem check
        data = self.ser.readlines()
        if 'OK' not in data[1].decode():
            self.close()
            raise Exception('No Modem on {}'.format(self.interface))
        self.send_command('AT+CMGF=1\r'.encode()) 			# SMS in test mode
        self.ser.flush()

    def get_number(self):
        self.open()
        self.send_command('AT+CNUM\r'.encode())
        data = self.ser.readlines()
        self.ser.flush()
        self.close()
        return data[3].decode().split(',')[1].replace('"', '')

    def get_webhook(self):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            for number in config['numbers']:
                if number['number'] == self.number:
                    return number['webhook']
            raise Exception('no config found for {}'.format(self.number))

    def send_command(self, command, getLine=True):
        self.ser.write(command)
        data = ''
        if getLine:
            data = self.read_line()
        return data

    def read_line(self):
        data = self.ser.read().decode()
        return data

    def get_all_sms(self):
        self.open()
        self.ser.flushInput()
        self.ser.flushOutput()

        command = 'AT+CMGL="ALL"\r\n'.encode()
        self.send_command(command, getLine=False)
        data = self.ser.readlines()
        self.close()
        if len(data) >= 5:
            data.pop(0)
            data.pop(len(data) - 1)
            data.pop(len(data) - 1)
            value = [data[x:x+3] for x in range(0, len(data),3)]
            return value
        return []

    def delete_sms(self, sms_index):
        self.open()
        self.send_command('AT+CMGD={}\r'.format(sms_index).encode())
        self.close()


    def close(self):
        self.ser.close()

    def send_to_slack(self, sender, message):
        """
        used to send a message to slack via webhook
        :param sender: the sender of the message
        :param message: the contetnt of the message
        """
        requests.post(self.webhook,
                      json={'text': 'From {}: \n {}'.format(sender, message)})

def decode_msg(msg):
    try:
        # try to decode UCS2
        return UCS2.decode(str(ord(c) for c in msg.decode("ISO-8859-1")))
    except:
        return str(msg.decode("ISO-8859-1"))  # use plain text


def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        modems = []
        for interface in config['modems']:
            try:
                modems.append(Modem(interface))
            except Exception as exp:
                print('failed: {}'.format(exp))


    for modem in modems:
        try:
            msg_list = modem.get_all_sms()

            for msg in msg_list:
                info = msg[0].decode().split(',')
                sms_index = info[0].replace('+CMGL: ', '')
                sender_number = info[2]
                # todo make apple readable
                sms_msg = decode_msg(msg[1])
                try:
                    modem.send_to_slack(sender_number, sms_msg)
                    #print('{}: {}'.format(sender_number, sms_msg))
                    modem.delete_sms(sms_index)
                except Exception as exp:
                    print('send Failed: {}'.format(exp))

        except Exception as exp:
            print('fetching msg failed: {}'.format(exp))


if __name__ == '__main__':
    main()