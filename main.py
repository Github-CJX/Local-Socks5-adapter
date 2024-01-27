import socket
import struct
from concurrent.futures import ThreadPoolExecutor

# 本地监听的地址和端口
LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 1080

# 需要认证的远程SOCKS5代理服务器的地址和端口
REMOTE_HOST = 'remote_socks5_server'

REMOTE_PORT = 1080

def handle_client(client_socket):
    # 接收客户端的请求
    version, nmethods = struct.unpack('!BB', client_socket.recv(2))
    methods = client_socket.recv(nmethods)

    # 回复客户端，告知无需认证
    client_socket.sendall(struct.pack('!BB', 5, 0))

    # 接收客户端的请求细节
    version, cmd, _, address_type = struct.unpack('!BBBB', client_socket.recv(4))
    if address_type == 1:  # IPv4
        target_address = socket.inet_ntoa(client_socket.recv(4))
    elif address_type == 3:  # 域名
        addr_len = struct.unpack('!B', client_socket.recv(1))[0]
        target_address = client_socket.recv(addr_len).decode('utf-8')
    target_port = struct.unpack('!H', client_socket.recv(2))[0]

    # 连接到远程SOCKS5代理服务器
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((REMOTE_HOST, REMOTE_PORT))

    # 发送用户名密码认证信息
    remote_socket.sendall(struct.pack('!BB', 1, len('username')))
    remote_socket.sendall('username'.encode('utf-8'))
    remote_socket.sendall(struct.pack('!B', len('password')))
    remote_socket.sendall('password'.encode('utf-8'))

    # 接收认证结果
    version, status = struct.unpack('!BB', remote_socket.recv(2))
    if status != 0:
        # 认证失败，关闭连接
        client_socket.close()
        remote_socket.close()
        print(f'Authentication failed and link is closed')
        return

    # 发送请求细节到远程SOCKS5代理服务器
    remote_socket.sendall(struct.pack('!BBB', version, cmd, 0))
    if address_type == 1:  # IPv4
        remote_socket.sendall(client_socket.recv(4))
    elif address_type == 3:  # 域名
        remote_socket.sendall(struct.pack('!B', addr_len))
        remote_socket.sendall(client_socket.recv(addr_len))
    remote_socket.sendall(struct.pack('!H', target_port))

    # 转发数据
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        remote_socket.sendall(data)

    # 接收响应数据并转发回客户端
    while True:
        data = remote_socket.recv(4096)
        if not data:
            break
        client_socket.sendall(data)

    # 关闭连接
    client_socket.close()
    remote_socket.close()

def main():
    # 创建本地监听socket
    local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_socket.bind((LOCAL_HOST, LOCAL_PORT))
    local_socket.listen(5)

    print(f'Started listening on {LOCAL_HOST}:{LOCAL_PORT}')

    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=10)

    while True:
        client_socket, addr = local_socket.accept()
        print(f'Accepted connection from {addr[0]}:{addr[1]}')
        # 提交任务到线程池处理
        executor.submit(handle_client, client_socket)

if __name__ == '__main__':
    main()
