# -*- coding: utf-8 -*-
"""
    probe and proxy
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-02-09 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.0'

__all__ = [
    'Probe',
    'Proxy',
]

import queue
import threading

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet.protocol import Protocol, Factory

from mymcp.protocols import *
from mymcp.protocols import ProtocolEnum as PE


class Probe:
    """
        探针
    """
    def __init__(self):
        self.queue = queue.Queue()
        self.status = PE.Status.HANDSHAKING
        self.threshold = -1

        self.codecs = {
            PE.Direction.SC: Codec(),
            PE.Direction.CS: Codec(),
        }

        self.running = True

    def probe(self, direct: PE.Direction, data: bytes):
        self.queue.put((direct, data))

    def run(self):
        threading.Thread(target=self._run).start()

    def _run(self):
        while self.running:
            direct, data = self.queue.get()
            for data_packet in self.codecs[direct].decode(data):

                _cls = ProtocolFactory.get_proto(direct, self.status, data_packet.pid)

                if _cls is None:
                    continue

                # Handshaking to Get Next State
                if self.status == PE.Status.HANDSHAKING:
                    if _cls == HandshakeProtocols.Client2Server.CSHandshake:
                        payload = _cls.decode(data_packet.bytes_io())
                        self.status = PE.Status(payload['next_state'])
                        continue

                # Get compression threshold in login state
                # Go to next state (configuration) when get LoginAcknowledged
                if self.status == PE.Status.LOGIN:
                    if _cls == LoginProtocols.Server2Client.SCLoginSetCompression:
                        payload = _cls.decode(data_packet.bytes_io())
                        for _ in self.codecs.values():
                            _.compression_threshold = payload['threshold']
                        self.threshold = payload['threshold']
                        continue

                    if _cls == LoginProtocols.Client2Server.CSLoginAcknowledged:
                        self.status = PE.Status.CONFIGURATION
                        continue

                # Go to next state (play) when get LoginAcknowledgedFinishConfiguration
                if self.status == PE.Status.CONFIGURATION:

                    if _cls == ConfigurationProtocols.Client2Server.CSLoginAcknowledgedFinishConfiguration:
                        self.status = PE.Status.PLAY
                        continue

                # Do What you want
                if self.status == PE.Status.PLAY:
                    self.play_protocol(direct, _cls, data_packet)

    def play_protocol(self, direct: PE.Direction, protocol_cls, data_packet: DataPacket):
        """
            Rewrite this function to make your own probe.
            This is just for examples.
        :param direct:
        :param protocol_cls:
        :param data_packet:
        :return:
        """
        ...


class PClient2Proxy(Protocol):
    """
        Client <> Proxy Protocol
    """
    def __init__(self):
        self.buffer = queue.Queue()
        self.proto_p2s = None
        self.probe: Probe | None = None

    def connectionMade(self):
        """
            Client Connect to Proxy
            1. connect to Server
            2. create a probe
        :return:
        """
        connectProtocol(
            TCP4ClientEndpoint(
                reactor, self.factory.server_host, self.factory.server_port
            ),
            PProxy2Server(self)
        )
        self.probe = self.factory.probe_cls()
        self.probe.run()

    def connectionLost(self, reason):
        """
            Close all connections
        :param reason:
        :return:
        """
        self.disconnect()

    def dataReceived(self, data):
        """
            Get data from client and send to server
        :param data:
        :return:
        """
        if self.proto_p2s is None:
            self.buffer.put(data)
        else:
            self.proto_p2s.transport.write(data)

        self.probe.probe(PE.Direction.CS, data)

    def disconnect(self):
        if self.probe:
            self.probe.running = False
        if self.proto_p2s:
            self.proto_p2s.transport.loseConnection()


class FClient2Proxy(Factory):

    protocol = PClient2Proxy

    def __init__(self, server_host: str, server_port: int, probe_cls):
        self.server_host = server_host
        self.server_port = server_port
        self.probe_cls = probe_cls


class PProxy2Server(Protocol):
    """
        Proxy <> Server Protocol
        Created by PClient2Proxy
    """

    def __init__(self, proto_client2proxy: PClient2Proxy):
        self.proto_client2proxy = proto_client2proxy

    def connectionMade(self):
        """
            Send all data in buffer
        :return:
        """
        while not self.proto_client2proxy.buffer.empty():
            self.transport.write(self.proto_client2proxy.buffer.get())
        self.proto_client2proxy.proto_p2s = self

    def connectionLost(self, reason):
        self.proto_client2proxy.disconnect()

    def dataReceived(self, data):
        self.proto_client2proxy.transport.write(data)
        self.proto_client2proxy.probe.probe(PE.Direction.SC, data)


class Proxy:
    """
        代理服务
    """
    def __init__(self, server_host: str, server_port: int = 25565, proxy_port: int = 25565, probe_cls = Probe):
        self.server_host = server_host
        self.server_port = server_port
        self.proxy_port = proxy_port
        self.probe_cls = probe_cls

    def run(self):
        print(f"Proxy running on {self.proxy_port}")
        TCP4ServerEndpoint(
            reactor, self.proxy_port
        ).listen(
            FClient2Proxy(self.server_host, self.server_port, self.probe_cls)
        )
        reactor.run()


if __name__ == '__main__':

    # for example
    class MyProbe(Probe):
        def play_protocol(self, direct: PE.Direction, protocol_cls, data_packet: DataPacket):

            # Create a protocol filter
            if protocol_cls not in (
                    PlayProtocols.Client2Server.CSPlayChatMessage,
                    PlayProtocols.Server2Client.SCPlayPlayerChatMessage
            ):
                return

            # Do what you want
            print(f"{protocol_cls.__name__:<30} > {protocol_cls.decode(data_packet.bytes_io())}")

    Proxy(server_host='minecraft_server_host', server_port=25565, proxy_port=25566, probe_cls=MyProbe).run()
