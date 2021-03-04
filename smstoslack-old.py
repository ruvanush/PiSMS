#!/usr/bin/python

import serial
import time
import sys
import requests
from smspdu.codecs import UCS2


class PiModem(object):

    def __init__(self):
        self.open()

    def open(self):
        # ttyS0 is Serial Interface of the Pi Zero
        self.ser = serial.Serial('/dev/ttyS0', 115200, timeout=5)
        self.SendCommand('AT\r'.encode())							# Modem check
        self.SendCommand('AT+CMGF=1\r'.encode())                    # SMS in testmoe
        self.ser.flush()

    def SendCommand(self, command, getLine=True):
        self.ser.write(command)
        data = ''
        if getLine:
            data = self.ReadLine()
        return data

    def ReadLine(self):
        data = self.ser.read().decode()
        #print (data)
        return data

    def getAllUnreadSMS(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        command = 'AT+CMGL="REC UNREAD"\r\n'.encode()
        self.SendCommand(command, getLine=False)
        data = self.ser.readlines()
        print (data)
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

def main():
    pm = PiModem()

    try:
        #print (url)
        while True:
            smsText = ""
            smsText = pm.getAllUnreadSMS()
            if smsText != None:
                #requests.post(url, json={"text": smsText})
                print (smsText)
            time.sleep(1)


    except KeyboardInterrupt:
        pm.close()

if __name__ == '__main__':
    main()