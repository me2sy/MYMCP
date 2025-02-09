# -*- coding: utf-8 -*-
"""
    status
    ~~~~~~~~~~~~~~~~~~

    Log:
         2025-02-08 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.0'


__all__ = [
    'StatusProtocols'
]

import json
from typing import IO

from mymcp.data_type import *
from mymcp.protocols import ProtocolEnum, Field, Packet


class PacketStatus(Packet):
    STATUS = ProtocolEnum.Status.STATUS

    def __repr__(self):
        _repr = ''
        _repr += f"0x{self.PACKET_ID_HEX:>02x} {self.__class__.__name__}"
        return _repr


class StatusProtocols:

    class Server2Client:

        class SCStatusResponse(PacketStatus):
            """
                Status Response packet.
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('status_response', String),
            ]

            @classmethod
            def decode(cls, bytes_io: IO) -> dict:
                return json.loads(super().decode(bytes_io)['status_response'])

        class SCStatusPongResponse(PacketStatus):
            """
                Pong Response
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('timestamp', Long)
            ]

    class Client2Server:

        class CSStatusRequest(PacketStatus):
            """
                The status can only be requested once immediately after the handshake, before any ping.
                The server won't respond otherwise.
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = []

        class CSStatusPingRequest(PacketStatus):
            """
                Ping
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('timestamp', Long)
            ]
