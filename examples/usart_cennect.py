import serial
import time
import threading

ser = serial.Serial()

def SerialOpen():
    ser.port="COM3" 
    ser.baudrate=115200
    ser.open()
    if(ser.isOpen):
        print("com open successfully")
    else:
        print("com open failed")

if __name__=='__main__':
    SerialOpen()
    while True:
        res = ser.readline().decode()
        print(res,end="")
        time.sleep(1)
