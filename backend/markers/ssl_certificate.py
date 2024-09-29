import ssl
import socket

def ssl_certificate(domain: str):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain, 443))
            cert = s.getpeercert()
        return True
    except Exception as e:
        # SSL certificate is invalid or absent
        return False
