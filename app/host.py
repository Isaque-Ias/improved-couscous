import socket
import threading
import json
import time

class Host:
    port = 1025
    host_logic = None
    clients = []
    clients_lock = threading.Lock()
    server_socket = None

    @classmethod
    def start_server(cls, port, host_logic):
        cls.port = int(port)
        cls.host_logic = host_logic

        cls.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.server_socket.bind(("127.0.0.1", cls.port))
        cls.server_socket.listen(20)

        print(f"Server running on 127.0.0.1:{cls.port}")

        # Accept client connections
        threading.Thread(target=cls.accept_loop, daemon=True).start()

        # Send updates to clients
        threading.Thread(target=cls.broadcast_loop, daemon=True).start()

    @classmethod
    def accept_loop(cls):
        while True:
            conn, addr = cls.server_socket.accept()
            print(f"Client connected: {addr}")

            with cls.clients_lock:
                cls.clients.append(conn)

            # Each client handled in a new thread
            threading.Thread(target=cls.client_handler, args=(conn,), daemon=True).start()

    @classmethod
    def client_handler(cls, conn):
        """Receives player data continuously"""
        while True:
            try:
                raw = conn.recv(4096)
                if not raw:
                    break

                data = json.loads(raw.decode())
                cls.host_logic.set_player(data)

            except:
                break

        # remove client
        with cls.clients_lock:
            if conn in cls.clients:
                cls.clients.remove(conn)

        conn.close()
        print("Client disconnected")

    @classmethod
    def broadcast_loop(cls):
        """Sends server state to all clients ~20 times/sec"""
        while True:
            try:
                packet = json.dumps(cls.host_logic.get_server_data()).encode()

                dead = []

                with cls.clients_lock:
                    for c in cls.clients:
                        try:
                            c.sendall(packet)
                        except:
                            dead.append(c)

                    # cleanup
                    for dc in dead:
                        cls.clients.remove(dc)
                        dc.close()

            except Exception as e:
                print("Broadcast error:", e)

            time.sleep(0.05)  # 20 updates/sec
