# -*- coding: utf-8 -*-
"""
    handshake
    ~~~~~~~~~~~~~~~~~~

    Log:
         2025-02-08 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.0'

__all__ = [
    'HandshakeProtocols'
]


from mymcp.data_type import VarInt, String, UnsignedShort
from mymcp.protocols import ProtocolEnum, Field, Packet


class PacketHandshake(Packet):
    STATUS = ProtocolEnum.Status.HANDSHAKING


class HandshakeProtocols:

    class Client2Server:

        class CSHandshake(PacketHandshake):
            """
                This packet causes the server to switch into the target state,
                it should be sent right after opening the TCP connection to avoid the server from disconnecting.
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('protocol_version', VarInt),
                Field('host', String),
                Field('port', UnsignedShort),
                Field('next_state', VarInt, enum=ProtocolEnum.HandShaking),
            ]

    class Server2Client:
        ...
