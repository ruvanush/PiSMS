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
        # ttyS0 is Serial Interface of the Pi Zero
        self.ser = serial.Serial('/dev/ttyS0', 115200, timeout=5)
        self.send_command('AT\r'.encode())							# Modem check
        self.send_command('AT+CMGF=1\r'.encode()) 					# SMS in testmoe

    def check_number(self):
        pass

    def send_command(self, command, getLine=True):
        self.ser.write(command)
        data = ''
        if getLine:
            data = self.read_line()
        return data

    def read_line(self):
        data = self.ser.read().decode()
        #print (data)
        return data

    def get_all_unread_sms(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        command = 'AT+CMGL="REC UNREAD"\r\n'.encode()
        self.send_command(command, getLine=False)
        data = self.ser.readlines()
        #print (len(data))
        if len(data) > 4:
            #print (data[2])
            #print (data[2].decode("ISO-8859-1"))
            try:
                # try to decode UCS2
                return UCS2.decode(str(ord(c) for c in data[2].decode("ISO-8859-1")))
            except:
                return str(data[2].decode("ISO-8859-1"))  # use plain text
            # return UCS2.decode(data[2])

    def close(self):
        self.ser.close()


def send_to_slack(text: str, webhook: str):
    """
    used to send text to certain slack webhook
    :param text: content
    :param webhook: address of slack webhook
    """
    requests.post(webhook, json={'text': text})

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



    #try:
    #    file = open('smstoslack.config', 'r')
    #    url: str = file.readline()
    #    while True:
    #        text: str = modem.get_all_unread_sms()
    #        if text != None:
    #            send_to_slack(text, url)

    #except KeyboardInterrupt:
    #    modem.close()


if __name__ == '__main__':
    main()