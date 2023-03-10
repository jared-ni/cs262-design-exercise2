from unittest import TestCase
from unittest import mock
import unittest
import clock
import time
from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
from collections import deque

FORMAT = 'ascii'
BYTE_ORDER = 'big'

class TestProcesses():
    def test_consumer_pros(self, ):
        print("TEST 1")
        localHost= "127.0.0.1"
        port1 = 18001
        port2 = 28001
        config1=[localHost, port1, port2]
        config1.append(os.getpid())
        ThisProcess = clock.MachineProcess(config1)
        
        def new_thread(ThisProcess):
            ADDR, PORT = str(ThisProcess.config["address"]), int(ThisProcess.config["server_port"])
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((ADDR, PORT))
            server.listen()
            while True:
                conn, addr = server.accept()
                time.sleep(3)
                ThisProcess.server_socket = conn
                print("!!!!! SERVER SOCKET")
                print(ThisProcess.server_socket)
                # start consumer thread for every consumer
                start_new_thread(clock.consumer, (conn, ThisProcess))

        init_thread = Thread(target=new_thread, args=(ThisProcess,))
        init_thread.start()

        
        config2=[localHost, port2, port1]
        config2.append(os.getpid())
        ThisProcess2 = clock.MachineProcess(config2)
        ADDR2, PORT2 = str(ThisProcess2.config['address']), int(ThisProcess2.config["client_port"])
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        time.sleep(3)

        client.connect((ADDR2, PORT2))

        time.sleep(3)

        codeVal = str(ThisProcess2.logical_clock) + "~" + str(ThisProcess2.code)
        message_body = codeVal.encode(FORMAT)
        message_length = len(message_body).to_bytes(1, BYTE_ORDER)
        client.send(message_length + message_body)

        codeVal = '1~testMessage1'
        message_body = codeVal.encode(FORMAT)
        message_length = len(message_body).to_bytes(1, BYTE_ORDER)
        client.send(message_length + message_body)

        codeVal = '2~testMessage2'
        message_body = codeVal.encode(FORMAT)
        message_length = len(message_body).to_bytes(1, BYTE_ORDER)
        client.send(message_length + message_body)

        time.sleep(2)
        assert ThisProcess.msg_queue.popleft() == '0~msg0'
        assert ThisProcess.msg_queue.popleft() == '1~testMessage1'
        assert ThisProcess.msg_queue.popleft() == '2~testMessage2'
        assert not ThisProcess.msg_queue


    def test_init_machine_pros(self, ):
        print("TEST 2")
        localHost= "127.0.0.1"
        port1 = 18002
        port2 = 28002
        config1=[localHost, port1, port2]
        config1.append(os.getpid())
        ThisProcess1 = clock.MachineProcess(config1)

        init_thread1 = Thread(target=clock.init_machine, args=(ThisProcess1,))
        init_thread1.start()

        time.sleep(3)

        config2=[localHost, port2, port1]
        config2.append(os.getpid())
        ThisProcess3 = clock.MachineProcess(config2)
        ADDR2, PORT2 = str(ThisProcess3.config['address']), int(ThisProcess3.config["client_port"])
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        time.sleep(3)

        client.connect((ADDR2, PORT2))

        time.sleep(3)

        codeVal = str(ThisProcess3.logical_clock) + "~" + str(ThisProcess3.code)
        message_body = codeVal.encode(FORMAT)
        message_length = len(message_body).to_bytes(1, BYTE_ORDER)
        client.send(message_length + message_body)

        codeVal = codeVal = '10~testMessage10'
        message_body = codeVal.encode(FORMAT)
        message_length = len(message_body).to_bytes(1, BYTE_ORDER)
        client.send(message_length + message_body)

        codeVal = codeVal = '100~testMessage100'
        message_body = codeVal.encode(FORMAT)
        message_length = len(message_body).to_bytes(1, BYTE_ORDER)
        client.send(message_length + message_body)

        codeVal = codeVal = 'good~everythingWorks1234'
        message_body = codeVal.encode(FORMAT)
        message_length = len(message_body).to_bytes(1, BYTE_ORDER)
        client.send(message_length + message_body)

        time.sleep(2)

        assert ThisProcess1.msg_queue.popleft() == '0~msg0'
        assert ThisProcess1.msg_queue.popleft() == '10~testMessage10'
        assert ThisProcess1.msg_queue.popleft() == '100~testMessage100'
        assert ThisProcess1.msg_queue.popleft() == 'good~everythingWorks1234'
        assert not ThisProcess1.msg_queue


class TestClock(TestCase):

    def test_consumer(self, ):
        
        testCases = TestProcesses()
        test_case = Process(target=testCases.test_consumer_pros, args=())
        test_case.start()
        time.sleep(11)
        test_case.terminate()


    def test_init_machine(self):

        testCases = TestProcesses()
        test_case = Process(target=testCases.test_init_machine_pros, args=())
        test_case.start()
        time.sleep(11)
        test_case.terminate()


    def test_machine(self):
        print("TEST 3")
        localHost= "127.0.0.1"
        port1 = 18008
        port2 = 28008
        config1=[localHost, port1, port2]

        p1 = Process(target=clock.machine, args=(config1, 1))

        p1.start()

        config2=[localHost, port2, port1]
        p2 = Process(target=clock.machine, args=(config2, 2))

        p2.start()

        time.sleep(5)
        p1.terminate()
        p2.terminate()
        
        time.sleep(2)
        self.assertTrue(p1)
        self.assertTrue(p2)


if __name__ == '__main__':
    unittest.main()