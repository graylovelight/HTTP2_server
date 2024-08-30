import socket
import ssl
import h2.connection
import h2.events
import h2.config

class HTTP2Server:
    def __init__(self, host, port, certfile, keyfile):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print("HTTP2服务器已启动，监听地址：%s，端口：%d" % (self.host, self.port))

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        context.set_alpn_protocols(['h2'])

        while True:
            conn, addr = sock.accept()
            print("接收到来自 %s 的连接" % str(addr))
            try:
                tls_conn = context.wrap_socket(conn, server_side=True)
                handle(tls_conn)
            except ssl.SSLError as e:
                print("SSL错误：", e)
            except Exception as e:
                print("连接处理过程中出错：", e)
            finally:
                conn.close()

def send_response(h2_conn, stream_id, headers):
    path = headers[":path"]

    if path == "/Hikari":
        with open(r'光光.png', 'rb') as f:
            response_data = f.read()
        content_type = 'image/jpeg'
    elif path == "/little":
        with open(r'小图片.JPG', 'rb') as f:
            response_data = f.read()
        content_type = 'image/jpeg'
    else:
        response_data = b"<html><body><h1>Hello, World!</h1></body></html>"
        content_type = 'text/html'

    response_headers = [
        (':status', '200'),
        ('server', 'basic-h2-server/1.0'),
        ('content-length', str(len(response_data))),
        ('content-type', content_type),
    ]

    h2_conn.send_headers(stream_id, response_headers)
    h2_conn.send_data(stream_id, response_data, end_stream=True)
    print("响应已发送")

def handle(tls_sock):
    config = h2.config.H2Configuration(client_side=False)
    h2_conn = h2.connection.H2Connection(config=config)
    h2_conn.initiate_connection()
    tls_sock.sendall(h2_conn.data_to_send())

    while True:
        data = tls_sock.recv(65535)
        if not data:
            break

        events = h2_conn.receive_data(data)
        for event in events:
            if isinstance(event, h2.events.RequestReceived):
                headers = {k: v for k, v in event.headers}
                method = headers[":method"]
                path = headers[":path"]

                print("请求方法：%s，路径：%s" % (method, path))
                send_response(h2_conn, event.stream_id, headers)

        data_to_send = h2_conn.data_to_send()
        if data_to_send:
            tls_sock.sendall(data_to_send)

if __name__ == "__main__":
    HOST = '0.0.0.0'
    PORT = 8080
    CERTFILE = r'证书\cert.pem'
    KEYFILE = r'证书\key.pem'
    server = HTTP2Server(HOST, PORT, CERTFILE, KEYFILE)
    server.start()
