"""
Networks 8 - Dropbox
A file sharing client and server
PFTP = pseudo FTP
"""

import socket
import threading
import os
import time
import pdb
from sys import stdout
from select import *

ROOT_PATH = r'/Users/nirweingarten/Desktop/python'
download_dict = {}

class File(object):
    """
    A file object that describes varias attributes of a single file or folder
    """
    global download_dict
    def __init__(self, file_path):
        if os.path.exists(file_path):
            self.exists = True
            self.path = file_path
            self.abs_path = os.path.abspath(file_path)
            (self.name, self.ext) = os.path.splitext(os.path.basename(file_path))
            self.ext = self.ext.strip('.')
            self.isdir = os.path.isdir(file_path)
            self.size = os.path.getsize(file_path)
            ctime = time.strptime(time.ctime(os.path.getctime(file_path)),'%c')
            self.create_time = time.strftime(r'%d/%m/%Y %H:%M:%S', ctime)
            if download_dict.has_key(self.abs_path):
                self.downloads = download_dict[self.abs_path]
            else:
                self.downloads = 0
        else:
            self.exists = False
    def __str__(self):
        if self.exists:
            return (self.name + 20 * ' ')[:20] + '\t' + self.ext + '\t\t' + self.isdir.__str__() + '\t\t'\
                    + self.size.__str__() + '\t\t' + self.create_time + '\t    ' + self.downloads.__str__()
        else:
            return '\n'

class ClientThread(threading.Thread):
    """
    Recives a socket froma Pftp server object
    Sends hello to client and opens a thread that recives a commands
    Recives and executes clients commands
    """
    def __init__(self, socket):
        super(ClientThread, self).__init__()
        self.socket = socket
        self.curdir = ROOT_PATH
        self.is_alive = True
    def run(self):
        self.socket.send('Hello. time = {0}'.format(time.ctime()))
        while self.is_alive:
            self.socket.send('\n\n> ')
            rlist, _, _ = select([self.socket], [], [])

            if rlist:
                command = self.socket.recv(2048).lstrip(' ').rstrip('\n')

            if command == 'ls':
                self.get_file_list()

            elif command.startswith('cd '):
                dir_path = os.path.join(self.curdir, command.split(' ')[1])
                if os.path.isdir(dir_path):
                    dir_path = os.path.normpath(dir_path)
                    if dir_path.startswith(ROOT_PATH):
                        self.curdir = respond = dir_path
                    else:
                        respond = 'Requested dir out of file system'
                else:
                    respond = 'No such dir'
                self.socket.send(respond)

            elif command.startswith('get '):
                file_path = os.path.join(self.curdir, command.split(' ')[1])
                if os.path.isfile(file_path):
                    file_path = os.path.normpath(file_path)
                    if file_path.startswith(ROOT_PATH):
                        self.socket.send('Delivering {0}'.format(os.path.basename(file_path)))
                        with open(file_path, 'rb') as file:
                            rlist, wlist, _ = select([file], [self.socket], [])
                            if rlist and wlist:
                                self.socket.send(file.read())
                                time.sleep(1)
                    else:
                        self.socket.send('Requested file out of file system')
                else:
                    self.socket.send('No such dir')

            elif command == 'exit':
                self.is_alive = False
            else:
                self.socket.send(r'unknown command {0}'.format(command))
        self.socket.send('\nBye\n')
        self.socket.close()

    def get_file_list(self):
        """
        Returns nice string of file objects in client curdir
        """
        self.socket.send('\n' + self.curdir + '\n\n' + 'NAME\t\t\tEXT\t\tISDIR\t\tSIZE\t\tCREATE_TIME\t\tDOWNLOADS')
        for path in os.listdir(self.curdir):
            self.socket.send('\n' + File(os.path.join(self.curdir, path)).__str__())


class PftpServer(object):
    """
    Creates a pseudo FTP server on port 20 
    The server will listen on said port and open a client thread for each new connection
    """
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind(('',20))
        self.socket.listen(10)
        self.socket_list=[]
    def run(self):
        while True:
            (client_socket, address) = self.socket.accept()
            print 'New connection from ', address
            self.socket_list.append(client_socket)
            ct = ClientThread(client_socket)
            ct.start()
    def close(self):
        for socket in self.socket_list:
            socket.close()
        self.socket.close()

class PftpClient(threading.Thread):
    """
    blalbla
    instead of using ncat
    """
    def __init__(self, host_ip, dst_port=20):
        self.host_ip = host_ip
        self.dst_port = dst_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def run(self):
        self.socket.connect((self.host_ip,self.dst_port))
        print 'connected to ', self.socket.getpeername()
        print self.socket.recv(2048)
        self.running = True
        while self.running:     
            rlist1, _, _ = select([self.socket], [], [])
            if rlist1:
                msg = self.socket.recv(2048)
                stdout.write(msg)
                if '> ' in msg:
                    cmd = raw_input()
                    self.socket.send(cmd)
                elif 'Delivering' in msg:
                    file_name = msg.split(' ')[1]
                    file_path = os.path.join(os.getcwd(), file_name)
                    rlist2 = True
                    with open(file_path, 'wb') as file:
                        while rlist2:
                            rlist2 = False
                            rlist2, _, _ = select([self.socket], [], [], 0)                        
                            if rlist2:
                                data = self.socket.recv(2048)
                                file.write(data)
                        print '\nfetched file at ', file_path
                elif 'Bye' in msg:
                    self.running = False
                    self.close()
    def close(self):
        self.socket.close()


if __name__ == "__main__":
    print 'Start by creating a PftpServer object'
