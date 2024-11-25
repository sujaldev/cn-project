from mitmproxy import http
import socket

# sock = socket.socket()


def request(flow: http.HTTPFlow):
    url = flow.request.pretty_url
    headers = "\n".join([f"{key}: {val}" for key, val in flow.request.headers.items()])
    # noinspection PyTypeChecker
    with socket.socket() as sock:
        sock.connect(("127.0.0.1", 54321))
        sock.sendall(bytes(f"URL: {url}\nHeaders:\n{headers}", "utf8"))
