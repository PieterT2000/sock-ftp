import os


class CustomError(Exception):
    def __init__(self, error_type, cmd, msg=''):
        self.error_type = error_type
        self.cmd = cmd
        self.msg = msg


def log_error(error_obj, socket_addr):
    print(
        f"({socket_addr[0]}, {socket_addr[1]}) {error_obj.cmd}: FAILURE - {error_obj.error_type} {error_obj.msg}")


def log_success(cmd, socket_addr):
    print(f"({socket_addr[0]}, {socket_addr[1]}) {cmd}: SUCCESS")


# Body delimiter is used to separate the body of the message from the header
BODY_DELIM = "\r\n"
# Agent type is either client or server
SERVER = "server"
CLIENT = "client"


def recv_file(fd, conn, agent_type, next_data=""):
    abs_path_to_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), agent_type, fd)
    abs_dir = os.path.dirname(abs_path_to_file)
    # create nested directory if it doesn't exist
    if not os.path.isdir(abs_dir):
        os.makedirs(abs_dir)
    try:
        with open(abs_path_to_file, "xb") as f:
            # In case we already received some file data in the first recv call
            if next_data:
                f.write(next_data)
            while True:
                data = conn.recv(2048)
                if not data:
                    break
                f.write(data)
    except Exception as e:
        print(e)
        raise


def send_file(fd, conn):
    try:
        with open(fd, "rb") as f:
            data = f.read(2048)
            while data:
                conn.sendall(data)
                data = f.read(2048)
    except Exception as e:
        raise
