import socket
import threading
import json

class Host:
    port = "1025"
    data = {"message": "default"}
    host = None

    @classmethod
    def start_server(cls, port, host):
        cls.port = port
        cls.host = host
        t = threading.Thread(target=cls.server_run, daemon=True)
        t.start()
    
    @classmethod
    def server_run(cls):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", cls.port))
        server.listen(1)

        print(f"Server running on 127.0.0.1:{cls.port}")

        while True:
            conn, addr = server.accept()
            print("Connected:", addr)

            cls.data = cls.host.get_server_data()
            message_bytes = json.dumps(cls.data).encode()

            conn.sendall(message_bytes)
            conn.close()

class Client:
    port = "1025"
    receiver = None

    @classmethod
    def join_server(cls, port, receiver):
        cls.port = port
        cls.receiver = receiver
        t = threading.Thread(target=cls.connect_to_server, daemon=True)
        t.start()

    @classmethod
    def connect_to_server(cls):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", cls.port))
            request = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
            s.sendall(request)
            response = s.recv(4096)
            cls.receiver.update_server(json.loads(response.decode()))
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            s.close()