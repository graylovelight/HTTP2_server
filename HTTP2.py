import json
import socket
import h2.connection
import h2.events
import h2.config

class HTTP2Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print("`HTTP2服务器已启动，监听地址：%s，端口：%d" % (self.host, self.port))

        while True:
            conn, addr = sock.accept()
            print("`接收到来自 %s 的连接" % str(addr))
            with conn:
                handle(conn)
def send_response(conn, event):
    stream_id = event.stream_id
    headers = {k: v for k, v in event.headers}
    path = headers[":path"]

    if path == "/little":
        with open(r'小图片.JPG', 'rb') as f:
            image_data = f.read()
        response_data = image_data
        content_length = len(response_data)
        content_type = 'image/jpeg'
    else:
        response_data = b"<html><body><h1>Hello, World!</h1></body></html>"
        content_length = len(response_data)
        content_type = 'text/html'

    conn.send_headers(
        stream_id=stream_id,
        headers=[
            (':status', '200'),
            ('server', 'basic-h2-server/1.0'),
            ('content-length', str(content_length)),
            ('content-type', content_type),
        ],
    )
    conn.send_data(
        stream_id=stream_id,
        data=response_data,
        end_stream=True
    )
    print("`响应已发送")


def handle(sock):
    config = h2.config.H2Configuration(client_side=False)
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()
    sock.sendall(conn.data_to_send())

    while True:
        data = sock.recv(65535)
        if not data:
            break

        events = conn.receive_data(data)
        for event in events:
            if isinstance(event, h2.events.RequestReceived):
                headers = {k: v for k, v in event.headers}
                method = headers[":method"]
                path = headers[":path"]

                if ":scheme" in headers:
                    http_version = "HTTP/2.0"
                else:
                    http_version = "HTTP/1.1"
                print("`请求方法：%s，路径：%s，HTTP版本：%s" % (method, path, http_version))
                send_response(conn, event)

        data_to_send = conn.data_to_send()
        if data_to_send:
            sock.sendall(data_to_send)




if __name__ == "__main__":
    HOST = '0.0.0.0'
    PORT = 8080
    server = HTTP2Server(HOST, PORT)
    server.start()