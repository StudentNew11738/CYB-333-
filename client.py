import socket
HOST = '127.0.0.1'
PORT = 5000

def start_client():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(5)
            print(f'Connecting to {HOST}:{PORT}...', flush=True)
            client.connect((HOST, PORT))
            print('Successfully connected to server!', flush=True)
            message = 'Hello Server! This is the CYB 333 client.'
            client.sendall(message.encode('utf-8'))
            print(f'Client sent: {message}', flush=True)
            response = client.recv(1024)
            if response:
                print(f'Server replied: {response.decode("utf-8")}', flush=True)
            else:
                print('Server closed without a response.', flush=True)
            print('Client connection closed cleanly.', flush=True)
    except ConnectionRefusedError:
        print('ERROR: Connection refused. Is the server running?', flush=True)
    except socket.timeout:
        print('ERROR: Connection timed out.', flush=True)
    except OSError as error:
        print(f'Connection error: {error}', flush=True)

if __name__ == '__main__':
    start_client()
