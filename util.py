import socket
import os
import struct


class Socket_client:

    def __init__(self):
        self.conn = socket.socket()
        self.conn.connect(("localhost", 1024))
        print(self.conn.recv(1024).decode())

    def handle(self, path):
        detection_result_path = ''
        recognition_result_path = ''

        if os.path.isfile(path):
            self.send_to_server(path)
            detection_result_path = self.recv_from_server()
            recognition_result_path = self.recv_from_server()
        return detection_result_path, recognition_result_path

    def send_to_server(self, filepath):
        file_head = struct.pack('128sl', bytes(os.path.basename(filepath).encode('utf-8')), os.stat(filepath).st_size)
        self.conn.send(file_head)
        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                print('{} send over...'.format(filepath))
                break
            self.conn.send(data)

    def recv_from_server(self):
        file_info_size = struct.calcsize('128sl')
        buf = self.conn.recv(file_info_size)
        result_path = ''
        if buf:
            file_name, file_size = struct.unpack('128sl', buf)
            result_path = os.path.join(str.encode('./output'), file_name.strip(str.encode('\00'))).decode()
            recv_size = 0
            fp = open(result_path, 'wb')
            while not recv_size == file_size:
                if file_size - recv_size > 1024:
                    data = self.conn.recv(1024)
                    recv_size += len(data)
                else:
                    data = self.conn.recv(file_size - recv_size)
                    recv_size = file_size
                fp.write(data)
            fp.close()
            print('{} recv over...'.format(result_path))
        return result_path

    def close(self):
        self.conn.close()