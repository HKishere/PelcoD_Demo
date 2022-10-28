#!/usr/bin/python3
import serial #导入模块
import sys
import threading

def OnRecv(data):
    print(data.decode())

class Serial:
    m_port_name = ''
    m_boudrate = 9600
    m_timex=None
    m_ser = 0
    CallBack = None
    m_bconnect = False

    def SetCallBack(self, callbackfunc):
        self.CallBack = callbackfunc

    def OpenSerial(self, port_name, bps):
        self.m_port_name = port_name
        self.bps = bps
        try:
            self.m_ser = serial.Serial(port_name, bps,timeout=self.m_timex)
        except:
            print("串口打开失败!")
            self.m_bconnect = False
            self.m_ser = 0
            return False
        self.m_bconnect = True
        print("串口详情参数：", self.m_ser)
        return True

    def SendData(self, data):
        if self.m_bconnect:
            self.m_ser.write(data)

    def ThunFunc(self):
        while True:
            if self.m_bconnect == True:
                result = self.m_ser.read(100)
                if self.CallBack != None:
                    self.CallBack(result)

if __name__ == "__main__":
    client = Serial()
    client.OpenSerial("/dev/ttyTHS1", 9600)
    client.SetCallBack(OnRecv)

    client.SendData(("hello world").encode())
