import socket
HOST = '127.0.0.1'
PORT = 5000

def start_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen(1)
            print(f'Server listening on {HOST}:{PORT}', flush=True)
            connection, address = server.accept()
            with connection:
                print(f'Connected to client: {address}', flush=True)
                connection.settimeout(10)
                data = connection.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    print(f'Client says: {message}', flush=True)
                    response = 'Server received your message!'
                    connection.sendall(response.encode('utf-8'))
                    print(f'Server sent: {response}', flush=True)
                else:
                    print('Client disconnected without sending data.', flush=True)
            print('Client connection closed cleanly.', flush=True)
    except socket.timeout:
        print('Error: Timed out waiting for client data.', flush=True)
    except OSError as error:
        print(f'Server error: {error}', flush=True)
    finally:
        print('Server shutdown complete.', flush=True)

if __name__ == '__main__':
    start_server()
