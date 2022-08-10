# WLAN
from machine import UART, Pin
import utime

# UART
# uart = machine.UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

STA_IF = 1
STA = 1

class WLAN():
    is_connected = False
    wlan_status = -1
    
    def __init__(self, mode=STA):
        mode_nr = 1
        # AT command Test
        if  not 'OK' in self.sendCMD_waitResp("AT\r\n"):
            return None
        
        #sendCMD_waitResp("AT+GMR\r\n") # AT version
        #sendCMD_waitResp("AT+RST\r\n") #  reset
        if mode == STA:
            # Station Mode
            mode_nr = 1
        if not 'OK' in self.sendATcmd_waitResp("CWMODE_CUR={}".format(mode_nr)):
            return None
        # DHCP on:
        if not 'OK' in self.sendATcmd_waitResp("CWDHCP_CUR=1,1"):
            return None
    
                
    # internal Functions:
    def sendCMD_waitResp(self, cmd, timeout=3000):
        print("CMD: " + cmd)
        uart.write("{}".format(cmd))
        resp = self.waitResp(timeout)
        # print()
        return resp
        
        
    def sendATcmd_waitResp(self, cmd, timeout=3000):
        print("CMD: AT+" + cmd)
        uart.write("AT+{}\r\n".format(cmd))
        resp = self.waitResp(timeout)
        # print()
        return resp
    
    
    def waitResp(self, timeout=3000):
        prvMills = utime.ticks_ms()
        resp = b""
        while (utime.ticks_ms()-prvMills) < timeout:
            if uart.any():
                resp = b"".join([resp, uart.read(1)])
        # print(resp)
        return resp
        
        
    def active(self, active_val):
        ret_val = True
        return ret_val
    
    
    def connect(self, ssid=None, key=None):
        # AP connecting:
        status = self.sendATcmd_waitResp('CWJAP_CUR="{}","{}"'.format(ssid, key))
        if "WIFI CONNECTED" in status:
            self.is_connected = True
        return status
    
    
    def isconnected(self):
        # self.is_connected = False
        # print("wlan.isconnected: {}".format(self.is_connected))
        return self.is_connected
        
        
    def status(self):
        ret_val = self.sendATcmd_waitResp("CIPSTA_CUR?") # network check (NW-Status)
        print("wlan.status: {}".format(self.wlan_status))
        return self.wlan_status
    
    
    def ifconfig(self):
        # Get IP Addr.:
        retval = self.sendATcmd_waitResp("CIPSTA_CUR?")
        return retval
    
    
    def tcp_server(self, port):
        # Enable Multiple Connections:
        if not self.send_cmd("AT+CIPMUX=1", 'OK'):
            return False
        # Create TCP Server:
        retval = self.send_cmd('AT+CIPSERVER=1,{}'.format(port), 'OK')
        return retval
    
    def tcp_close(self, linkID):
        # End the TCP Connection
        # self.sendATcmd_waitResp("CIPCLOSE={}".format(linkID))
        self.send('AT+CIPCLOSE={}'.format(linkID), 'OK')
        
        
    def ReceiveData(self):
        s = uart.read()
        if (s != None):
            s = s.decode()
            # print(s)
            if '+IPD' in s:
                n1 = s.find('+IPD,')
                n2 = s.find(',', n1 + 5)
                linkID = int(s[n1 + 5:n2])
                n3 = s.find(':')
                http = s[n3 + 1:]
                n4 = s.find('HTTP')
                request_line = s[n3 + 1:n4]
                #print("linkID="+str(ID) + ", Data="+s)+
                return linkID, http, request_line
        return None, None, None
           
           
    def send_data(self, linkID, data):
        self.send_cmd('AT+CIPSEND={0},{1}'.format(linkID, len(data)), '>')
        uart.write(data)
        #print("sendData: '" + data + "'")
    
    
    def send_cmd(self, cmd, ack, timeout=2000):
        print("send_cmd: {}".format(cmd))
        uart.write('{}\r\n'.format(cmd))
        retval = self.wait_ack(ack, timeout)
        return retval

            
    def wait_ack(self, ack, timeout=2000):
        t = utime.ticks_ms()
        while (utime.ticks_ms() - t) < timeout:
            s = uart.read()
            if (s != None):
                s = s.decode()
                print(s)
                if ack in s:
                    return True
        return False
    