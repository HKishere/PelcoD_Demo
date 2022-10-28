#!/usr/bin/python3
import imp
import sys
import threading
import TCP_Client as tcp
import Serial as ser

PelcoDHead = 0xFF

HEAD_GO_LEFT    = 0x0004
HEAD_GO_RIGHT   = 0x0002
HEAD_GO_UP      = 0x0008
HEAD_GO_DOWN    = 0x0010

HEAD_GO_DOWN_LEFT = HEAD_GO_DOWN + HEAD_GO_LEFT
HEAD_GO_DOWN_RIGHT = HEAD_GO_DOWN + HEAD_GO_RIGHT
HEAD_GO_UP_LEFT = HEAD_GO_UP + HEAD_GO_LEFT
HEAD_GO_UP_RIGHT = HEAD_GO_UP + HEAD_GO_RIGHT

ZOOM_IN         = 0x0020
ZOOM_OOUT       = 0x0040
FOCUS_PLUS      = 0x0080
FOCUS_SUB       = 0x0100

HEAD_STOP = 0x0000

NONE_MODEL      = 0
NETWORK_MODEL   = 1
SERIAL_MODEL    = 2

if sys.platform == 'win32':
    from msvcrt import getch
    print("Windows环境, 使用msvcrt")
else:
    import sys, tty, termios
    print("Linux环境, 使用termios")

def SUMCheck(strCode):
    All_btye = strCode.split()
    All_btye.remove(All_btye[0])
    sum = 0
    for each_byte in All_btye:
        each_num = int(each_byte, 16)
        sum += each_num
    return sum

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

class _Getch:
       #"""Gets a single character from standard input.  Does not echo to thescreen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

mygetch = _Getch()
class PelcoDDemo:
    m_Speed = 10
    m_client = tcp.TCP_Client()
    m_serial = ser.Serial()
    m_addr = 1
    m_model = NONE_MODEL
    lock_keyboard = threading.Lock()


    def Connect(self, strIP, nPort):
        if(self.m_client.StartConnect(strIP, nPort)):
            return True
        else:
            return False

    def OpenSer(self, strPortName, nBoundRate):
        if(self.m_serial.OpenSerial(strPortName, nBoundRate)):
            print("已打开串口")
            return True
        else:
            print("未打开串口")
            return False

    def Str2Bytes(self, strCode):
        bytesdata = bytes()
        senddataarr = strCode.split()
        for each in senddataarr:
            bytesdata += int(each,16).to_bytes(1, byteorder="little", signed=False)
        return bytesdata

    def SetSpeed(self):
        self.m_Speed = int(input("重新设置速度:"))

    def SetAddrCode(self):
        self.m_addr = int(input("重新转台地址:"))

    def MakePelcoDOrder(self, nOder,  Address, nSpeed = 1):
        if nOder == HEAD_GO_LEFT or nOder == HEAD_GO_RIGHT:
            str = "%02X %02X %02X %02X %02X 00" % (PelcoDHead, Address, nOder >> 8, nOder, nSpeed)
        elif nOder == HEAD_GO_UP or nOder == HEAD_GO_DOWN:
            str = "%02X %02X %02X %02X 00 %02X" % (PelcoDHead, Address, nOder >> 8, nOder, nSpeed)
        elif nOder == HEAD_GO_DOWN_LEFT or nOder == HEAD_GO_DOWN_RIGHT or nOder == HEAD_GO_UP_LEFT or nOder == HEAD_GO_UP_RIGHT:
            str = "%02X %02X %02X %02X %02X %02X" % (PelcoDHead, Address, nOder >> 8, nOder, nSpeed, nSpeed)
        else:
            str = "%02X %02X %02X %02X 00 00" % (PelcoDHead, Address, nOder >> 8, nOder)

        check_sum = SUMCheck(str)
        check_sum = check_sum & 0x00FF
        str += " %02X" % (check_sum)
        return str

    def GameModel(self):
        print("======游戏模式启动======")
        print("按键指南:")
        print("w 向上 s 向下 a 向左 a 向右")
        print("q 左上 e 右上 z 左下 c 右下")
        print("r 重置速度")
        print("f 重置云台地址码")
        print(">>当前云台地址码: 0x%02X" %(self.m_addr))
        print(">>当前云台速度值: 0x%02X" %(self.m_Speed))
        print(">>>>>>>>按p键退出")
        while True:
            order = ord(mygetch())
            order = chr(order)
            str = ""
            if(order == 'w'):
                self.OnGameModelPress(HEAD_GO_UP)
            if(order == 'd'):   
                self.OnGameModelPress(HEAD_GO_RIGHT)
            if(order == 's'):
                self.OnGameModelPress(HEAD_GO_DOWN)
            if(order == 'a'):
                self.OnGameModelPress(HEAD_GO_LEFT)
            if(order == 'q'):
                self.OnGameModelPress(HEAD_GO_UP_LEFT)
            if(order == 'e'):
                self.OnGameModelPress(HEAD_GO_UP_RIGHT)
            if(order == 'z'):
                self.OnGameModelPress(HEAD_GO_DOWN_LEFT)
            if(order == 'c'):
                self.OnGameModelPress(HEAD_GO_DOWN_RIGHT)
            if(order == ' '):
                self.OnGameModelPress(HEAD_STOP)
            if(order == 'r'):
                self.SetSpeed()
            if(order == 'f'):
                self.SetAddrCode()
            if(order == 'p'):
                return

    def OnGameModelPress(self, nOder):
        strPelcoD = self.MakePelcoDOrder(nOder, self.m_addr, self.m_Speed)
        print(strPelcoD)

        bytesdata = self.Str2Bytes(strPelcoD)
        self.SendDataInCurModel(bytesdata)
    
    def SendDataInCurModel(self, data):
        if self.m_model == NETWORK_MODEL:
            self.m_client.SendData(data)
        elif self.m_model == SERIAL_MODEL:
            self.m_serial.SendData(data)

if __name__ == '__main__':

    Demo = PelcoDDemo()

    print("=====PelcoD测试Demo=====")
    print("走网络还是串口?")
    print("1.TCP网络")
    print("2.串口")

    choose = 0
    choose = input("输入需要的指令:")
    
    if choose == '1':
        Demo.m_model = NETWORK_MODEL
        strIP = input("输入IP:")
        nPort = input("输入端口:")    

        if Demo.Connect(strIP, nPort) == False:
            sys.exit()

    else:
        Demo.m_model = SERIAL_MODEL
        strCOM_Name = input("输入串口号,Linux下需要使用绝对路径，如/dev/COM1:")
        nBp = input("输入波特率:") 

        if Demo.OpenSer(strCOM_Name, nBp) == False:
            sys.exit()
    
    Demo.GameModel()

