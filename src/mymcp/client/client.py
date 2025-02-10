# -*- coding: utf-8 -*-
"""
    client
    ~~~~~~~~~~~~~~~~~~
    A client For Minecraft Player
    Auto Finished Handshake/Login/Configurate

    Log:
        2025-02-10 0.1.2 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.2'

__all__ = ['Client']

import time

from loguru import logger

from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.endpoints import connectProtocol, TCP4ClientEndpoint

from mymcp.client.player import Player
from mymcp.protocols import *
from mymcp.protocols import ProtocolEnum as PE


class Client(Protocol):

    def __init__(self, player: Player):

        self.codec = Codec()
        self.status = PE.Status.HANDSHAKING

        self.player = player
        self.player.client = self

    def connectionMade(self):
        self._login()

    def _login(self):
        host = self.transport.getHost()
        logger.info(f"Connected to {host}, Start to Login")
        self.send_protocol(
            HandshakeProtocols.Client2Server.CSHandshake,
            protocol_version=769,
            host=host.host, port=host.port,
            next_state=ProtocolEnum.HandShaking.LOGIN.value
        )
        self.status = PE.Status.LOGIN
        self.send_protocol(
            LoginProtocols.Client2Server.CSLoginStart,
            name=self.player.name, uuid=self.player.local_uuid
        )

    def connectionLost(self, reason):
        logger.warning(f"Connection to {self.transport.getPeer().host} lost With {reason}")
        reactor.stop()

    def dataReceived(self, data: bytes):
        for data_packet in self.codec.decode(data):
            if data_packet is None:
                time.sleep(1 / 1000)
                continue

            if self.status == PE.Status.PLAY:
                self.player.reaction(
                    data_packet,
                    ProtocolFactory.get_proto(PE.Direction.SC, self.status, data_packet.pid)
                )
            else:
                self.prepare_to_play(data_packet)

    def prepare_to_play(self, data_packet: DataPacket):
        """
            登录过程
        :param data_packet:
        :return:
        """

        cls = ProtocolFactory.get_proto(PE.Direction.SC, self.status, data_packet.pid)

        # Login
        if self.status == ProtocolEnum.Status.LOGIN:

            if cls == LoginProtocols.Server2Client.SCLoginSetCompression:
                self.codec.compression_threshold = cls.decode(data_packet.bytes_io())['threshold']
                logger.success(f"Compression threshold set to {self.codec.compression_threshold}")
                return

            if cls == LoginProtocols.Server2Client.SCLoginSuccess:
                user_info = cls.decode(data_packet.bytes_io())
                logger.success(f"Login successful {user_info}")
                self.player.server_uuid = user_info['uuid']
                self.send_protocol(LoginProtocols.Client2Server.CSLoginAcknowledged)

                # Send Client Information
                self.send_protocol(
                    ConfigurationProtocols.Client2Server.CSConfigurationClientInformation,
                    locale='zh_cn', view_distance=12,
                    chat_mode=0, chat_colors=True, displayed_skin_parts=127,
                    main_hand=1, enable_text_filtering=True,
                    allow_server_listings=True, unknown=False
                )
                self.status = ProtocolEnum.Status.CONFIGURATION
                return

        # Configuration
        elif self.status == PE.Status.CONFIGURATION:
            if cls == ConfigurationProtocols.Server2Client.SCConfigurationPluginMessage:
                _data = cls.decode(data_packet.bytes_io())
                logger.success(f"S>C Configuration plugin message {_data}")
                self.send_protocol(
                    ConfigurationProtocols.Client2Server.CSConfigurationPluginMessage,
                    **_data
                )
                return

            elif cls == ConfigurationProtocols.Server2Client.SCConfigurationKnownPacks:
                _data = cls.decode(data_packet.bytes_io())
                logger.success(f"S>C Configuration known packs {_data}")
                self.send_protocol(
                    ConfigurationProtocols.Client2Server.CSConfigurationKnowPacks,
                    **_data
                )
                return

            elif cls == ConfigurationProtocols.Server2Client.SCConfigurationFinishConfiguration:
                logger.success(f"S>C Configuration finish configuration")
                self.send_protocol(
                    ConfigurationProtocols.Client2Server.CSLoginAcknowledgedFinishConfiguration
                )
                self.status = ProtocolEnum.Status.PLAY
                return

    def sendDataPacket(self, data_packet: DataPacket):
        self.transport.write(self.codec.encode(data_packet))

    def send_protocol(self, protocol_cls, **kwargs):
        self.sendDataPacket(protocol_cls.encode(**kwargs))

    def disconnect(self):
        self.transport.loseConnection()
        reactor.stop()

    @classmethod
    def run(cls, player: Player, server_host: str, server_port: int = 25565):
        """
            启动client
        :param player:
        :param server_host:
        :param server_port:
        :return:
        """
        connectProtocol(
            TCP4ClientEndpoint(reactor, server_host, server_port),
            cls(player)
        )
        reactor.run()
