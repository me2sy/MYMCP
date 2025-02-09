# -*- coding: utf-8 -*-
"""
    login
    ~~~~~~~~~~~~~~~~~~

    Log:
         2025-02-08 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.0'

__all__ = [
    'LoginProtocols'
]

from collections import OrderedDict
from typing import IO, Any

from mymcp.data_type import *
from mymcp.protocols import ProtocolEnum, Field, FieldsArray, Packet, DataPacket


class PacketLogin(Packet):
    STATUS = ProtocolEnum.Status.LOGIN


class LoginProtocols:

    class Server2Client:

        class SCLoginDisconnect(PacketLogin):
            """
                Disconnect
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('reason', JsonTextComponent)
            ]

        class SCLoginEncryptionRequest(PacketLogin):
            """
                Encryption Request
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('server_id', String),
                Field('public_key_length', VarInt),
                FieldsArray(
                    'public_keys',
                    [
                        Field('public_key', [Byte])
                    ],
                    'public_key_length'
                ),
                Field('verify_token_length', VarInt),
                FieldsArray(
                    'verify_tokens',
                    [
                        Field('verify_token', [Byte])
                    ],
                    'verify_token_length'
                ),
                Field('should_authenticate', Boolean)
            ]

        class SCLoginSuccess(PacketLogin):
            """
                Login Success
            """
            PACKET_ID_HEX = 0x02
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('uuid', UUID),
                Field('username', String),
                Field('num_properties', VarInt),
                FieldsArray('properties', [
                    Field('name', String),
                    Field('value', String),
                    Field('is_signed', Boolean),
                    Field('signature', String, optional_field_name='is_signed'),
                ], 'num_properties')
            ]

        class SCLoginSetCompression(PacketLogin):
            """
                Compression
            """
            PACKET_ID_HEX = 0x03
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('threshold', VarInt)
            ]

        class SCLoginPluginRequest(PacketLogin):
            """
                Used to implement a custom handshaking flow together with Login Plugin Response.
                In Notchian client, the maximum data length is 1048576 bytes.
            """
            PACKET_ID_HEX = 0x04
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                res = OrderedDict()
                res['message_id'] = VarInt.decode(bytes_io)
                res['channel'] = Identifier.decode(bytes_io)
                bs = bytes()
                while True:
                    _ = bytes_io.read(1)
                    if _ == b'':
                        break
                    else:
                        bs += _
                res['data'] = bs
                return res

        class SCLoginCookieRequest(PacketLogin):
            """
                Requests a cookie that was previously stored.
            """
            PACKET_ID_HEX = 0x05
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('key', Identifier)
            ]

    class Client2Server:

        class CSLoginStart(PacketLogin):
            """
                Login Start
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('name', String),
                Field('uuid', UUID),
            ]

        class CSEncryptionResponse(PacketLogin):
            """
                Encryption Response
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('shared_secret_length', VarInt),
                FieldsArray(
                    'shared_secret',
                    [Field('secret', Byte)],
                    'shared_secret_length'
                ),
                Field('verify_token_length', VarInt),
                FieldsArray(
                    'verify_tokens',
                    [Field('verify_token', [Byte])],
                    'verify_token_length'
                )
            ]

        class CSLoginPluginResponse(PacketLogin):
            """
                Plugin Response
            """
            PACKET_ID_HEX = 0x02
            DIRECT = ProtocolEnum.Direction.CS

            @classmethod
            def encode(cls, **kwargs) -> DataPacket:
                res = bytes()
                res += VarInt.encode(kwargs['message_id'])
                res += Boolean.encode(kwargs['successful'])
                res += kwargs['data']
                return DataPacket(len(res), cls.PACKET_ID_HEX, res)

        class CSLoginAcknowledged(PacketLogin):
            """
                Login Acknowledged
            """
            PACKET_ID_HEX = 0x03
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = []

        class CSLoginCookieResponse(PacketLogin):
            """
                Response to a Cookie Request (login) from the server.
                The Notchian server only accepts responses of up to 5 kiB in size.
                # TODO
            """
            PACKET_ID_HEX = 0x04
            DIRECT = ProtocolEnum.Direction.CS

            @classmethod
            def encode(cls, values: dict) -> bytes:
                raise NotImplementedError
