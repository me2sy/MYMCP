# -*- coding: utf-8 -*-
"""
    configuration
    ~~~~~~~~~~~~~~~~~~

    Log:
         2025-02-08 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.0'

__all__ = [
    'ConfigurationProtocols'
]

from collections import OrderedDict
from typing import IO, Any

from mymcp.data_type import *
from mymcp.protocols import ProtocolEnum, Field, FieldsArray, Packet, DataPacket


class PacketConfiguration(Packet):
    STATUS = ProtocolEnum.Status.CONFIGURATION


class ConfigurationProtocols:

    class Server2Client:

        class SCConfigurationCookieRequest(PacketConfiguration):
            """
                Requests a cookie that was previously stored.
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('key', Identifier)
            ]

        class SCConfigurationPluginMessage(PacketConfiguration):
            """
                Configuration Plugin Message
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('channel', Identifier),
                Field('data', String),
            ]

            # @classmethod
            # def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
            #     result = OrderedDict()
            #     result['channel'] = Identifier.decode(bytes_io)
            #     result['data'] = bytes_io.read()
            #     return result

        class SCConfigurationDisconnect(PacketConfiguration):
            """
                Disconnect
            """
            PACKET_ID_HEX = 0x02
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('reason', TextComponent)
            ]

        class SCConfigurationFinishConfiguration(PacketConfiguration):
            """
                Sent by the server to notify the client that the configuration process has finished.
                The client answers with Acknowledge Finish Configuration whenever it is ready to continue.
            """
            PACKET_ID_HEX = 0x03
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = []

        class SCConfigurationKeepAlive(PacketConfiguration):
            """
                The server will frequently send out a keep-alive (see Clientbound Keep Alive),
                each containing a random ID.
                The client must respond with the same packet.
            """
            PACKET_ID_HEX = 0x04
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('keep_alive_id', Long),
            ]

        class SCConfigurationPing(PacketConfiguration):
            """
                Packet is not used by the Notchian server.
                When sent to the client, client responds with a Pong packet with the same id.
            """
            PACKET_ID_HEX = 0x05
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('id', Int),
            ]

        class SCConfigurationResetChat(PacketConfiguration):
            """
                Reset Chat
            """
            PACKET_ID_HEX = 0x06
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = []

        class SCConfigurationRegistryData(PacketConfiguration):
            """
                Represents certain registries that are sent from the server and are applied on the client.
                https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Registry_Data
            """
            PACKET_ID_HEX = 0x07
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('registry_id', Identifier),
                Field('entry_count', VarInt),
                FieldsArray(
                    'entries',
                    [
                        Field('entry_id', Identifier),
                        Field('has_data', Boolean),
                        Field('data', NBT, optional_field_name='has_data'),
                    ],
                    'entry_count'
                )
            ]

        class SCConfigurationRemoveResourcePack(PacketConfiguration):
            """
                Remove Resource Pack
            """
            PACKET_ID_HEX = 0x08
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('has_uuid', Boolean),
                Field('uuid', UUID, optional_field_name='has_uuid'),
            ]

        class SCConfigurationAddResourcePack(PacketConfiguration):
            """
                Add Resource Pack
            """
            PACKET_ID_HEX = 0x09
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('uuid', UUID),
                Field('url', String),
                Field('hash', String),
                Field('forced', Boolean),
                Field('has_prompt_message', Boolean),
                Field('prompt_message', TextComponent, optional_field_name='has_prompt_message'),
            ]

        class SCConfigurationStoreCookie(PacketConfiguration):
            """
                Stores some arbitrary data on the client, which persists between server transfers.
                The Notchian client only accepts cookies of up to 5 kiB in size.
            """
            PACKET_ID_HEX = 0x0A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('key', Identifier),
                Field('payload_length', VarInt),
                FieldsArray(
                    'payload',
                    [
                        Field('payload_bytes', Byte),
                    ],
                    'payload_length'
                )
            ]

        class SCConfigurationTransfer(PacketConfiguration):
            """
                Notifies the client that it should transfer to the given server.
                Cookies previously stored are preserved between server transfers.
            """
            PACKET_ID_HEX = 0x0B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('host', String),
                Field('port', VarInt),
            ]

        class SCConfigurationFeatureFlags(PacketConfiguration):
            """
                Used to enable and disable features, generally experimental ones, on the client.
            """
            PACKET_ID_HEX = 0x0C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('total_features', VarInt),
                FieldsArray(
                    'feature_flags',
                    [
                        Field('flags', Identifier),
                    ],
                    'total_features'
                )
            ]

        class SCConfigurationUpdateTags(PacketConfiguration):
            """
                Update Tags
            """
            PACKET_ID_HEX = 0x0D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('length_of_the_array', VarInt),
                FieldsArray(
                    'array_of_tags',
                    [
                        Field('registry', Identifier),
                        Field('length', VarInt),
                        FieldsArray(
                            'tags',
                            [
                                Field('tag_name', Identifier),
                                Field('count', VarInt),
                                FieldsArray(
                                    'entries',
                                    [
                                        Field('entry', VarInt)
                                    ],
                                    'count'
                                )
                            ],
                            'length'
                        )
                    ],
                    'length_of_the_array'
                )
            ]

        class SCConfigurationKnownPacks(PacketConfiguration):
            """
                Informs the client of which data packs are present on the server.
                The client is expected to respond with its own Serverbound Known Packs packet.
                The Notchian server does not continue with Configuration until it receives a response.
                The Notchian client requires the minecraft:core pack with version 1.21 for a normal login sequence.
                This packet must be sent before the Registry Data packets.
            """
            PACKET_ID_HEX = 0x0E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('known_pack_count', VarInt),
                FieldsArray(
                    'known_packs',
                    [
                        Field('namespace', String),
                        Field('_id', String),
                        Field('version', String),
                    ],
                    'known_pack_count'
                )
            ]

        class SCConfigurationCustomReportDetails(PacketConfiguration):
            """
                Contains a list of key-value text entries that are included in any crash
                or disconnection report generated during connection to the server.
            """
            PACKET_ID_HEX = 0x0F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('details_count', VarInt),
                FieldsArray(
                    'details',
                    [
                        Field('title', String),
                        Field('description', String),
                    ],
                    'details_count'
                )
            ]

        class SCConfigurationServerLinks(PacketConfiguration):
            """
                This packet contains a list of links that the Notchian client will display
                in the menu available from the pause menu.
                Link labels can be built-in or custom (i.e., any text).
            """
            PACKET_ID_HEX = 0x10
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['links_count'] = VarInt.decode(bytes_io)

                links = []

                for _ in range(result['links_count']):
                    link = dict(is_built_in=Boolean.decode(bytes_io))
                    link['label'] = VarInt.decode(bytes_io) if link['is_built_in'] else TextComponent.decode(bytes_io)
                    link['url'] = String.decode(bytes_io)
                    links.append(link)

                result['links'] = links
                return result

    class Client2Server:

        class CSConfigurationClientInformation(PacketConfiguration):
            """
                Configuration Client Information
                Sent when the player connects, or when settings are changed.
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('locale', String),
                Field('view_distance', Byte),
                Field('chat_mode', VarInt),
                Field('chat_colors', Boolean),
                Field('displayed_skin_parts', UnsignedByte),
                Field('main_hand', VarInt),
                Field('enable_text_filtering', Boolean),
                Field('allow_server_listings', Boolean),
                Field('unknown', Boolean)
            ]

        class CSConfigurationCookieResponse(PacketConfiguration):
            """
                Response to a Cookie Request (configuration) from the server.
                The Notchian server only accepts responses of up to 5 kiB in size.
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('key', Identifier),
                Field('has_payload', Boolean),
                Field('payload_length', VarInt, optional_field_name='has_payload'),
                FieldsArray(
                    'payload',
                    [
                        Field('payload_bytes', Byte),
                    ],
                    'payload_length',
                    optional_field_name='has_payload'
                )
            ]

            @classmethod
            def encode(cls, values: dict) -> bytes:
                raise NotImplementedError

        class CSConfigurationPluginMessage(PacketConfiguration):
            """
                Configuration Plugin Message
            """
            PACKET_ID_HEX = 0x02
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('channel', Identifier),
                Field('data', String),
            ]

        class CSLoginAcknowledgedFinishConfiguration(PacketConfiguration):
            """
                Sent by the client to notify the server that the configuration process has finished.
                It is sent in response to the server's Finish Configuration.
            """
            PACKET_ID_HEX = 0x03
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = []

        class CSConfigurationKeepAlive(PacketConfiguration):
            """
                The server will frequently send out a keep-alive (see Clientbound Keep Alive),
                each containing a random ID. The client must respond with the same packet.
            """
            PACKET_ID_HEX = 0x04
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('keep_alive_id', Long),
            ]

        class CSConfigurationPong(PacketConfiguration):
            """
                Response to the clientbound packet (Ping) with the same id.
            """
            PACKET_ID_HEX = 0x05
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('id', Int),
            ]

        class CSConfigurationResourcePackResponse(PacketConfiguration):
            """
                Resource Pack Response
                Result can be one of the following values:
                ID	Result
                0	Successfully downloaded
                1	Declined
                2	Failed to download
                3	Accepted
                4	Downloaded
                5	Invalid URL
                6	Failed to reload
                7	Discarded
            """
            PACKET_ID_HEX = 0x06
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('uuid', UUID),
                Field('result', VarInt),
            ]

        class CSConfigurationKnowPacks(PacketConfiguration):
            """
                Informs the server of which data packs are present on the client.
                The client sends this in response to Clientbound Known Packs.
                If the client specifies a pack in this packet,
                the server should omit its contained data from the Registry Data packet.
            """
            PACKET_ID_HEX = 0x07
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('known_pack_count', VarInt),
                FieldsArray(
                    'known_packs',
                    [
                        Field('namespace', String),
                        Field('_id', String),
                        Field('version', String),
                    ],
                    'known_pack_count'
                )
            ]

            @classmethod
            def encode(cls, **kwargs) -> DataPacket:
                bs = VarInt.encode(kwargs['known_pack_count'])
                for _ in kwargs['known_packs']:
                    bs += String.encode(_['namespace'])
                    bs += String.encode(_['_id'])
                    bs += String.encode(_['version'])
                return DataPacket(len(bs), cls.PACKET_ID_HEX, bs)
