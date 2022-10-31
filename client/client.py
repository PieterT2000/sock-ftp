import sys
from socket import *
import os

sys.path.insert(0, '..')
from helpers import *

if len(sys.argv) < 4:
    print("Usage: python3 client.py <hostname> <port> <cmd> [fd]")
    exit(1)

hostname = sys.argv[1]
try:
    port = int(sys.argv[2])
except ValueError:
    print("Port must be an integer")
    exit(1)
server_addr = (hostname, port)
cmd = sys.argv[3]

if cmd in ["put", "get"] and len(sys.argv) < 5:
    print("Please provide a file location for put and get commands")
    print("Usage: python3 client.py <hostname> <port> <cmd> [fd]")
    exit(1)

fd = sys.argv[4] if cmd in ["put", "get"] else ""


client = socket(AF_INET, SOCK_STREAM)
# handshake
client.connect((hostname, port))


def get(fd, client):
    # check if file exists
    if os.path.isfile(fd):
        raise FileExistsError("Can't overwrite existing file on client")

    client.send(f"get {fd}".encode("utf-8"))
    res = client.recv(1024).decode("utf-8")
    [status, next_data] = res.split(BODY_DELIM)
    [code, *error] = status.split()
    if code != "OK":
        error_msg = " ".join(error)
        log_error(CustomError(error_msg, f"get {fd}"), server_addr)
        return

    try:
        recv_file(fd, client, CLIENT, next_data)
        log_success(f"get {fd}", server_addr)
    except Exception as e:
        raise


def put(fd, client):
    if not os.path.isfile(fd):
        raise FileNotFoundError("File not found on client")

    client.send(f"put {fd}".encode("utf-8"))
    res = client.recv(1024).decode("utf-8")
    [code, *error] = res.split()
    if code != "OK":
        error_msg = " ".join(error)
        log_error(CustomError(
            error_msg, f"get {fd}"), addr)
        return

    try:
        send_file(fd, client)
        log_success(f"put {fd}", server_addr)
    except Exception as e:
        raise


def get_list(fd, client):
    client.send(f"list".encode("utf-8"))
    res = client.recv(2048).decode("utf-8")
    print("./")
    for item in res.split("***"):
        print(f"  {item}")
    log_success(f"list", server_addr)


cmd_map = {
    'get': get,
    'put': put,
    'list': get_list,
    'ls': get_list,
}

try:
    cmd_map[cmd](fd, client)
except KeyError:
    log_error(CustomError("InvalidCommand", cmd,
              "Valid commands are: [get, put, list]"), server_addr)
except Exception as e:
    log_error(CustomError(e.__class__.__name__,
              f"{cmd} {fd}", e.__str__()), server_addr)
finally:
    client.close()
    exit(0)
