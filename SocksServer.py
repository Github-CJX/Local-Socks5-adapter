# Socks5用户名认证转无需认证Socks5接口
import concurrent
import ctypes
import socket
import struct
import socks
import json
from concurrent.futures import ThreadPoolExecutor

# 创建线程池
executor = ThreadPoolExecutor(max_workers=50)

try:
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)

    REMOTE_SOCKS5_HOST = config_data.get('REMOTE_SOCKS5_HOST', '')
    REMOTE_SOCKS5_PORT = config_data.get('REMOTE_SOCKS5_PORT', 0)
    USERNAME = config_data.get('USERNAME', '')
    PASSWORD = config_data.get('PASSWORD', '')

except FileNotFoundError:
    ctypes.windll.user32.MessageBoxW(None, "没有找到config.json配置文件", "提示", 0x40)
    exit()

# 设置本地SOCKS5代理服务器的信息
LOCAL_SOCKS5_HOST = '127.0.0.1'
LOCAL_SOCKS5_PORT = 1080


def handle_client_to_remote(client_socket, remote_socket):
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            remote_socket.sendall(data)
    except Exception as e:
        print(f"Error: {e}")


def handle_remote_to_client(client_socket, remote_socket):
    try:
        while True:
            data = remote_socket.recv(4096)
            if not data:
                break
            client_socket.sendall(data)
    except Exception as e:
        print(f"Error: {e}")


def handle_client_connection(client_socket):
    try:
        # 与客户端进行SOCKS5握手
        client_socket.recv(256)  # 足够大以接收所有可能的客户端认证方法
        client_socket.sendall(b'\x05\x00')  # 响应客户端支持SOCKS5无需认证

        # 接收客户端的连接请求
        version, cmd, _, address_type = struct.unpack('!BBBB', client_socket.recv(4))
        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(client_socket.recv(4))
        elif address_type == 3:  # Domain name
            domain_length = client_socket.recv(1)[0]
            address = client_socket.recv(domain_length).decode('utf-8')
        else:
            client_socket.close()
            return

        target_port = struct.unpack('!H', client_socket.recv(2))[0]

        # 响应客户端请求成功
        # 这里的响应是一个占位符，地址和端口都是0
        response = b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00'
        client_socket.sendall(response)

        # 创建到远程SOCKS5代理的连接
        remote_sock = socks.socksocket()
        remote_sock.set_proxy(socks.SOCKS5, REMOTE_SOCKS5_HOST, REMOTE_SOCKS5_PORT, True, USERNAME, PASSWORD)
        remote_sock.connect((address, target_port))

        # 转发客户端到远程代理的数据
        # 提交任务给ThreadPoolExecutor
        future_client_to_remote = executor.submit(handle_client_to_remote, client_socket, remote_sock)
        future_remote_to_client = executor.submit(handle_remote_to_client, client_socket, remote_sock)

        # 等待两个线程都完成
        concurrent.futures.wait([future_client_to_remote, future_remote_to_client],
                                return_when=concurrent.futures.ALL_COMPLETED)

    except Exception as e:
        print(f"CC Error: {e}")
    finally:
        client_socket.close()
        if 'remote_sock' in locals():
            remote_sock.close()
        print(f"[-] A local connection has been processed")


def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((LOCAL_SOCKS5_HOST, LOCAL_SOCKS5_PORT))
        server.listen(5)
        print(f"[*] Listening on {LOCAL_SOCKS5_HOST}:{LOCAL_SOCKS5_PORT}")
        ctypes.windll.user32.MessageBoxW(None, "SocksServer服务启动成功", "提示", 0x40)

        while True:
            client_sock, address = server.accept()
            print(f"[+] Accepted connection from {address[0]}:{address[1]}")
            executor.submit(handle_client_connection, client_sock)

    except Exception as e:
        # 捕获异常，显示连接失败的提示框
        ctypes.windll.user32.MessageBoxW(None, f"SocksServer服务启动失败：{str(e)}", "提示", 0x40)
        exit()


if __name__ == '__main__':
    main()
