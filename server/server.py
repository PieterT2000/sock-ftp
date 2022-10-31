import os
import sys
from socket import *

sys.path.insert(0, '..')
from helpers import *


if len(sys.argv) < 2:
    print("Usage: python server.py <port>")
    exit(1)

port = sys.argv[1]

# Create a TCP socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
try:
    serverSocket.bind(('', int(port)))
    serverSocket.listen(1)
except Exception as e:
    log_error(CustomError(e.__class__.__name__, e.__str__()), ("", port))
    exit(1)
print(f"Server up and running at port {port}")


def handle_get(fd, cli_conn, cli_addr):
    file_does_not_exist = not os.path.isfile(fd)
    if file_does_not_exist:
        cli_conn.send(
            f"ERROR FileNotFoundError File not found on server {BODY_DELIM}".encode("utf-8"))
        log_error(CustomError("FileNotFoundError", f"get {fd}",
                  "File not found on server"), cli_addr)
        return
    else:
        cli_conn.send(f"OK {BODY_DELIM}".encode("utf-8"))
        try:
            send_file(fd, cli_conn)
            log_success(f"get {fd}", cli_addr)
        except Exception as e:
            raise


def handle_put(fd, cli_conn, cli_addr):
    file_exists = os.path.isfile(fd)
    if file_exists:
        cli_conn.send(
            "ERROR FileExists Can't overwrite existing file on server".encode("utf-8"))
        log_error(CustomError("FileExists", f"put {fd}",
                  "Can't overwrite existing file on server"), cli_addr)
    else:
        cli_conn.send(f"OK".encode("utf-8"))
        try:
            recv_file(fd, cli_conn, SERVER)
            log_success(f"put {fd}", cli_addr)
        except Exception as e:
            raise


def handle_list(fd, cli_conn, cli_addr):
    ls = "***".join(os.listdir())
    cli_conn.send(ls.encode("utf-8"))
    log_success(f"list", cli_addr)


cmd_map = {
    "get": handle_get,
    "put": handle_put,
    "list": handle_list,
    "ls": handle_list,
}

while True:
    try:
        cli_conn, addr = serverSocket.accept()
        # do get, put or list
        message = cli_conn.recv(2048).decode('utf-8')
        if not message:
            continue
        [cmd, *fd] = message.split()

        try:
            cmd_map[cmd]("".join(fd), cli_conn, addr)
        except Exception as e:
            log_error(CustomError(e.__class__.__name__,
                      message, e.__str__()), addr)
        finally:
            cli_conn.close()
    except KeyboardInterrupt:
        print("\rShutting down server...")
        serverSocket.close()
        exit(0)


"""
Server commands send through socket:
** get <fd>
    * If file exists, should return file size. 
    * After EOF, should close file descriptor and close connection
** put <fd> (<data>, in next message)
** list
"""
