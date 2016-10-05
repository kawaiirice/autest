
import socket

def bind_unused_port(interface=''):
    '''
    Binds a server socket to an available port on 0.0.0.0.
    Returns a tuple (socket, port).

    Assume that the port will stay open as port are generally increased
    Als we have a very short time between getting the port and starting ATS

    '''
    sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((interface, 0))  # bind to all interfaces on an ephemeral port
    port = sock.getsockname()[1]
    return sock, port
