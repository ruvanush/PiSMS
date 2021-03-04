#!/usr/bin/python

import serial
import time
import sys
import requests
import json
from smspdu.codecs import UCS2


class Modem(object):

    def __init__(self, number, webhook, interface):
        self.number = number
        self.webhook = webhook
        self.interface = interface

    def open(self):
        self.ser = serial.Serial(self.interface, 115200, timeout=5)
        self.send_command('AT\r'.encode())					# Modem check
        self.send_command('AT+CMGF=1\r'.encode()) 			# SMS in test mode
        self.ser.flush()

    def check_number(self):
        self.send_command('AT+CNUM\r'.encode())
        data = self.ser.readlines()
        print(data)
        exit(0)

    def send_command(self, command, getLine=True):
        self.ser.write(command)
        data = ''
        if getLine:
            data = self.read_line()
        return data

    def read_line(self):
        data = self.ser.read().decode()
        return data

    def get_all_unread_sms(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        command = 'AT+CMGL="REC UNREAD"\r\n'.encode()
        self.send_command(command, getLine=False)
        data = None
        data = self.ser.readlines()

        if(len(data) >= 5):
            data.pop(0)
            data.pop(len(data) - 1)
            data.pop(len(data) - 1)
            return[data[x:x+3] for x in range(0, len(data),3)]

    def close(self):
        self.ser.close()


def send_to_slack(sender, message: str, webhook: str):
    """
    used to send a message to a certain slack webhook
    :param message: content
    :param webhook: address of slack webhook
    """
    requests.post(webhook, json={'text': 'From: {} \n {}'.format(sender, message)})

def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        modems = []
        for modem in config['modems']:
            modems.append(Modem(modem['number'],
                                modem['webhook'],
                                modem['interface']))

    for modem in modems:
        modem.open()
        msg_list = modem.get_all_unread_sms()

        for msg in msg_list:
            info = msg[0].decode().split(',')
            number = info[2]
            sms = msg[1].decode()
            send_to_slack(number, sms, modem.webhook)




if __name__ == '__main__':
    main()