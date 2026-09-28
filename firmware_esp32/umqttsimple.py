import usocket as socket
import ustruct as struct
from ubinascii import hexlify
# A biblioteca padrão e leve do MicroPython para cliente MQTT.# Arquivo: firmware_esp32/umqttsimple.py

class MQTTException(Exception):
    pass

class MQTTClient:
    def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={}):
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False

    def _send_str(self, s):
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self.sock.read(1)
            if not b:
                return None
            b = b[0]
            n |= (b & 0x7f) << sh
            if not (b & 0x80):
                return n
            sh += 7

    def connect(self, clean_session=True):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        if self.ssl:
            import ussl
            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)
        msg = bytearray(b"\x10\x00\x00\x00")
        msg[1] = 10 + 2 + len(self.client_id)
        msg[2] = 0
        msg[3] = 4
        msg[4] = ord('M')
        msg[5] = ord('Q')
        msg[6] = ord('T')
        msg[7] = ord('T')
        msg[8] = 4
        msg[9] = 0x02 if clean_session else 0
        msg[10] = 0
        msg[11] = self.keepalive
        self.sock.write(msg)
        self._send_str(self.client_id)
        resp = self.sock.read(4)
        return resp[3] == 0

    def publish(self, topic, msg, retain=False, qos=0):
        pkt = bytearray(b"\x30\x00\x00\x00")
        pkt[0] |= (qos << 1) | (1 if retain else 0)
        sz = 2 + len(topic) + len(msg)
        if sz >= 2097152:
            raise MQTTException("Payload muito grande")
        i = 1
        while sz > 0x7f:
            pkt[i] = (sz & 0x7f) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz & 0x7f
        self.sock.write(pkt[:i+1])
        self._send_str(topic)
        self.sock.write(msg)

    def disconnect(self):
        self.sock.write(b"\xe0\x00")
        self.sock.close()