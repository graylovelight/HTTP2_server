import socket
class HTTP1Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        try:
            # 创建一个TCP套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置套接字选项，允许地址重用
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 绑定主机和端口
            self.server_socket.bind((self.host, self.port))
            # 监听连接
            self.server_socket.listen(5)
            print("`HTTP1服务器已启动，监听地址：%s，端口：%d" % (self.host, self.port))

            while True:
                # 接受连接
                client_socket, client_address = self.server_socket.accept()
                print("`接收到来自 %s 的连接" % str(client_address))
                # 处理HTTP请求
                self.handle(client_socket)

        except Exception as e:
            print("`发生异常：%s" % str(e))

        finally:
            if self.server_socket:
                self.server_socket.close()
                print("`HTTP1服务器已关闭")

    def handle(self, client_socket):
        # 接收客户端请求数据
        request_data = client_socket.recv(1024).decode('utf-8')
        # 解析请求
        request_lines = request_data.split('\n')
        if request_lines:
            # 获取请求方法、路径和HTTP版本
            method, path, http_version = request_lines[0].strip().split()
            print("`请求方法：%s，路径：%s，HTTP版本：%s" % (method, path, http_version))

            # 构造HTTP响应
            if path == '/Hikari':
                # 读取本地图片文件
                with open(r'光光.png', 'rb') as f:
                    image_data = f.read()
                response_body = image_data
                content_length = len(response_body)
                content_type = 'image/jpeg'
            elif path == '/little':
                # 读取本地图片文件
                with open(r'小图片.JPG', 'rb') as f:
                    image_data = f.read()
                response_body = image_data
                content_length = len(response_body)
                content_type = 'image/jpeg'
            else:
                response_body = b"<html><body><h1>Hello, World!</h1></body></html>"
                content_length = len(response_body)
                content_type = 'text/html'

            response_headers = [
                b"HTTP/1.1 200 OK",
                b"Content-Type: %s" % content_type.encode('utf-8'),
                b"Content-Length: %d" % content_length,
                b"\n"
            ]
            response = b'\n'.join(response_headers) + response_body

            # 发送响应数据到客户端
            client_socket.sendall(response)
            # 关闭客户端连接
            client_socket.close()
            print("`响应已发送")

# 主函数
if __name__ == "__main__":
    # 服务器主机和端口
    HOST = '0.0.0.0'
    PORT = 8080
    # 创建HTTP服务器实例并启动
    http_server = HTTP1Server(HOST, PORT)
    http_server.start()
