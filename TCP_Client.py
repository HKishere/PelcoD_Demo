#!/usr/bin/python3
from pickle import TRUE
import socket  #导入socket模块
import time
import threading

def OnRecv(data):
    print(data.decode())

class TCP_Client:
    m_port = 9999
    m_IP = "192.168.2.213"
    m_bconnect = False
    m_server_socket = 0
    CallBack = None

    def SetCallBack(self, callbackfunc):
        self.CallBack = callbackfunc

    def StartConnect(self, strIP, nPort):
        self.m_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if strIP != '':
            self.m_IP = strIP
        if nPort != '':
            self.m_port = int(nPort)

        address = (self.m_IP, self.m_port)
        try:
            ret = self.m_server_socket.connect(address)
        except:
            print("连接失败!")
            return False
        # 为服务器绑定一个固定的地址，ip和端口
        self.m_bconnect = True
        self.tRecv = threading.Thread(None, self.ThunFunc)
        self.tRecv.start()
        print("连接成功!")
        return True
        

    def SendData(self, data):
        if self.m_bconnect:
            self.m_server_socket.send(data)

    def ThunFunc(self):
        while True:
            if self.m_bconnect:
                recvbuffer = self.m_server_socket.recv(1024)
                #print(recvbuffer.hex(' '))
                if self.CallBack != None:
                    self.CallBack(recvbuffer)
                
                

if __name__ == "__main__":
    client = TCP_Client()
    client.StartConnect("127.0.0.1", 9999)
    client.SetCallBack(OnRecv)

    client.SendData(("hello world").encode())#python3.5以上需要编码成byte


    


