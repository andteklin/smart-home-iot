# udp.py
import socket

UDP_PORT = 5005

def init_udp(bind_ip="0.0.0.0"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, UDP_PORT))
    sock.setblocking(False)
    return sock

def send_msg(sock, target_ip, msg):
    sock.sendto(msg.encode(), (target_ip, UDP_PORT))

def recv_msg(sock):
    try:
        data, addr = sock.recvfrom(1024)
        return data.decode(), addr[0]
    except:
        return None, None
