import serial

ser = serial.Serial("COM3", 115200)
while True:
    data_raw = ser.readline()
    data_split = data_raw.split(b' ')
    print(data_split)
    print(float(data_split[1]))
