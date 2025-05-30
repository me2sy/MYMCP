# -*- coding: utf-8 -*-
"""
    v769
    ~~~~~~~~~~~~~~~~~~
    Packets for V769
    More Details see https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Protocol?oldid=2938097

    Log:
        2025-05-29 0.2.0 Me2sY  重构，完成全部 Protocol 编码/解码

        2025-05-23 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = ['PacketsV769', 'PacketFactoryV769']

import datetime
import json
from dataclasses import dataclass
from io import BytesIO
from typing import Optional, IO, Self, ClassVar, Union

from mymcp.data_types import *
from mymcp.data_types.entity import EntityMetadata
from mymcp.data_types.protocol import AdvancementMapping, ProgressMapping, OptionalSignature256, Trade
from mymcp.data_types.slot import Slot, RecipeDisplay, SlotDisplay
from mymcp.data_types.particle import Particle
from mymcp.data_types.nbt import TagCompound
from mymcp.data_types.chunk import ChunkData, LightData
from mymcp.packets import Packet
from mymcp.packets.enums import V769 as ENUMS


class PacketsV769:

    # Handshaking
    # ------------------------------------------------------------------------------------------------------

    @dataclass(slots=True)
    class HSIntention(Packet):
        """
            This packet causes the server to switch into the target state,
            it should be sent right after opening the TCP connection to avoid the server from disconnecting.
        """
        RESOURCE = 'intention'
        STATUS = ENUMS.Status.HANDSHAKING
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x00

        protocol_version: Field | VarInt
        host: Field | String
        port: Field | UnsignedShort
        next_state: Field | VarInt


    # Status
    # ------------------------------------------------------------------------------------------------------

    @dataclass(slots=True)
    class SCStatusResponse(Packet):
        """
            Status Response packet.
        """
        RESOURCE = 'status_response'
        STATUS = ENUMS.Status.STATUS
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x00

        status_response: Field | String

        @property
        def status(self) -> dict:
            """
                返回 status
            :return:
            """
            return json.loads(self.status_response.value)


    @dataclass(slots=True)
    class SCPongResponse(Packet):
        """
            Pong Response
        """
        RESOURCE = 'pong_response'
        STATUS = ENUMS.Status.STATUS
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x01

        timestamp: Field | Long


    @dataclass(slots=True)
    class SSStatusRequest(Packet):
        """
            The status can only be requested once immediately after the handshake, before any ping.
            The server won't respond otherwise.
        """
        RESOURCE = 'status_request'
        STATUS = ENUMS.Status.STATUS
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x00


    @dataclass(slots=True)
    class SSPingRequest(Packet):
        """
            Ping
        """
        RESOURCE = 'ping_request'
        STATUS = ENUMS.Status.STATUS
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x01

        timestamp: Field | Long


    # Login Status
    # ------------------------------------------------------------------------------------------------------

    @dataclass(slots=True)
    class LCLoginDisconnect(Packet):
        """
            Disconnect
        """
        RESOURCE = 'login_disconnect'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x00

        reason: Field | JsonTextComponent


    @dataclass(slots=True)
    class LCHello(Packet):
        """
            Encryption Request
        """
        RESOURCE = 'hello'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x01

        server_id: Field | String
        public_key: Field | list[Byte]
        verify_tokens: Field | list[Byte]
        should_authenticate: Field | Boolean


    @dataclass(slots=True)
    class LCLoginFinished(Packet):
        """
            Login Success
        """

        @dataclass(slots=True)
        class Property(Combined):
            name: Field | String
            value: Field | String
            signature: Field | OptionalString

        RESOURCE = 'login_finished'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x02

        uuid: Field | UUID
        username: Field | String
        property: Field | list[Property]


    @dataclass(slots=True)
    class LCLoginCompression(Packet):
        """
            Compression
        """
        RESOURCE = 'login_compression'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x03

        threshold: Field | VarInt


    @dataclass(slots=True)
    class LCCustomQuery(Packet):
        """
            Used to implement a custom handshaking flow together with Login Plugin Response.
            In Notchian client, the maximum data length is 1048576 bytes.
        """
        RESOURCE = 'custom_query'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x04

        message_id: Field | VarInt
        channel: Field | Identifier
        data: Field | list[Byte]

        @classmethod
        def decode(cls, data_packet: DataPacket) -> Self:
            data_io = data_packet.bytes_io()
            message_id = VarInt.decode(data_io)
            channel = Identifier.decode(data_io)
            data = []
            while True:
                _ = data_io.read(1)
                if _ == b'':
                    break
                else:
                    data.append(Byte.decode_bytes(_))
            return cls(message_id=message_id, channel=channel, data=data)

        def __bytes__(self) -> bytes:
            return self.message_id.bytes + self.channel.bytes + b''.join(_.bytes for _ in self.data)


    @dataclass(slots=True)
    class LCCookieRequest(Packet):
        """
            Requests a cookie that was previously stored.
        """
        RESOURCE = 'cookie_request'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x05

        key: Field | Identifier


    @dataclass(slots=True)
    class LSHello(Packet):
        """
            Login Start
        """
        RESOURCE = 'hello'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x00

        name: Field | String
        uuid: Field | UUID


    @dataclass(slots=True)
    class LSKey(Packet):
        """
            Encryption Response
        """
        RESOURCE = 'key'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x01

        shared_secret: Field | list[Byte]
        verify_tokens: Field | list[Byte]


    @dataclass(slots=True)
    class LSCustomQueryAnswer(Packet):
        """
            Plugin Response
        """
        RESOURCE = 'custom_query_answer'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x02

        message_id: Field | VarInt
        data: Field | list[Byte]

        @classmethod
        def decode(cls, data_packet: DataPacket) -> Self:
            data_io = data_packet.bytes_io()
            message_id = VarInt.decode(data_io)
            data = []
            while True:
                _ = data_io.read(1)
                if _ == b'':
                    break
                else:
                    data.append(Byte.decode_bytes(_))

            return cls(message_id=message_id, data=data)

        def __bytes__(self) -> bytes:
            return self.message_id.bytes + b''.join(_.bytes for _ in self.data)


    @dataclass(slots=True)
    class LSLoginAcknowledged(Packet):
        """
            Login Acknowledged
        """
        RESOURCE = 'login_acknowledged'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x03


    @dataclass(slots=True)
    class LSCookieResponse(Packet):
        """
            Response to a Cookie Request (login) from the server.
            The Notchian server only accepts responses of up to 5 kiB in size.
        """
        RESOURCE = 'cookie_response'
        STATUS = ENUMS.Status.LOGIN
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x04

        key: Field | Identifier
        value: Field | Optional[list[Byte]] = None

        def __bytes__(self) -> bytes:
            return self.key.bytes + Boolean.TRUE + self.list_to_bytes(self.value) if self.value else Boolean.FALSE

        @classmethod
        def decode(cls, data_packet: DataPacket) -> Self:
            data_io = data_packet.bytes_io()
            key = Identifier.decode(data_io)
            has_data = Boolean.decode(data_io)
            if has_data:
                value = cls.bytes_to_list(data_io, Byte)[1]
            else:
                value = None
            return cls(key=key, value=value)

    # Configurate
    # ------------------------------------------------------------------------------------------------------

    @dataclass(slots=True)
    class CCCookieRequest(Packet):
        """
            Requests a cookie that was previously stored.
        """
        RESOURCE = 'cookie_request'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x00

        key: Field | Identifier


    @dataclass(slots=True)
    class CCCustomPayload(Packet):
        """
            Configuration Plugin Message
        """
        RESOURCE = 'custom_payload'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x01

        channel: Field | Identifier
        data: Field | list[Byte]

        @classmethod
        def decode(cls, data_packet: DataPacket) -> Self:
            data_io = data_packet.bytes_io()
            channel = Identifier.decode(data_io)
            data = []
            while True:
                _ = data_io.read(1)
                if _ == b'':
                    break
                else:
                    data.append(Byte.decode_bytes(_))
            return cls(channel=channel, data=data)

        def __bytes__(self) -> bytes:
            return self.channel.bytes + b''.join(_.bytes for _ in self.data)


    @dataclass(slots=True)
    class CCDisconnect(Packet):
        """
            Disconnect
        """
        RESOURCE = 'disconnect'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x02

        reason: Field | TextComponent


    @dataclass(slots=True)
    class CCFinishConfiguration(Packet):
        """
            Sent by the server to notify the client that the configuration process has finished.
            The client answers with Acknowledge Finish Configuration whenever it is ready to continue.
        """
        RESOURCE = 'finish_configuration'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x03


    @dataclass(slots=True)
    class CCKeepAlive(Packet):
        """
            The server will frequently send out a keep-alive (see Clientbound Keep Alive),
            each containing a random ID.
            The client must respond with the same packet.
        """
        RESOURCE = 'keep_alive'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x04

        keep_alive_id: Field | Long

        @classmethod
        def one(cls) -> Self:
            return cls(keep_alive_id=Long(int(datetime.datetime.now().timestamp() * 1_000_000)))


    @dataclass(slots=True)
    class CCPing(Packet):
        """
            Packet is not used by the Notchian server.
            When sent to the client, client responds with a Pong packet with the same id.
        """
        RESOURCE = 'ping'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x05

        id_: Field | Int


    @dataclass(slots=True)
    class CCResetChat(Packet):
        """
            Reset Chat
        """
        RESOURCE = 'reset_chat'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x06


    @dataclass(slots=True)
    class CCRegistryData(Packet):
        """
            Represents certain registries that are sent from the server and are applied on the client.
            https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Registry_Data
        """
        @dataclass(slots=True)
        class Entity(Combined):
            entry_id: Field | Identifier
            data: Field | OptionalNBT

        RESOURCE = 'registry_data'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x07

        registry_id: Field | Identifier
        entries: Field | list[Entity]


    @dataclass(slots=True)
    class CCResourcePackPop(Packet):
        """
            Remove Resource Pack
        """
        RESOURCE = 'resource_pack_pop'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x08

        uuid: Field | OptionalUUID


    @dataclass(slots=True)
    class CCResourcePackPush(Packet):
        """
            Add Resource Pack
        """
        RESOURCE = 'resource_pack_push'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x09

        uuid: Field | UUID
        url: Field | String
        hash: Field | String
        forced: Field | Boolean
        prompt_message: Field | OptionalTextComponent


    @dataclass(slots=True)
    class CCStoreCookie(Packet):
        """
            Stores some arbitrary data on the client, which persists between server transfers.
            The Notchian client only accepts cookies of up to 5 kiB in size.
        """
        RESOURCE = 'store_cookie'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0A

        key: Field | Identifier
        payload: Field | list[Byte]


    @dataclass(slots=True)
    class CCTransfer(Packet):
        """
            Notifies the client that it should transfer to the given server.
            Cookies previously stored are preserved between server transfers.
        """
        RESOURCE = 'transfer'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0B

        host: Field | String
        port: Field | VarInt


    @dataclass(slots=True)
    class CCUpdateEnabledFeatures(Packet):
        """
            Used to enable and disable features, generally experimental ones, on the client.
        """
        RESOURCE = 'update_enabled_features'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0C

        feature_flags: Field | list[Identifier]


    @dataclass(slots=True)
    class CCUpdateTags(Packet):
        """
            Update Tags
        """
        @dataclass(slots=True)
        class Tags(Combined):

            @dataclass(slots=True)
            class Tag(Combined):
                tag_name: Field | Identifier
                entries: Field | list[VarInt]

            registry: Field | Identifier
            tags: Field | list[Tag]

        RESOURCE = 'update_tags'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0D

        tags: Field | list[Tags]


    @dataclass(slots=True)
    class CCSelectKnownPacks(Packet):
        """
            Informs the client of which data packs are present on the server.
            The client is expected to respond with its own Serverbound Known Packs packet.
            The Notchian server does not continue with Configuration until it receives a response.
            The Notchian client requires the minecraft:core pack with version 1.21 for a normal login sequence.
            This packet must be sent before the Registry Data packets.
        """

        @dataclass(slots=True)
        class KnownPackets(Combined):
            namespace: Field | String
            id_: Field | String
            version: Field | String

        RESOURCE = 'select_known_packs'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0E

        known_packs: Field | list[KnownPackets]


    @dataclass(slots=True)
    class CCCustomReportDetails(Packet):
        """
            Contains a list of key-value text entries that are included in any crash
            or disconnection report generated during connection to the server.
        """

        @dataclass(slots=True)
        class Detail(Combined):
            title: Field | String
            description: Field | String

        RESOURCE = 'custom_report_details'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0F

        details: Field | list[Detail]


    @dataclass(slots=True)
    class CCServerLinks(Packet):
        """
            This packet contains a list of links that the Notchian client will display
            in the menu available from the pause menu.
            Link labels can be built-in or custom (i.e., any text).
        """
        @dataclass(slots=True)
        class Link(Combined):
            is_built_in: Field | Boolean
            label: Field | Union[VarInt, TextComponent]
            url: Field | String

            def __bytes__(self) -> bytes:
                return self.is_built_in.bytes + self.label.bytes + self.url.bytes

            @classmethod
            def decode(cls, bytes_source: BytesIO) -> Self:
                is_built_in = Boolean.decode(bytes_source)
                if is_built_in:
                    label = VarInt.decode(bytes_source)
                else:
                    label = TextComponent.decode(bytes_source)
                url = String.decode(bytes_source)
                return cls(is_built_in=is_built_in, label=label, url=url)

        RESOURCE = 'server_links'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x10

        links: Field | list[Link]


    @dataclass(slots=True)
    class CSClientInformation(Packet):
        """
            Configuration Client Information
            Sent when the player connects, or when settings are changed.
        """
        RESOURCE = 'client_information'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x00

        locale: Field | String
        view_distance: Field | Byte
        chat_mode: Field | VarInt
        chat_colors: Field | Boolean
        displayed_skin_parts: Field | UnsignedByte
        main_hand: Field | VarInt
        enable_text_filtering: Field | Boolean
        allow_server_listings: Field | Boolean
        particle_status: Field | VarInt


    @dataclass(slots=True)
    class CSCookieResponse(Packet):
        """
            Response to a Cookie Request (configuration) from the server.
            The Notchian server only accepts responses of up to 5 kiB in size.
        """
        RESOURCE = 'cookie_response'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x01

        key: Field | Identifier
        payload: Field | Optional[list[Byte]] = None

        def __bytes__(self) -> bytes:
            return self.key.bytes + (
                Boolean.TRUE + b''.join(_.bytes for _ in self.payload) if self.payload else Boolean.FALSE
            )

        @classmethod
        def decode(cls, bytes_source: BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)

            key = Identifier.decode(bytes_io)
            payload = None
            if Boolean.decode(bytes_io):
                payload = [Byte.decode(bytes_io) for _ in range(VarInt.decode(bytes_io).value)]

            return cls(key=key, payload=payload)


    @dataclass(slots=True)
    class CSCustomPayload(Packet):
        """
            Configuration Plugin Message
        """
        RESOURCE = 'custom_payload'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x02

        channel: Field | Identifier
        data: Field | String


    @dataclass(slots=True)
    class CSFinishConfiguration(Packet):
        """
            Sent by the client to notify the server that the configuration process has finished.
            It is sent in response to the server's Finish Configuration.
        """
        RESOURCE = 'finish_configuration'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x03


    @dataclass(slots=True)
    class CSKeepAlive(Packet):
        """
            The server will frequently send out a keep-alive (see Clientbound Keep Alive),
            each containing a random ID. The client must respond with the same packet.
        """
        RESOURCE = 'keep_alive'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x04

        keep_alive_id: Field | Long


    @dataclass(slots=True)
    class CSPong(Packet):
        """
            Response to the clientbound packet (Ping) with the same id.
        """
        RESOURCE = 'pong'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x05

        id_: Field | Int


    @dataclass(slots=True)
    class CSResourcePack(Packet):
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
        RESOURCE = 'resource_pack'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x06

        uuid: Field | UUID
        result: Field | VarInt


    @dataclass(slots=True)
    class CSSelectKnownPacks(Packet):
        """
            Informs the server of which data packs are present on the client.
            The client sends this in response to Clientbound Known Packs.
            If the client specifies a pack in this packet,
            the server should omit its contained data from the Registry Data packet.
        """

        @dataclass(slots=True)
        class KnownPacket(Combined):
            namespace: Field | String
            id_: Field | String
            version: Field | String

        RESOURCE = 'select_known_packs'
        STATUS = ENUMS.Status.CONFIGURATION
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x07

        known_packs: Field | list[KnownPacket]


    # Play
    # ------------------------------------------------------------------------------------------------------
    @dataclass(slots=True)
    class PCBundleDelimiter(Packet):
        """
            The delimiter for a bundle of packets.
            When received, the client should store every subsequent packet it receives,
            and wait until another delimiter is received.
            Once that happens, the client is guaranteed to process every packet in the bundle on the same tick,
            and the client should stop storing packets.
        """
        RESOURCE = 'bundle_delimiter'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x00


    @dataclass(slots=True)
    class PCAddEntity(Packet):
        """
            Sent by the server when an entity (aside from Experience Orb) is created.
        """
        RESOURCE = 'add_entity'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x01

        entity_id: Field | VarInt
        entity_uuid: Field | UUID

        # ID in the minecraft:entity_type registry (see "type" field in Entity metadata#Entities).
        # https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Entity_metadata#Entities
        _type: Field | VarInt
        x: Field | Double
        y: Field | Double
        z: Field | Double

        # To get the real pitch, you must divide this by (256.0F / 360.0F)
        pitch: Field | Angle

        # To get the real yaw, you must divide this by (256.0F / 360.0F)
        yaw: Field | Angle

        # Only used by living entities, where the head of the entity may differ from the general body rotation.
        head_yaw: Field | Angle

        # Meaning dependent on the value of the Type field, see Object Data for details.
        # https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Object_Data
        data: Field | VarInt

        velocity_x: Field | Short
        velocity_y: Field | Short
        velocity_z: Field | Short


    @dataclass(slots=True)
    class PCAddExperienceOrb(Packet):
        """
            Spawns one or more experience orbs.
        """
        RESOURCE = 'add_experience_orb'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x02

        entity_id: Field | VarInt
        x: Field | Double
        y: Field | Double
        z: Field | Double
        count: Field | Short


    @dataclass(slots=True)
    class PCAnimate(Packet):
        """
            Sent whenever an entity should change animation.
            Animation can be one of the following values:
            ID	Animation
            0	Swing main arm
            2	Leave bed
            3	Swing offhand
            4	Critical effect
            5	Magic critical effect
        """
        RESOURCE = 'animate'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x03

        entity_id: Field | VarInt
        animation: Field | UnsignedByte


    @dataclass(slots=True)
    class PCAwardStats(Packet):
        """
            Sent as a response to Client Status (id 1).
            Will only send the changed values if previously requested.
        """
        @dataclass(slots=True)
        class Statistic(Combined):
            category_id: Field | VarInt
            statistic_id: Field | VarInt
            value: Field | VarInt

        RESOURCE = 'award_stats'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x04

        statistic: Field | list[Statistic]


    @dataclass(slots=True)
    class PCBlockChangedAck(Packet):
        """
            Acknowledges a user-initiated block change.
            After receiving this packet,
            the client will display the block state sent by the server instead of the one predicted by the client.
        """
        RESOURCE = 'block_changed_ack'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x05

        sequence_id: Field | VarInt


    @dataclass(slots=True)
    class PCBlockDestruction(Packet):
        """
            0–9 are the displayable destroy stages and each other number means that
            there is no animation on this coordinate.
        """
        RESOURCE = 'block_destruction'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x06

        entity_id: Field | VarInt
        location: Field | Position
        destroy_stage: Field | Byte


    @dataclass(slots=True)
    class PCBlockEntityData(Packet):
        """
            Sets the block entity associated with the block at the given location.
        """
        RESOURCE = 'block_entity_data'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x07

        location: Field | Position
        type_: Field | VarInt
        nbt_data: Field | NBT


    @dataclass(slots=True)
    class PCBlockEvent(Packet):
        """
            This packet is used for a number of actions and animations performed by blocks,
            usually non-persistent.
            The client ignores the provided block type and instead uses the block state in their world.
        """
        RESOURCE = 'block_event'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x08

        location: Field | Position
        action_id: Field | UnsignedByte
        action_parameter: Field | UnsignedByte
        block_type: Field | VarInt


    @dataclass(slots=True)
    class PCBlockUpdate(Packet):
        """
            Fired whenever a block is changed within the render distance.
        """
        RESOURCE = 'block_update'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x09

        location: Field | Position
        block_id: Field | VarInt


    @dataclass(slots=True)
    class PCBossEvent(Packet):
        """
            Boss Bar
        """
        @dataclass(slots=True)
        class Action(Combined):
            action: Field | VarInt
            action_data: Field | tuple

            def __bytes__(self) -> bytes:
                return self.action.bytes + b''.join(_.bytes for _ in self.action_data)

            @classmethod
            def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
                action = VarInt.decode(bytes_io)
                actions = []
                if action.value == ENUMS.BossBarAction.ADD:
                    actions.append(TextComponent.decode(bytes_io))
                    actions.append(Float.decode(bytes_io))
                    actions.append(VarInt.decode(bytes_io))
                    actions.append(VarInt.decode(bytes_io))
                    actions.append(UnsignedByte.decode(bytes_io))
                elif action.value == ENUMS.BossBarAction.UPDATE_HEALTH:
                    actions.append(Float.decode(bytes_io))
                elif action.value == ENUMS.BossBarAction.UPDATE_TITLE:
                    actions.append(TextComponent.decode(bytes_io))
                elif action.value == ENUMS.BossBarAction.UPDATE_STYLE:
                    actions.append(VarInt.decode(bytes_io))
                    actions.append(VarInt.decode(bytes_io))
                elif action.value == ENUMS.BossBarAction.UPDATE_FLAGS:
                    actions.append(UnsignedByte.decode(bytes_io))
                return cls(action=action, action_data=tuple(actions))

        RESOURCE = 'boss_event'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0A

        uuid: Field | UUID
        action: Field | Action


    @dataclass(slots=True)
    class PCChangeDifficulty(Packet):
        """
            Changes the difficulty setting in the client's option menu
        """
        RESOURCE = 'change_difficulty'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0B

        difficulty: Field | UnsignedByte
        difficulty_locked: Field | Boolean


    @dataclass(slots=True)
    class PCChunkBatchFinished(Packet):
        """
            Marks the end of a chunk batch.
        """
        RESOURCE = 'chunk_batch_finished'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0C
        batch_size: Field | VarInt


    @dataclass(slots=True)
    class PCChunkBatchStart(Packet):
        """
            Marks the start of a chunk batch.
            The Notchian client marks and stores the time it receives this packet.
        """
        RESOURCE = 'chunk_batch_start'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0D


    @dataclass(slots=True)
    class PCChunksBiomes(Packet):
        """
            Chunk Biomes
            The order of X and Z is inverted, because the client reads them as one big-endian Long,
            with Z being the upper 32 bits.
        """

        @dataclass(slots=True)
        class ChunkBiomeData(Combined):
            chunk_z: Field | Int
            chunk_x: Field | Int
            data: Field | list[Byte]

        RESOURCE = 'chunks_biomes'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0E

        chunk_biome_data: Field | ChunkBiomeData


    @dataclass(slots=True)
    class PCClearTitles(Packet):
        """
            Clear the client's current title information, with the option to also reset it.
        """
        RESOURCE = 'clear_titles'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x0F

        reset: Field | Boolean


    @dataclass(slots=True)
    class PCCommandSuggestions(Packet):
        """
            The server responds with a list of auto-completions of the last word sent to it.
            In the case of regular chat, this is a player username.
            Command names and parameters are also supported.
            The client sorts these alphabetically before listing them.
        """
        @dataclass(slots=True)
        class Match(Combined):
            match: Field | String
            tooltip: Field | OptionalTextComponent

        RESOURCE = 'command_suggestions'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x10

        id_: Field | VarInt
        start: Field | VarInt
        length: Field | VarInt
        matches: Field | list[Match]


    @dataclass(slots=True)
    class PCCommands(Packet):
        """
            Lists all the commands on the server, and how they are parsed.
            This is a directed graph, with one root node.
            Each redirect or child node must refer only to nodes that have already been declared.
        """
        RESOURCE = 'commands'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x11

        nodes: Field | list[Node]
        root_index: Field | VarInt


    @dataclass(slots=True)
    class PCContainerClose(Packet):
        """
            This packet is sent from the server to the client when a window is forcibly closed,
            such as when a chest is destroyed while it's open.
            The Notchian client disregards the provided window ID and closes any active window.
        """
        RESOURCE = 'container_close'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x12

        window_id: Field | UnsignedByte


    @dataclass(slots=True)
    class PCContainerSetContent(Packet):
        """
            Replaces the contents of a container window.
            Sent by the server upon initialization of a container window or the player's inventory,
            and in response to state ID mismatches (see #Click Container).
        """
        RESOURCE = 'container_set_content'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x13

        window_id: Field | UnsignedByte
        state_id: Field | VarInt
        slot_data: Field | list[Slot]
        carried_item: Field | Slot


    @dataclass(slots=True)
    class PCContainerSetData(Packet):
        """
            This packet is used to inform the client that part of a GUI window should be updated.
        """
        RESOURCE = 'container_set_data'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x14

        window_id: Field | UnsignedByte
        property: Field | Short
        value: Field | Short


    @dataclass(slots=True)
    class PCContainerSetSlot(Packet):
        """
            Sent by the server when an item in a slot (in a window) is added/removed.
        """
        RESOURCE = 'container_set_slot'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x15

        window_id: Field | Byte
        state_id: Field | VarInt
        slot: Field | Short
        slot_data: Field | Slot


    @dataclass(slots=True)
    class PCCookieRequest(Packet):
        """
            Requests a cookie that was previously stored.
        """
        RESOURCE = 'cookie_request'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x16

        key: Field | Identifier


    @dataclass(slots=True)
    class PCCooldown(Packet):
        """
            Applies a cooldown period to all items with the given type.
        """
        RESOURCE = 'cooldown'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x17

        item_id: Field | VarInt
        cooldown_ticks: Field | VarInt


    @dataclass(slots=True)
    class PCCustomChatCompletions(Packet):
        """
            Unused by the Notchian server.
            Likely provided for custom servers to send chat message completions to clients.
        """
        RESOURCE = 'custom_chat_completions'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x18

        action: Field | VarInt
        entries: Field | list[String]


    @dataclass(slots=True)
    class PCCustomPayload(Packet):
        """
            Mods and plugins can use this to send their data.
        """
        RESOURCE = 'custom_payload'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x19

        channel: Field | Identifier
        data: Field | list[Byte]

        def __bytes__(self) -> bytes:
            return self.channel.bytes + b''.join(_.bytes for _ in self.data)

        @classmethod
        def decode(cls, data_packet: DataPacket) -> Self:
            data_io = data_packet.bytes_io()
            channel = Identifier.decode(data_io)
            data = []
            while True:
                _ = data_io.read(1)
                if _ == b'':
                    break
                else:
                    data.append(Byte.decode(data_io))
            return cls(channel, data)


    @dataclass(slots=True)
    class PCDamageEvent(Packet):
        """
            Damage Event
        """
        RESOURCE = 'damage_event'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x1A

        entity_id: Field | VarInt
        source_type_id: Field | VarInt
        source_cause_id: Field | VarInt
        source_direct_id: Field | VarInt
        has_source_position: OptionalGroupField[0] | Boolean
        source_position_x: OptionalGroupField[0] | Double = None
        source_position_y: OptionalGroupField[0] | Double = None
        source_position_z: OptionalGroupField[0] | Double = None


    @dataclass(slots=True)
    class PCDebugSample(Packet):
        """
            Sample data that is sent periodically after the client has subscribed with Debug Sample Subscription.
        """
        RESOURCE = 'debug_sample'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x1B

        sample: Field | list[Long]
        sample_type: Field | VarInt


    @dataclass(slots=True)
    class PCDeleteChat(Packet):
        """
            Removes a message from the client's chat.
            This only works for messages with signatures, system messages cannot be deleted with this packet.
        """
        RESOURCE = 'delete_chat'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x1C

        message_id: Field | VarInt
        signature: Field | Optional[list[Byte]] = None

        def __bytes__(self) -> bytes:
            return self.message_id.bytes + (b''.join(_.bytes for _ in self.signature) if self.signature else b'')

        @classmethod
        def decode(cls, data_packet: DataPacket) -> Self:
            data_io = data_packet.bytes_io()
            message_id = VarInt.decode(data_io)
            if message_id.value == 0:
                signature = [Byte.decode(data_io) for _ in range(256)]
            else:
                signature = None
            return cls(message_id, signature)


    @dataclass(slots=True)
    class PCDisconnect(Packet):
        """
            Sent by the server before it disconnects a client.
            The client assumes that the server has already closed the connection by the time the packet arrives.
        """
        RESOURCE = 'disconnect'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x1D

        reason: Field | TextComponent


    @dataclass(slots=True)
    class PCDisguisedChat(Packet):
        """
            Sends the client a chat message, but without any message signing information.
        """
        RESOURCE = 'disguised_chat'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x1E

        message_id: Field | TextComponent
        chat_type: Field | VarInt
        sender_name: Field | TextComponent
        target_name: Field | OptionalTextComponent


    @dataclass(slots=True)
    class PCEntityEvent(Packet):
        """
            Entity statuses generally trigger an animation for an entity.
            The available statuses vary by the entity's type (and are available to subclasses of that type as well).
            See https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Entity_statuses
            for a list of which statuses are valid for each type of entity.
        """
        RESOURCE = 'entity_event'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x1F

        entity_id: Field | Int
        entity_status: Field | Byte


    @dataclass(slots=True)
    class PCEntityPositionSync(Packet):
        """
            This packet is sent by the server when an entity moves more than 8 blocks.
        """
        RESOURCE = 'entity_position_sync'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x20

        entity_id: Field | VarInt
        x: Field | Double
        y: Field | Double
        z: Field | Double
        velocity_x: Field |Double
        velocity_y: Field |Double
        velocity_z: Field | Double

        # Rotation on the X axis, in degrees.
        yam: Field | Float

        # Rotation on the Y axis, in degrees.
        pitch: Field | Float

        on_ground: Field | Boolean


    @dataclass(slots=True)
    class PCExplode(Packet):
        """
            Sent when an explosion occurs (creepers, TNT, and ghast fireballs).
        """

        RESOURCE = 'explode'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x21

        x: Field | Double
        y: Field | Double
        z: Field | Double
        has_player_velocity: OptionalGroupField[0] | Boolean
        player_velocity_x: OptionalGroupField[0] | Double
        player_velocity_y: OptionalGroupField[0] | Float
        player_velocity_z: OptionalGroupField[0] | Float
        explosion_particle: Field | Particle
        explosion_sound: Field | IDOrSoundEvent


    @dataclass(slots=True)
    class PCForgetLevelChunk(Packet):
        """
            Tells the client to unload a chunk column.
        """
        RESOURCE = 'forget_level_chunk'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x22

        chunk_z: Field | Int
        chunk_x: Field | Int


    @dataclass(slots=True)
    class PCGameEvent(Packet):
        """
            Used for a wide variety of game events, from weather to bed use to game mode to demo messages.
        """
        RESOURCE = 'game_event'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x23

        event: Field | UnsignedByte
        value: Field | Float


    @dataclass(slots=True)
    class PCHorseScreenOpen(Packet):
        """
            This packet is used exclusively for opening the horse GUI.
            Open Screen is used for all other GUIs.
            The client will not open the inventory if the Entity ID does not point to an horse-like animal.
        """
        RESOURCE = 'horse_screen_open'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x24

        window_id: Field | VarInt
        slot_count: Field | VarInt
        entity_id: Field | Int


    @dataclass(slots=True)
    class PCHurtAnimation(Packet):
        """
            Plays a bobbing animation for the entity receiving damage.
        """
        RESOURCE = 'hurt_animation'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x25

        entity_id: Field | VarInt
        yaw: Field | Float


    @dataclass(slots=True)
    class PCInitializeBorder(Packet):
        """
            Initial world border.
        """
        RESOURCE = 'initialize_border'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x26

        x: Field | Double
        z: Field | Double
        old_diameter: Field | Double
        new_diameter: Field | Double
        speed: Field | VarLong
        portal_teleport_boundary: Field | VarInt
        warning_blocks: Field | VarInt
        warning_time: Field | VarInt


    @dataclass(slots=True)
    class PCKeepAlive(Packet):
        """
            The server will frequently send out a keep-alive, each containing a random ID.
            The client must respond with the same payload (see Serverbound Keep Alive).
            If the client does not respond to a Keep Alive packet within 15 seconds after it was sent,
            the server kicks the client.
            Vice versa, if the server does not send any keep-alives for 20 seconds,
            the client will disconnect and yields a "Timed out" exception.
            The Notchian server uses a system-dependent time in milliseconds to generate the keep alive ID value.
        """
        RESOURCE = 'keep_alive'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x27

        keep_alive_id: Field | Long

        @classmethod
        def one(cls, *args, **kwargs) -> Self:
            return cls(keep_alive_id=Long(int(datetime.datetime.now().timestamp() * 1_000_000)))


    @dataclass(slots=True)
    class PCLevelChunkWithLight(Packet):
        """
            Sent when a chunk comes into the client's view distance,
            specifying its terrain, lighting and block entities.
        """
        RESOURCE = 'level_chunk_with_light'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x28

        chunk_x: Field | Int
        chunk_z: Field | Int
        data: Field | ChunkData
        light: Field | LightData

        def __repr__(self):
            return f"PacketsV769 {self.PACKET_ID_HEX} <ChunkWithLight>({self.chunk_x}, {self.chunk_z})"

        @classmethod
        def decode(cls, bytes_source: BytesIO | DataPacket | bytes, dimension_chunk_size: int = 24) -> Self:
            """
                不同世界 chunk size 不同
            :param bytes_source:
            :param dimension_chunk_size:
            :return:
            """
            bytes_io = cls.to_bytes_io(bytes_source)
            chunk_x = Int.decode(bytes_io)
            chunk_z = Int.decode(bytes_io)
            data = ChunkData.decode(bytes_io, dimension_chunk_size)
            light = LightData.decode(bytes_io)
            return cls(chunk_x=chunk_x, chunk_z=chunk_z, data=data, light=light)


    @dataclass(slots=True)
    class PCLevelEvent(Packet):
        """
            Sent when a client is to play a sound or particle effect.
        """
        RESOURCE = 'level_event'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x29

        event: Field | Int
        location: Field | Position
        data: Field | Int
        disable_relative_volume: Field | Boolean


    @dataclass(slots=True)
    class PCLevelParticles(Packet):
        """
            Displays the named particle
        """
        RESOURCE = 'level_particles'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x2A

        long_distance: Field | Boolean
        always_visible: Field | Boolean
        x: Field | Double
        y: Field | Double
        z: Field | Double
        offset_x: Field | Float
        offset_y: Field | Float
        offset_z: Field | Float
        max_speed: Field | Float
        particle_count: Field | Int
        particle: Field | Particle


    @dataclass(slots=True)
    class PCLightUpdate(Packet):
        """
            Updates light levels for a chunk. See Light for information on how lighting works in Minecraft.
            https://minecraft.wiki/w/Light
        """
        RESOURCE = 'light_update'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x2B

        chunk_x: Field | VarInt
        chunk_z: Field | VarInt
        data: Field | LightData


    @dataclass(slots=True)
    class PCLogin(Packet):
        """
            Player Login
        """

        RESOURCE = 'login'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x2C

        entity_id: Field | Int
        is_hardcore: Field | Boolean
        dimension_names: Field | list[Identifier]
        max_players: Field | VarInt
        view_distance: Field | VarInt
        simulation_distance: Field | VarInt
        reduced_debug_info: Field | Boolean
        enable_respawn_screen: Field | Boolean
        do_limited_crafting: Field | Boolean
        dimension_type: Field | VarInt
        dimension_name: Field | Identifier
        hashed_seed: Field | Long
        game_mode: Field | UnsignedByte
        previous_game_mode: Field | Byte
        is_debug: Field | Boolean
        is_flat: Field | Boolean
        has_death_location: OptionalGroupField[0] | Boolean
        death_dimension_name: OptionalGroupField[0] | Identifier
        death_location: OptionalGroupField[0] | Position
        portal_cooldown: Field | VarInt
        sea_level: Field | VarInt
        enforces_secure_chat: Field | Boolean


    @dataclass(slots=True)
    class PCMapItemData(Packet):
        """
            Updates a rectangular area on a map item.
        """
        @dataclass(slots=True)
        class Icon(Combined):
            type_: Field | VarInt
            x: Field | Byte
            z: Field | Byte
            direction: Field | Byte
            display_name: Field | OptionalTextComponent

        @dataclass(slots=True)
        class ColorPatch(Combined):

            columns: Field | UnsignedByte
            rows: Field | Optional[UnsignedByte] = None
            x: Field | Optional[UnsignedByte] = None
            z: Field | Optional[UnsignedByte] = None
            data: Field | Optional[list[UnsignedByte]] = None

            def __bytes__(self) -> bytes:
                bs = self.columns.bytes

                if self.rows is not None:
                    bs += self.rows.bytes

                if self.x is not None:
                    bs += self.x.bytes

                if self.z is not None:
                    bs += self.z.bytes

                if self.data is not None:
                    bs += self.list_to_bytes(self.data)

                return bs

            @classmethod
            def decode(cls, bytes_io: BytesIO, *args, **kwargs) -> Self:
                columns = UnsignedByte.decode(bytes_io)
                if columns.value == 0:
                    return cls(columns)
                else:
                    return cls(
                        columns, UnsignedByte.decode(bytes_io),
                        UnsignedByte.decode(bytes_io), UnsignedByte.decode(bytes_io),
                        cls.bytes_to_list(bytes_io, UnsignedByte)[1]
                    )

        RESOURCE = 'map_item_data'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x2D

        map_id: Field | VarInt
        scale: Field | Byte
        locked: Field | Boolean
        has_icon: OptionalGroupField[0] | Boolean
        icon: OptionalGroupField[0] | list[Icon] = None
        color_patch: Field | ColorPatch = None


    @dataclass(slots=True)
    class PCMerchantOffers(Packet):
        """
            The list of trades a villager NPC is offering.
        """
        RESOURCE = 'merchant_offers'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x2E

        window_id: Field | VarInt
        trades: Field | list[Trade]
        villager_level: Field | VarInt
        experience: Field | VarInt
        is_regular_villager: Field | Boolean
        can_restock: Field | Boolean


    @staticmethod
    def delta2cur(delta: int, prev: float) -> float:
        return delta / 4096.0 + prev


    @dataclass(slots=True)
    class PCMoveEntityPos(Packet):
        """
            This packet is sent by the server when an entity moves a small distance.
            The change in position is represented as a fixed-point number with 12 fraction bits and 4 integer bits.
            As such, the maximum movement distance along each axis is 8 blocks in the negative direction,
            or 7.999755859375 blocks in the positive direction.
            If the movement exceeds these limits, Teleport Entity should be sent instead.
        """
        RESOURCE = 'move_entity_pos'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x2F

        entity_id: Field | VarInt
        delta_x: Field | Short
        delta_y: Field | Short
        delta_z: Field | Short
        on_ground: Field | Boolean


    @dataclass(slots=True)
    class PCMoveEntityPosRot(Packet):
        """
            This packet is sent by the server when an entity rotates and moves.
            See #Update Entity Position for how the position is encoded.
            https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Protocol#Update_Entity_Position
        """
        RESOURCE = 'move_entity_pos_rot'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x30

        entity_id: Field | VarInt
        delta_x: Field | Short
        delta_y: Field | Short
        delta_z: Field | Short
        yaw: Field | Angle
        pitch: Field | Angle
        on_ground: Field | Boolean


    @dataclass(slots=True)
    class PCMoveMinecartAlongTrack(Packet):
        """
            Move Minecraft Along Track.
        """

        @dataclass(slots=True)
        class Step(Combined):
            x: Field | Double
            y: Field | Double
            z: Field | Double
            velocity_x: Field | Double
            velocity_y: Field | Double
            velocity_z: Field | Double
            yaw: Field | Angle
            pitch: Field | Angle
            weight: Field | Float

        RESOURCE = 'move_minecart_along_track'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x31

        entity_id: Field | VarInt
        step: Field | list[Step]


    @dataclass(slots=True)
    class PCMoveEntityRot(Packet):
        """
            This packet is sent by the server when an entity rotates.
        """
        RESOURCE = 'move_entity_rot'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x32

        entity_id: Field | VarInt
        yaw: Field | Angle
        pitch: Field | Angle
        on_ground: Field | Boolean


    @dataclass(slots=True)
    class PCMoveVehicle(Packet):
        """
            Note that all fields use absolute positioning and do not allow for relative positioning.
        """
        RESOURCE = 'move_vehicle'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x33

        x: Field | Double
        y: Field | Double
        z: Field | Double
        yaw: Field | Float
        pitch: Field | Float


    @dataclass(slots=True)
    class PCOpenBook(Packet):
        """
            Sent when a player right clicks with a signed book. This tells the client to open the book GUI.
        """
        RESOURCE = 'open_book'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x34

        hand: Field | VarInt


    @dataclass(slots=True)
    class PCOpenScreen(Packet):
        """
            This is sent to the client when it should open an inventory,
            such as a chest, workbench, furnace, or other container.
            Resending this packet with already existing window id,
            will update the window title and window type without closing the window.
        """
        RESOURCE = 'open_screen'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x35

        window_id: Field | VarInt
        window_type: Field | VarInt
        window_title: Field | TextComponent


    @dataclass(slots=True)
    class PCOpenSignEditor(Packet):
        """
            Sent when the client has placed a sign and is allowed to send Update Sign.
            There must already be a sign at the given location (which the client does not do automatically) -
            send a Block Update first.
        """
        RESOURCE = 'open_sign_editor'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x36

        location: Field | Position
        is_front_text: Field | Boolean


    @dataclass(slots=True)
    class PCPing(Packet):
        """
            Packet is not used by the Notchian server. When sent to the client,
            client responds with a Pong packet with the same id.
        """
        RESOURCE = 'ping'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x37

        id_: Field | Int


    @dataclass(slots=True)
    class PCPongResponse(Packet):
        """
            Ping Response.
        """
        RESOURCE = 'pong_response'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x38

        payload: Field | Long


    @dataclass(slots=True)
    class PCPlaceGhostRecipe(Packet):
        """
            Response to the serverbound packet (Place Recipe), with the same recipe ID.
            Appears to be used to notify the UI.
        """
        RESOURCE = 'place_ghost_recipe'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x39

        window_id: Field | VarInt
        recipe_display: Field | RecipeDisplay


    @dataclass(slots=True)
    class PCPlayerAbilities(Packet):
        """
            The latter 2 floats are used to indicate the flying speed and field of view respectively,
             while the first byte is used to determine the value of 4 booleans.
             About the flags:
            Field	                        Bit
            Invulnerable	                0x01
            Flying	                        0x02
            Allow Flying	                0x04
            Creative Mode (Instant Break)	0x08
            If Flying is set but Allow Flying is unset, the player is unable to stop flying.
        """
        RESOURCE = 'player_abilities'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x3A

        flags: Field | Byte
        flying_speed: Field | Float
        field_of_view_modifier: Field | Float


    @dataclass(slots=True)
    class PCPlayerChat(Packet):
        """
            Sends the client a chat message from a player
        """

        RESOURCE = 'player_chat'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x3B

        @dataclass(slots=True)
        class MessageSignatureArray(Combined):
            signature: Field | Optional[list[Byte]] = None

            def __bytes__(self) -> bytes:
                return Boolean.TRUE + b''.join(_.bytes for _ in self.signature) if self.signature else Boolean.FALSE

            @classmethod
            def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
                has_value = Boolean.decode(bytes_io)
                if has_value:
                    # 256定长
                    return cls([Byte.decode(bytes_io) for _ in range(256)])
                else:
                    return cls(None)

        @dataclass(slots=True)
        class SignatureMessage(Combined):
            message_id: Field | VarInt
            signature: Field | Optional[list[Byte]] = None

            def __bytes__(self) -> bytes:
                return self.message_id.bytes + (b''.join(_.bytes for _ in self.signature) if self.signature else b'')

            @classmethod
            def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
                message_id = VarInt.decode(bytes_io)
                if message_id.value == 0:
                    # 256定长
                    return cls(message_id, [Byte.decode(bytes_io) for _ in range(256)])
                else:
                    return cls(message_id)

        @dataclass(slots=True)
        class Filter(Combined):
            PASS_THROUGH: ClassVar[int] = 0
            FULLY_FILTERED: ClassVar[int]  = 1
            PARTIALLY_FILTERED: ClassVar[int]  = 2

            filter_type: Field | VarInt
            filter_type_bits: Optional[BitSet] = None

            def __bytes__(self) -> bytes:
                bs = self.filter_type.bytes
                if self.filter_type_bits:
                    bs += self.filter_type_bits.bytes
                return self.filter_type.bytes + (self.filter_type.bytes if self.filter_type_bits else b'')

            @classmethod
            def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
                filter_type = VarInt.decode(bytes_io)
                if filter_type.value == cls.PARTIALLY_FILTERED:
                    return cls(filter_type, BitSet.decode(bytes_io))
                else:
                    return cls(filter_type)

        sender: Field | UUID
        index: Field | VarInt

        message_signature_bytes: Field | MessageSignatureArray
        message: Field | String
        timestamp: Field | Long
        salt: Field | Long
        messages: Field | list[SignatureMessage]
        unsigned_content: Field | OptionalTextComponent
        filter: Field | Filter
        chat_type: Field | VarInt
        sender_name: Field | TextComponent
        target_name: Field | OptionalTextComponent


    @dataclass(slots=True)
    class PCPlayerCombatEnd(Packet):
        """
            Unused by the Notchian client.
            This data was once used for twitch.tv metadata circa 1.8.
        """
        RESOURCE = 'player_combat_end'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x3C

        duration: Field | VarInt


    @dataclass(slots=True)
    class PCPlayerCombatEnter(Packet):
        """
            Unused by the Notchian client. This data was once used for twitch.tv metadata circa 1.8.
        """
        RESOURCE = 'player_combat_enter'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x3D


    @dataclass(slots=True)
    class PCPlayerCombatKill(Packet):
        """
            Used to send a respawn screen.
        """
        RESOURCE = 'player_combat_kill'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x3E

        player_id: Field | VarInt
        message: Field | TextComponent


    @dataclass(slots=True)
    class PCPlayerInfoRemove(Packet):
        """
            Used by the server to remove players from the player list.
        """
        RESOURCE = 'player_info_remove'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x3F

        uuids: Field | list[UUID]


    @dataclass(slots=True)
    class PCPlayerInfoUpdate(Packet):
        """
            Sent by the server to update the user list (<tab> in the client).
        """

        @dataclass(slots=True)
        class Player(Combined):

            MASK_ADD_PLAYER: ClassVar[int] = 0x01
            MASK_INITIALIZE_CHAT: ClassVar[int] = 0x02
            MASK_UPDATE_GAME_MODE: ClassVar[int] = 0x04
            MASK_UPDATE_LISTED: ClassVar[int] = 0x08
            MASK_UPDATE_LATENCY: ClassVar[int] = 0x10
            MASK_UPDATE_DISPLAY_NAME: ClassVar[int] = 0x20
            MASK_UPDATE_LIST_PRIORITY: ClassVar[int] = 0x40
            MASK_UPDATE_HAT: ClassVar[int] = 0x80

            @dataclass(slots=True)
            class AddPlayer(Combined):

                @dataclass(slots=True)
                class Property(Combined):
                    name: Field | String
                    value: Field | String
                    signature: Field | OptionalString

                name: Field | String
                property: Field | list[Property]

            @dataclass(slots=True)
            class InitializeChat(Combined):
                has_signature_data: OptionalGroupField[0] | Boolean
                chat_session_id: OptionalGroupField[0] | UUID = None
                public_key_expiry_time: OptionalGroupField[0] | Long = None
                encoded_public_key: OptionalGroupField[0] | list[Byte] = None
                public_key_signature: OptionalGroupField[0] | list[Byte] = None


            uuid: Field | UUID
            player_actions: Field | tuple

            def __bytes__(self) -> bytes:
                return self.uuid.bytes + b''.join(_.bytes for _ in self.player_actions)

            @classmethod
            def decode(cls, bytes_io: BytesIO, actions: Byte) -> Self:
                uuid = UUID.decode(bytes_io)
                action = actions.value
                actions = []
                if action & cls.MASK_ADD_PLAYER:
                    actions.append(cls.AddPlayer.decode(bytes_io))

                if action & cls.MASK_INITIALIZE_CHAT:
                    actions.append(cls.InitializeChat.decode(bytes_io))

                if action & cls.MASK_UPDATE_GAME_MODE:
                    actions.append(VarInt.decode(bytes_io))

                if action & cls.MASK_UPDATE_LISTED:
                    actions.append(Boolean.decode(bytes_io))

                if action & cls.MASK_UPDATE_LATENCY:
                    actions.append(VarInt.decode(bytes_io))

                if action & cls.MASK_UPDATE_DISPLAY_NAME:
                    actions.append(OptionalTextComponent.decode(bytes_io))

                if action & cls.MASK_UPDATE_LIST_PRIORITY:
                    actions.append(VarInt.decode(bytes_io))

                if action & cls.MASK_UPDATE_HAT:
                    actions.append(Boolean.decode(bytes_io))

                return cls(uuid, tuple(actions))

        RESOURCE = 'player_info_update'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x40

        actions: Field | Byte
        players: Field | list[Player] = None

        @classmethod
        def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)
            actions = Byte.decode(bytes_io)
            return cls(
                actions,
                [
                    cls.Player.decode(bytes_io, actions) for _ in range(VarInt.decode(bytes_io).value)
                ]
            )

        def __bytes__(self) -> bytes:
            bs = self.actions.bytes + VarInt.encode(len(self.players))
            bs += b''.join(_.bytes for _ in self.players)
            return bs


    @dataclass(slots=True)
    class PCPlayerLookAt(Packet):
        """
            Used to rotate the client player to face the given location or entity
            (for /teleport [<targets>] <x> <y> <z> facing).
        """

        RESOURCE = 'player_look_at'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x41

        feet_or_eyes: Field | VarInt
        target_x: Field | Double
        target_y: Field | Double
        target_z: Field | Double
        is_entity: OptionalGroupField[0] | Boolean
        entity_id: OptionalGroupField[0] | Optional[VarInt] = None
        entity_feet_or_eyes: OptionalGroupField[0] | Optional[VarInt] = None


    @dataclass(slots=True)
    class PCPlayerPosition(Packet):
        """
            Teleports the client, e.g. during login, when using an ender pearl, in response to invalid move packets, etc.
            Due to latency, the server may receive outdated movement packets sent before the client was aware of the teleport.
            To account for this, the server ignores all movement packets
            from the client until a Confirm Teleportation packet with an ID matching the one
            sent in the teleport packet is received.
            Yaw is measured in degrees, and does not follow classical trigonometry rules.
            The unit circle of yaw on the XZ-plane starts at (0, 1) and turns counterclockwise,
            with 90 at (-1, 0), 180 at (0, -1) and 270 at (1, 0).
            Additionally, yaw is not clamped to between 0 and 360 degrees;
            any number is valid, including negative numbers and numbers greater than 360 (see MC-90097).
            Pitch is measured in degrees, where 0 is looking straight ahead, -90 is looking straight up,
            and 90 is looking straight down.
        """
        RESOURCE = 'player_position'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x42

        teleport_id: Field | VarInt
        x: Field | Double
        y: Field | Double
        z: Field | Double
        velocity_x: Field | Double
        velocity_y: Field | Double
        velocity_z: Field | Double
        yaw: Field | Float
        pitch: Field | Float
        flags: Field | Int


    @dataclass(slots=True)
    class PCPlayerRotation(Packet):
        """
            Player Rotation
        """
        RESOURCE = 'player_rotation'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x43

        yaw: Field | Float
        pitch: Field | Float


    @dataclass(slots=True)
    class PCRecipeBookAdd(Packet):
        """
              Recipe Book Add.
        """
        RESOURCE = 'recipe_book_add'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x44

        @dataclass(slots=True)
        class Recipe(Combined):
            recipe_id: Field | VarInt
            display: Field | RecipeDisplay
            group_id: Field | VarInt
            category_id: Field | VarInt
            has_ingredients: OptionalGroupField[0] | Boolean
            ingredients: OptionalGroupField[0] | list[IDSet]
            flags: Field | Byte

        recipes: Field | list[Recipe]
        replace: Field | Boolean


    @dataclass(slots=True)
    class PCRecipeBookRemove(Packet):
        """
            Recipe Book Remove.
        """
        RESOURCE = 'recipe_book_remove'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x45

        recipes: Field | list[VarInt]


    @dataclass(slots=True)
    class PCRecipeBookSettings(Packet):
        """
            Recipe Book Settings.
        """
        RESOURCE = 'recipe_book_settings'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x46

        crafting_recipe_book_open: Field | Boolean
        crafting_recipe_book_filter_active: Field | Boolean
        smelting_recipe_book_open: Field | Boolean
        smelting_recipe_book_filter_active: Field | Boolean
        blast_furnace_recipe_book_open: Field | Boolean
        blast_furnace_recipe_book_filter_active: Field | Boolean
        smoker_recipe_book_open: Field | Boolean
        smoker_recipe_book_filter_active: Field | Boolean


    @dataclass(slots=True)
    class PCRemoveEntities(Packet):
        """
            Sent by the server when an entity is to be destroyed on the client.
        """
        RESOURCE = 'remove_entities'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x47

        entity_ids: Field | list[VarInt]


    @dataclass(slots=True)
    class PCRemoveMobEffect(Packet):
        """
            Remove Entity Effect.
        """
        RESOURCE = 'remove_mob_effect'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x48

        entity_id: Field | VarInt
        effect_id: Field | VarInt


    @dataclass(slots=True)
    class PCResetScore(Packet):
        """
            This is sent to the client when it should remove a scoreboard item.
        """
        RESOURCE = 'reset_score'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x49

        entity_name: Field | String
        objective_name: Field | OptionalString


    @dataclass(slots=True)
    class PCResourcePackPop(Packet):
        """
            Remove Resource Pack.
        """
        RESOURCE = 'resource_pack_pop'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x4A

        uuid: Field | OptionalUUID


    @dataclass(slots=True)
    class PCResourcePackPush(Packet):
        """
            Add Resource Pack.
        """
        RESOURCE = 'resource_pack_push'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x4B

        uuid: Field | UUID
        url: Field | String
        hash: Field | String
        forced: Field | Boolean
        prompt_message: Field | OptionalTextComponent


    @dataclass(slots=True)
    class PCRespawn(Packet):
        """
            To change the player's dimension (overworld/nether/end),
            send them a respawn packet with the appropriate dimension,
            followed by prechunks/chunks for the new dimension,
            and finally a position and look packet.
            You do not need to unload chunks, the client will do it automatically.
        """
        RESOURCE = 'respawn'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x4C

        dimension_type: Field | VarInt
        dimension_name: Field | Identifier
        hashed_seed: Field | Long
        game_mode: Field | UnsignedByte
        previous_game_mode: Field | Byte
        is_debug: Field | Boolean
        is_flat: Field | Boolean
        has_death_location: OptionalGroupField[0] | Boolean
        death_dimension_name: OptionalGroupField[0] | Identifier
        death_location: OptionalGroupField[0] | Position
        portal_cooldown: Field | VarInt
        sea_level: Field | VarInt
        data_kept: Field | Byte


    @dataclass(slots=True)
    class PCRotateHead(Packet):
        """
            Changes the direction an entity's head is facing.
            While sending the Entity Look packet changes the vertical rotation of the head,
            sending this packet appears to be necessary to rotate the head horizontally.
        """
        RESOURCE = 'rotate_head'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x4D

        entity_id: Field | VarInt
        head_yaw: Field | Angle


    @dataclass(slots=True)
    class PCSectionBlocksUpdate(Packet):
        """
            Fired whenever 2 or more blocks are changed within the same chunk on the same tick.
        """
        RESOURCE = 'section_blocks_update'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x4E

        chunk_section_position: Field | Long
        blocks: Field | list[VarLong]


    @dataclass(slots=True)
    class PCSelectAdvancementsTab(Packet):
        """
            Sent by the server to indicate that the client should switch advancement tab.
            Sent either when the client switches tab in the GUI or when an advancement in another tab is made.
        """
        RESOURCE = 'select_advancements_tab'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x4F

        identifier: Field | OptionalIdentifier


    @dataclass(slots=True)
    class PCServerData(Packet):
        """
            Server data.
        """
        RESOURCE = 'server_data'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x50

        motd: Field | TextComponent
        has_icon: OptionalGroupField[0] | Boolean
        icons: OptionalGroupField[0] | list[Byte] = None


    @dataclass(slots=True)
    class PCSetActionBarText(Packet):
        """
            Displays a message above the hotbar.
        """
        RESOURCE = 'set_action_bar_text'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x51

        action_bar_text: Field | TextComponent


    @dataclass(slots=True)
    class PCSetBorderCenter(Packet):
        RESOURCE = 'set_border_center'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x52

        x: Field | Double
        y: Field | Double


    @dataclass(slots=True)
    class PCSetBorderLerpSize(Packet):
        """
            Set Border Lerp Size.
        """
        RESOURCE = 'set_border_lerp_size'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x53

        old_diameter: Field | Double
        new_diameter: Field | Double
        speed: Field | VarLong


    @dataclass(slots=True)
    class PCSetBorderSize(Packet):
        """
            Set Border Size.
        """
        RESOURCE = 'set_border_size'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x54

        diameter: Field | Double


    @dataclass(slots=True)
    class PCSetBorderWarningDelay(Packet):
        """
            Set Border Warning Delay.
        """
        RESOURCE = 'set_border_warning_delay'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x55

        warning_time: Field | VarInt


    @dataclass(slots=True)
    class PCSetBorderWarningDistance(Packet):
        """
            Set Border Warning Distance.
        """
        RESOURCE = 'set_border_warning_distance'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x56

        warning_blocks: Field | VarInt


    @dataclass(slots=True)
    class PCSetCamera(Packet):
        """
            Sets the entity that the player renders from.
        """
        RESOURCE = 'set_camera'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x57

        camera_id: Field | VarInt


    @dataclass(slots=True)
    class PCSetChunkCacheCenter(Packet):
        """
            Sets the center position of the client's chunk loading area.
        """
        RESOURCE = 'set_chunk_cache_center'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x58

        chunk_x: Field | VarInt
        chunk_z: Field | VarInt


    @dataclass(slots=True)
    class PCSetChunkCacheRadius(Packet):
        """
            Sent by the integrated singleplayer server when changing render distance.
            This packet is sent by the server when the client reappears in the overworld after leaving the end.
        """
        RESOURCE = 'set_chunk_cache_radius'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x59

        view_distance: Field | VarInt


    @dataclass(slots=True)
    class PCSetCursorItem(Packet):
        """
            Replaces or sets the inventory item that's being dragged with the mouse.
        """
        RESOURCE = 'set_cursor_item'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x5A

        carried_item: Field | Slot


    @dataclass(slots=True)
    class PCSetDefaultSpawnPosition(Packet):
        """
            Sent by the server after login to specify the coordinates of the spawn point
             (the point at which players spawn at, and which the compass points to).
             It can be sent at any time to update the point compasses point at.
        """
        RESOURCE = 'set_default_spawn_position'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x5B

        location: Field | Position
        angle: Field | Float


    @dataclass(slots=True)
    class PCSetDisplayObjective(Packet):
        """
            This is sent to the client when it should display a scoreboard.
        """
        RESOURCE = 'set_display_objective'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x5C

        position: Field | VarInt
        score_name: Field | String


    @dataclass(slots=True)
    class PCSetEntityData(Packet):
        """
            Updates one or more metadata properties for an existing entity.
            Any properties not included in the Metadata field are left unchanged.
        """
        RESOURCE = 'set_entity_data'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x5D

        entity_id: Field | VarInt
        metadata: Field | EntityMetadata


    @dataclass(slots=True)
    class PCSetEntityLink(Packet):
        """
            This packet is sent when an entity has been leashed to another entity.
        """
        RESOURCE = 'set_entity_link'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x5E

        attached_entity_id: Field | Int
        holding_entity_id: Field | Int


    @dataclass(slots=True)
    class PCSetEntityMotion(Packet):
        """
            Velocity is in units of 1/8000 of a block per server tick (50ms);
            for example, -1343 would move (-1343 / 8000) = −0.167875 blocks per tick (or −3.3575 blocks per second).
        """
        RESOURCE = 'set_entity_motion'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x5F

        entity_id: Field | VarInt
        velocity_x: Field | Short
        velocity_y: Field | Short
        velocity_z: Field | Short


    @dataclass(slots=True)
    class PCSetEquipment(Packet):
        """
            Set Equipment
        """
        RESOURCE = 'set_equipment'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x60

        @dataclass(slots=True)
        class Equipment(Combined):
            slot: Field | Byte
            item: Field | Slot

        entity_id: Field | VarInt
        equipments: Field | list[Equipment]

        def __bytes__(self) -> bytes:
            return self.entity_id.bytes + b''.join(_.bytes for _ in self.equipments)

        @classmethod
        def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)

            entity_id = VarInt.decode(bytes_io)
            equipments = []

            while True:
                equipment = cls.Equipment.decode(bytes_io)
                equipments.append(equipment)
                if equipment.slot.value < 64:
                    break

            return cls(entity_id=entity_id, equipments=equipments)


    @dataclass(slots=True)
    class PCSetExperience(Packet):
        """
            Sent by the server when the client should change experience levels.
        """
        RESOURCE = 'set_experience'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x61

        experience_bar: Field | Float
        level: Field | VarInt
        total_experience: Field | VarInt


    @dataclass(slots=True)
    class PCSetHealth(Packet):
        """
            Sent by the server to set the health of the player it is sent to.
            Food saturation acts as a food “overcharge”.
            Food values will not decrease while the saturation is over zero.
            New players logging in or respawning automatically get a saturation of 5.0.
            Eating food increases the saturation as well as the food bar.
        """
        RESOURCE = 'set_health'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x62

        health: Field | Float
        food: Field | VarInt
        food_saturation: Field | Float


    @dataclass(slots=True)
    class PCSetHeldSlot(Packet):
        """
            Sent to change the player's slot selection.
        """
        RESOURCE = 'set_held_slot'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x63

        slot: Field | VarInt


    @dataclass(slots=True)
    class PCSetObjective(Packet):
        """
            This is sent to the client when it should create a new scoreboard objective or remove one.
        """
        RESOURCE = 'set_objective'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x64

        objective_name: Field | String
        mode: Field | Byte
        objective_value: Field | Optional[TextComponent] = None
        type_: Field | Optional[VarInt] = None
        has_number_format: Field | Optional[Boolean] = None
        number_format: Field | Optional[VarInt] = None
        format_data: Field | Optional[DataType] = None

        def __bytes__(self) -> bytes:
            bs = self.objective_name.bytes + self.mode.bytes

            if self.objective_value:
                bs += self.objective_value.bytes

            if self.type_:
                bs += self.type_.bytes

            if self.has_number_format:
                bs += self.number_format.bytes

            if self.number_format:
                bs += self.number_format.bytes

            if self.format_data:
                bs += self.format_data.bytes

            return bs

        @classmethod
        def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)

            objective_name = String.decode(bytes_io)
            mode = Byte.decode(bytes_io)

            _condition = (
                ENUMS.UpdateScoreAction.CREATE,
                ENUMS.UpdateScoreAction.UPDATE,
            )

            instance = cls(objective_name=objective_name, mode=mode)

            if mode.value in _condition:
                instance.objective_value = TextComponent.decode(bytes_io)
                instance.type_ = VarInt.decode(bytes_io)
                instance.has_number_format = Boolean.decode(bytes_io)
                if instance.has_number_format:
                    instance.number_format = VarInt.decode(bytes_io)
                    if instance.number_format.value == 1:
                        instance.format_data = TagCompound.decode(bytes_io)
                    else:
                        instance.format_data = TextComponent.decode(bytes_io)

            return instance


    @dataclass(slots=True)
    class PCSetPassengers(Packet):
        """
            Set Passengers
        """
        RESOURCE = 'set_passengers'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x65

        entity_id: Field | VarInt
        passengers: Field | list[VarInt]


    @dataclass(slots=True)
    class PCSetPlayerInventory(Packet):
        """
            Set Player's inventory slot.
        """
        RESOURCE = 'set_player_inventory'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x66

        slot: Field | VarInt
        slot_data: Field | Slot


    @dataclass(slots=True)
    class PCSetPlayerTeam(Packet):
        """
            Creates and updates teams.
        """
        RESOURCE = 'set_player_team'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x67

        @dataclass(slots=True)
        class TeamMethod(Combined):

            @dataclass(slots=True)
            class CreateTeam(Combined):
                team_display_name: Field | TextComponent
                friendly_flags: Field | Byte
                name_tag_visibility: Field | String
                collision_rule: Field | String
                team_color: Field | VarInt
                team_prefix: Field | TextComponent
                team_suffix: Field | TextComponent
                entities: Field | list[String]

            @dataclass(slots=True)
            class RemoveTeam(Combined): ...

            @dataclass(slots=True)
            class UpdateTeamInfo(Combined):
                team_display_name: Field | TextComponent
                friendly_flags: Field | Byte
                name_tag_visibility: Field | String
                collision_rule: Field | String
                team_color: Field | VarInt
                team_prefix: Field | TextComponent
                team_suffix: Field | TextComponent

            @dataclass(slots=True)
            class AddEntitiesToTeam(Combined):
                entities: Field | list[String]

            @dataclass(slots=True)
            class RemoveEntitiesFromTeam(Combined):
                entities: Field | list[String]

            method: Field | Byte
            methodAction: Field | Combined

            @classmethod
            def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
                bytes_io = cls.to_bytes_io(bytes_source)

                method = Byte.decode(bytes_io)
                if method.value == ENUMS.UpdateTeamsMethod.CREATE_TEAM:
                    return cls(method, cls.CreateTeam.decode(bytes_io))

                elif method.value == ENUMS.UpdateTeamsMethod.REMOVE_TEAM:
                    return cls(method, cls.RemoveTeam.decode(bytes_io))

                elif method.value == ENUMS.UpdateTeamsMethod.UPDATE_TEAM_INFO:
                    return cls(method, cls.UpdateTeamInfo.decode(bytes_io))

                elif method.value == ENUMS.UpdateTeamsMethod.ADD_ENTITIES_TO_TEAM:
                    return cls(method, cls.AddEntitiesToTeam.decode(bytes_io))

                elif method.value == ENUMS.UpdateTeamsMethod.REMOVE_ENTITIES_FROM_TEAM:
                    return cls(method, cls.RemoveEntitiesFromTeam.decode(bytes_io))

        team_name: Field | String
        action: Field | TeamMethod


    @dataclass(slots=True)
    class PCSetScore(Packet):
        """
            This is sent to the client when it should update a scoreboard item.
        """
        RESOURCE = 'set_score'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x68

        entity_name: Field | String
        objective_name: Field | String
        value: Field | VarInt
        display_name: Field | OptionalTextComponent
        number_format: Field | OptionalVarInt
        format_data: Field | Optional[DataType] = None

        def __bytes__(self) -> bytes:
            bs = self.entity_name.bytes + self.objective_name.bytes + self.value.bytes + self.display_name.bytes + self.number_format.bytes
            if self.format_data:
                bs += self.format_data.bytes
            return bs

        @classmethod
        def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)
            entity_name = String.decode(bytes_io)
            objective_name = String.decode(bytes_io)
            value = VarInt.decode(bytes_io)
            display_name = OptionalTextComponent.decode(bytes_io)
            number_format = OptionalVarInt.decode(bytes_io)

            instance = cls(entity_name, objective_name, value, display_name, number_format)

            if number_format.value == 1:
                instance.format_data = TagCompound.decode(bytes_io)
            elif number_format.value == 2:
                instance.format_data = TextComponent.decode(bytes_io)

            return instance


    @dataclass(slots=True)
    class PCSetSimulationDistance(Packet):
        """
            Set simulation distance.
        """
        RESOURCE = 'set_simulation_distance'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x69

        simulation_distance: Field | VarInt


    @dataclass(slots=True)
    class PCSetSubtitleText(Packet):
        """
            Set Subtitle Text
        """
        RESOURCE = 'set_subtitle_text'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x6A

        subtitle_text: Field | TextComponent


    @dataclass(slots=True)
    class PCSetTime(Packet):
        """
            Time is based on ticks, where 20 ticks happen every second.
            There are 24000 ticks in a day, making Minecraft days exactly 20 minutes long.
            The time of day is based on the timestamp modulo 24000.
            0 is sunrise, 6000 is noon, 12000 is sunset, and 18000 is midnight.
            The default SMP server increments the time by 20 every second.
        """
        RESOURCE = 'set_time'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x6B

        world_age: Field | Long
        time_of_day: Field | Long
        time_of_day_increasing: Field | Boolean


    @dataclass(slots=True)
    class PCSetTitleText(Packet):
        """
            Set Title Text
        """
        RESOURCE = 'set_title_text'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x6C

        title_text: Field | TextComponent


    @dataclass(slots=True)
    class PCSetTitlesAnimation(Packet):
        """
            Set Title Animation Times
        """
        RESOURCE = 'set_titles_animation'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x6D

        fade_in: Field | Int
        stay: Field | Int
        fade_out: Field | Int


    @dataclass(slots=True)
    class PCSoundEntity(Packet):
        """
            Plays a sound effect from an entity, either by hardcoded ID or Identifier.
            Sound IDs and names can be found here.
            https://pokechu22.github.io/Burger/1.21.html#sounds
        """
        RESOURCE = 'sound_entity'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x6E

        sound_effect: Field | IDOrSoundEvent
        sound_category: Field | VarInt
        entity_id: Field | VarInt
        volume: Field | Float
        pitch: Field | Float
        seed: Field | Long


    @dataclass(slots=True)
    class PCSound(Packet):
        """
            Plays a sound effect at the given location, either by hardcoded ID or Identifier.
            Sound IDs and names can be found here.
            https://pokechu22.github.io/Burger/1.21.html#sounds
        """
        RESOURCE = 'sound'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x6F

        sound_event: Field | IDOrSoundEvent
        sound_category: Field | VarInt
        effect_position_x: Field | Int
        effect_position_y: Field | Int
        effect_position_z: Field | Int
        volume: Field | Float
        pitch: Field | Float
        seed: Field | Long


    @dataclass(slots=True)
    class PCStartConfiguration(Packet):
        """
            Sent during gameplay in order to redo the configuration process.
            The client must respond with Acknowledge Configuration for the process to start.
        """
        RESOURCE = 'start_configuration'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x70
        FIELDS = ()


    @dataclass(slots=True)
    class PCStopSound(Packet):
        """
            Stop Sound.
        """
        RESOURCE = 'stop_sound'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x71

        flags: Field | Byte
        source: Field | Optional[VarInt] = None
        sound: Field | Optional[Identifier] = None

        def __bytes__(self) -> bytes:
            return self.flags.bytes + (
                self.source.bytes if self.source else b''
            ) + (
                self.sound.bytes if self.sound else b''
            )

        @classmethod
        def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)
            flags = Byte.decode(bytes_io)
            instance = cls(flags)

            if flags in (
                ENUMS.SoundCategory.MUSIC,
                ENUMS.SoundCategory.WEATHER,
            ):
                instance.source = VarInt.decode(bytes_io)

            if flags in (
                ENUMS.SoundCategory.RECORD,
                ENUMS.SoundCategory.WEATHER,
            ):
                instance.sound = Identifier.decode(bytes_io)

            return instance


    @dataclass(slots=True)
    class PCStoreCookie(Packet):
        """
            Stores some arbitrary data on the client, which persists between server transfers.
            The Notchian client only accepts cookies of up to 5 kiB in size.
        """
        RESOURCE = 'store_cookie'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x72

        key: Field | Identifier
        payload: Field | list[Byte]


    @dataclass(slots=True)
    class PCSystemChat(Packet):
        """
            Sends the client a raw system message.
        """
        RESOURCE = 'system_chat'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x73

        content: Field | TextComponent
        overlay: Field | Boolean


    @dataclass(slots=True)
    class PCTabList(Packet):
        """
            This packet may be used by custom servers to display additional information above/below the player list.
             It is never sent by the Notchian server.
        """
        RESOURCE = 'tab_list'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x74

        header: Field | TextComponent
        footer: Field | TextComponent


    @dataclass(slots=True)
    class PCTagQuery(Packet):
        """
            Sent in response to Query Block Entity Tag or Query Entity Tag.
        """
        RESOURCE = 'tag_query'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x75

        transaction_id: Field | VarInt
        nbt: Field | NBT


    @dataclass(slots=True)
    class PCTakeItemEntity(Packet):
        """
            Sent by the server when someone picks up an item lying on the ground
            — its sole purpose appears to be the animation of the item flying towards you.
        """
        RESOURCE = 'take_item_entity'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x76

        collected_entity_id: Field | VarInt
        collector_entity_id: Field | VarInt
        pickup_item_count: Field | VarInt


    @dataclass(slots=True)
    class PCTeleportEntity(Packet):
        """
            Teleports the entity on the client without changing the reference point of movement deltas
            in future Update Entity Position packets.
            Seems to be used to make relative adjustments to vehicle positions; more information needed.
        """
        RESOURCE = 'teleport_entity'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x77

        entity_id: Field | VarInt
        x: Field | Double
        y: Field | Double
        z: Field | Double
        velocity_x: Field | Double
        velocity_y: Field | Double
        velocity_z: Field | Double
        yaw: Field | Float
        pitch: Field | Float
        flags: Field | TeleportFlags
        on_ground: Field | Boolean


    @dataclass(slots=True)
    class PCTickingState(Packet):
        """
            Used to adjust the ticking rate of the client, and whether it's frozen.
        """
        RESOURCE = 'ticking_state'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x78

        tick_rate: Field | Float
        is_frozen: Field | Boolean


    @dataclass(slots=True)
    class PCTickingStep(Packet):
        """
            Advances the client processing by the specified number of ticks.
            Has no effect unless client ticking is frozen.
        """
        RESOURCE = 'ticking_step'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x79

        tick_steps: Field | VarInt


    @dataclass(slots=True)
    class PCTransfer(Packet):
        """
            Notifies the client that it should transfer to the given server.
            Cookies previously stored are preserved between server transfers.
        """
        RESOURCE = 'transfer'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x7A

        host: Field | String
        port: Field | String


    @dataclass(slots=True)
    class PCUpdateAdvancements(Packet):
        """
            Update Advancements.
        """
        RESOURCE = 'update_advancements'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x7B

        reset_or_clear: Field | Boolean
        advancement_mapping: Field | list[AdvancementMapping]
        identifiers: Field | list[Identifier]
        progress_mapping: Field | list[ProgressMapping]


    @dataclass(slots=True)
    class PCUpdateAttributes(Packet):
        """
            Sets attributes on the given entity.
            https://minecraft.wiki/w/Attribute
        """
        RESOURCE = 'update_attributes'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x7C

        @dataclass(slots=True)
        class Property(Combined):

            @dataclass(slots=True)
            class Modifier(Combined):
                id_: Field | Identifier
                amount: Field | Double
                operation: Field | Byte

            id_: Field | VarInt
            value: Field | Double
            modifiers: Field | list[Modifier]

        entity_id: Field | VarInt
        properties: Field | list[Property]


    @dataclass(slots=True)
    class PCUpdateMobEffect(Packet):
        """
            Entity Effect.
        """
        RESOURCE = 'update_mob_effect'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x7D

        entity_id: Field | VarInt
        effect_id: Field | VarInt
        amplifier: Field | VarInt
        duration: Field | VarInt
        flags: Field | Byte


    @dataclass(slots=True)
    class PCUpdateRecipes(Packet):
        """
            Update Recipes
        """
        RESOURCE = 'update_recipes'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x7E

        @dataclass(slots=True)
        class PropertySet(Combined):
            property_set_id: Field | Identifier
            items: Field | list[VarInt]

        @dataclass(slots=True)
        class StonecutterRecipe(Combined):
            ingredients: Field | IDSet
            slot_display: Field | SlotDisplay

        property_sets: Field | list[PropertySet]
        stonecutter_recipes: Field | list[StonecutterRecipe]


    @dataclass(slots=True)
    class PCUpdateTags(Packet):
        """
            Update Tags
        """
        RESOURCE = 'update_tags'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x7F

        @dataclass(slots=True)
        class Registry(Combined):

            @dataclass(slots=True)
            class Tag(Combined):
                tag_name: Field | Identifier
                entries: Field | list[VarInt]

            registry: Field | Identifier
            tags: Field | list[Tag]

        registry_to_tags_map: Field | list[Registry]


    @dataclass(slots=True)
    class PCProjectilePower(Packet):
        """
            Projectile Power
        """
        RESOURCE = 'projectile_power'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x80

        entity_id: Field | VarInt
        power: Field | Double


    @dataclass(slots=True)
    class PCCustomReportDetails(Packet):
        """
            Contains a list of key-value text entries that are included
            in any crash or disconnection report generated during connection to the server.
        """
        RESOURCE = 'custom_report_details'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x81

        @dataclass(slots=True)
        class Detail(Combined):
            title: Field | String
            description: Field | String

        details: Field | list[Detail]


    @dataclass(slots=True)
    class PCServerLinks(Packet):
        """
            This packet contains a list of links that the Notchian client will display
            in the menu available from the pause menu.
            Link labels can be built-in or custom (i.e., any text).
        """
        RESOURCE = 'server_links'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.CLIENT
        PACKET_ID_HEX = 0x82

        @dataclass(slots=True)
        class Link(Combined):
            is_built_in: Field | Boolean
            label: Field | Union[VarInt, TextComponent]
            url: Field | String

            def __bytes__(self) -> bytes:
                return self.is_built_in.bytes + self.label.bytes + self.url.bytes

            @classmethod
            def decode(cls, bytes_source: BytesIO) -> Self:
                is_built_in = Boolean.decode(bytes_source)
                if is_built_in:
                    label = VarInt.decode(bytes_source)
                else:
                    label = TextComponent.decode(bytes_source)
                url = String.decode(bytes_source)
                return cls(is_built_in=is_built_in, label=label, url=url)

        links: Field | list[Link]


    # Play BoundTo Server
    # -------------------------------------------------------------------------------------

    @dataclass(slots=True)
    class PSAcceptTeleportation(Packet):
        """
            Sent by client as confirmation of Synchronize Player Position.
        """
        RESOURCE = 'accept_teleportation'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x00

        teleport_id: Field | VarInt


    @dataclass(slots=True)
    class PSBlockEntityTagQuery(Packet):
        """
            Used when F3+I is pressed while looking at a block.
        """
        RESOURCE = 'block_entity_tag_query'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x01

        transaction_id: Field | VarInt
        location: Field | Position


    @dataclass(slots=True)
    class PSBundleItemSelected(Packet):
        """
            Bundle item selected.
        """
        RESOURCE = 'bundle_item_selected'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x02

        slot_of_bundle: Field | VarInt
        slot_in_bundle: Field | VarInt


    @dataclass(slots=True)
    class PSChangeDifficulty(Packet):
        """
            Must have at least op level 2 to use.
            Appears to only be used on singleplayer;
            the difficulty buttons are still disabled in multiplayer.
        """
        RESOURCE = 'change_difficulty'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x03

        new_difficulty: Field | Byte


    @dataclass(slots=True)
    class PSChatAck(Packet):
        """
            Acknowledge message.
        """
        RESOURCE = 'chat_ack'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x04

        message_count: Field | VarInt


    @dataclass(slots=True)
    class PSChatCommand(Packet):
        """
            Chat Command.
        """
        RESOURCE = 'chat_command'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x05

        command: Field | String


    @dataclass(slots=True)
    class PSChatCommandSigned(Packet):
        """
            Signed Chat.
        """
        RESOURCE = 'chat_command_signed'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x06

        @dataclass(slots=True)
        class ArgumentSignature(Combined):
            argument_name: Field | String
            signature: Field | list[Byte]

            def __bytes__(self) -> bytes:
                return self.argument_name.bytes + b''.join(_.bytes for _ in self.signature)

            @classmethod
            def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
                bytes_io = cls.to_bytes_io(bytes_source)
                return cls(
                    String.decode(bytes_io), [Byte.decode(bytes_io) for _ in range(256)],
                )

        command: Field | String
        timestamp: Field | Long
        salt: Field | Long
        argument_signatures: Field | list[ArgumentSignature]
        message_count: Field | VarInt
        acknowledged: Field | FixedBitSet


    @dataclass(slots=True)
    class PSChat(Packet):
        """
            Used to send a chat message to the server.
            The message may not be longer than 256 characters or else the server will kick the client.
        """
        RESOURCE = 'chat'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x07

        message: Field | String
        timestamp: Field | Long
        salt: Field | Long
        signature: Field | OptionalSignature256
        message_count: Field | VarInt
        acknowledged: Field | FixedBitSet


    @dataclass(slots=True)
    class PSChatSessionUpdate(Packet):
        """
            Player Session.
        """
        RESOURCE = 'chat_session_update'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x08

        @dataclass(slots=True)
        class PublicKey(Combined):
            expires_at: Field | Long
            public_key: Field | list[Byte]
            key_signature: Field | list[Byte]

        session_id: Field | UUID
        public_key: Field | PublicKey


    @dataclass(slots=True)
    class PSChunkBatchReceived(Packet):
        """
            Notifies the server that the chunk batch has been received by the client.
            The server uses the value sent in this packet to adjust the number of chunks to be sent in a batch.
        """
        RESOURCE = 'chunk_batch_received'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x09

        chunks_per_tick: Field | Float


    @dataclass(slots=True)
    class PSClientCommand(Packet):
        """
            Client Status.
            Action ID	Action	Notes
            0	Perform respawn	Sent when the client is ready to complete login and when the client is ready to respawn after death.
            1	Request stats	Sent when the client opens the Statistics menu.
        """
        RESOURCE = 'client_command'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x0A

        action_id: Field | VarInt


    @dataclass(slots=True)
    class PSClientTickEnd(Packet):
        """
            Client Tick End.
        """
        RESOURCE = 'client_tick_end'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x0B


    @dataclass(slots=True)
    class PSClientInformation(Packet):
        """
            Sent when the player connects, or when settings are changed.
        """
        RESOURCE = 'client_information'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x0C

        locale: Field | String
        view_distance: Field | Byte
        chat_mode: Field | VarInt
        chat_colors: Field | Boolean
        displayed_skin_parts: Field | UnsignedByte
        main_hand: Field | VarInt
        enable_text_filtering: Field | Boolean
        allow_server_listings: Field | Boolean


    @dataclass(slots=True)
    class PSCommandSuggestion(Packet):
        """
            Sent when the client needs to tab-complete a minecraft:ask_server suggestion type.
        """
        RESOURCE = 'command_suggestion'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x0D

        transaction_id: Field | VarInt
        text: Field | String


    @dataclass(slots=True)
    class PSConfigurationAcknowledged(Packet):
        """
            Sent by the client upon receiving a Start Configuration packet from the server.
            This packet switches the connection state to configuration.
        """
        RESOURCE = 'configuration_acknowledged'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x0E


    @dataclass(slots=True)
    class PSContainerButtonClick(Packet):
        """
            Used when clicking on window buttons. Until 1.14, this was only used by enchantment tables.
        """
        RESOURCE = 'container_button_click'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x0F

        window_id: Field | VarInt
        button_id: Field | VarInt


    @dataclass(slots=True)
    class PSContainerClick(Packet):
        """
            This packet is sent by the client when the player clicks on a slot in a window.
        """
        RESOURCE = 'container_click'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x10

        @dataclass(slots=True)
        class ChangedSlot(Combined):
            slot_number: Field | Short
            slot_data: Field | Slot

        window_id: Field | VarInt
        state_id: Field | VarInt
        slot: Field | Short
        button: Field | Byte
        mode: Field | VarInt
        changed_slots: Field | list[ChangedSlot]
        carried_item: Field | Slot


    @dataclass(slots=True)
    class PSContainerClose(Packet):
        """
            This packet is sent by the client when closing a window.
            Notchian clients send a Close Window packet with Window ID 0 to close their inventory
            even though there is never an Open Screen packet for the inventory.
        """
        RESOURCE = 'container_close'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x11

        window_id: Field | VarInt


    @dataclass(slots=True)
    class PSContainerSlotStateChanged(Packet):
        """
            This packet is sent by the client when toggling the state of a Crafter.
        """
        RESOURCE = 'container_slot_state_changed'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x12

        slot_id: Field | VarInt
        window_id: Field | VarInt
        state: Field | Boolean


    @dataclass(slots=True)
    class PSCookieResponse(Packet):
        """
            Response to a Cookie Request (play) from the server.
            The Notchian server only accepts responses of up to 5 kiB in size.
        """
        RESOURCE = 'cookie_response'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x13

        key: Field | Identifier
        has_payload: OptionalGroupField[0] | Boolean
        payload: OptionalGroupField[0] | list[Byte] = None


    @dataclass(slots=True)
    class PSCustomPayload(Packet):
        """
            Mods and plugins can use this to send their data.
            Minecraft itself uses some plugin channels.
            These internal channels are in the minecraft namespace.
        """
        RESOURCE = 'custom_payload'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x14

        channel: Field | Identifier
        data: Field | list[Byte]

        @classmethod
        def decode(cls, bytes_source: DataPacket) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)
            channel = Identifier.decode(bytes_io)
            data = []
            while True:
                _ = bytes_io.read(1)
                if _ == b'':
                    break
                else:
                    data.append(Byte.decode(bytes_io))
            return cls(channel, data)


    @dataclass(slots=True)
    class PSDebugSampleSubscription(Packet):
        """
            Subscribes to the specified type of debug sample data,
            which is then sent periodically to the client via Debug Sample.
        """
        RESOURCE = 'debug_sample_subscription'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x15

        sample_type: Field | VarInt


    @dataclass(slots=True)
    class PSEditBook(Packet):
        """
            Edit Book
        """
        RESOURCE = 'edit_book'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x16

        slot: Field | VarInt
        entries: Field | list[String]
        title: Field | OptionalString


    @dataclass(slots=True)
    class PSEntityTagQuery(Packet):
        """
            Used when F3+I is pressed while looking at an entity.
        """
        RESOURCE = 'entity_tag_query'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x17

        transaction_id: Field | VarInt
        entity_id: Field | VarInt


    @dataclass(slots=True)
    class PSInteract(Packet):
        """
            This packet is sent from the client to the server when the client attacks
            or right-clicks another entity (a player, minecart, etc).
            A Notchian server only accepts this packet if the entity being attacked/used is visible
            without obstruction and within a 4-unit radius of the player's position.
            The target X, Y, and Z fields represent the difference between the vector location of the cursor
            at the time of the packet and the entity's position.
            Note that middle-click in creative mode is interpreted by the client
            and sent as a Set Creative Mode Slot packet instead.
        """
        RESOURCE = 'interact'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x18

        entity_id: Field | VarInt
        type_: Field | VarInt
        target_x: Field | Optional[Float] = None
        target_y: Field | Optional[Float] = None
        target_z: Field | Optional[Float] = None
        hand: Field | Optional[VarInt] = None
        sneak_key_pressed: Field | Boolean = None

        def __bytes__(self) -> bytes:
            bs = self.entity_id.bytes + self.type_.bytes
            if self.type_.value == 2:
                if self.target_x:
                    bs += self.target_x.bytes
                if self.target_y:
                    bs += self.target_y.bytes
                if self.target_z:
                    bs += self.target_z.bytes

            if self.type_.value in [0, 2]:
                if self.hand:
                    bs += self.hand.bytes

            return bs + self.sneak_key_pressed.bytes

        @classmethod
        def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)
            entity_id = VarInt.decode(bytes_io)
            type_ = VarInt.decode(bytes_io)

            instance = cls(entity_id, type_)

            if type_.value == 2:
                instance.target_x = Float.decode(bytes_io)
                instance.target_y = Float.decode(bytes_io)
                instance.target_z = Float.decode(bytes_io)

            if type_.value in [0, 2]:
                instance.hand = VarInt.decode(bytes_io)

            instance.sneak_key_pressed = Boolean.decode(bytes_io)

            return instance


    @dataclass(slots=True)
    class PSJigsawGenerate(Packet):
        """
            Sent when Generate is pressed on the Jigsaw Block interface.
        """
        RESOURCE = 'jigsaw_generate'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x19

        location: Field | Position
        levels: Field | VarInt
        keep_jigsaws: Field | Boolean


    @dataclass(slots=True)
    class PSKeepAlive(Packet):
        """
            The server will frequently send out a keep-alive (see Clientbound Keep Alive),
            each containing a random ID. The client must respond with the same packet.
        """
        RESOURCE = 'keep_alive'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x1A

        keep_alive_id: Field | Long


    @dataclass(slots=True)
    class PSLockDifficulty(Packet):
        """
            Must have at least op level 2 to use.
            Appears to only be used on singleplayer;
            the difficulty buttons are still disabled in multiplayer.
        """
        RESOURCE = 'lock_difficulty'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x1B

        locked: Field | Boolean


    @dataclass(slots=True)
    class PSMovePlayerPos(Packet):
        """
            Updates the player's XYZ position on the server.
        """
        RESOURCE = 'move_player_pos'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x1C

        x: Field | Double
        feet_y: Field | Double
        z: Field | Double
        flags: Field | Byte

        @property
        def is_on_ground(self) -> bool:
            return self.flags.value & 0x01 > 0

        @property
        def is_pushing_against_wall(self) -> bool:
            return self.flags.value & 0x02 > 0


    @dataclass(slots=True)
    class PSMovePlayerPosRot(Packet):
        """
            A combination of Move Player Rotation and Move Player Position.
        """
        RESOURCE = 'move_player_pos_rot'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x1D

        x: Field | Double
        feet_y: Field | Double
        z: Field | Double
        yaw: Field | Float
        pitch: Field | Float
        flags: Field | Byte

        @property
        def is_on_ground(self) -> bool:
            return self.flags.value & 0x01 > 0

        @property
        def is_pushing_against_wall(self) -> bool:
            return self.flags.value & 0x02 > 0


    @dataclass(slots=True)
    class PSMovePlayerRot(Packet):
        """
            Updates the direction the player is looking in.
        """
        RESOURCE = 'move_player_rot'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x1E

        yaw: Field | Float
        pitch: Field | Float
        flags: Field | Byte

        @property
        def is_on_ground(self) -> bool:
            return self.flags.value & 0x01 > 0

        @property
        def is_pushing_against_wall(self) -> bool:
            return self.flags.value & 0x02 > 0

    
    @dataclass(slots=True)
    class PSMovePlayerStatusOnly(Packet):
        """
            This packet as well as Set Player Position, Set Player Rotation,
            and Set Player Position and Rotation are called the “serverbound movement packets”.
            Vanilla clients will send Move Player Position once every 20 ticks even for a stationary player.
        """
        RESOURCE = 'move_player_status_only'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x1F

        flags: Field | Byte

        @property
        def is_on_ground(self) -> bool:
            return self.flags.value & 0x01 > 0

        @property
        def is_pushing_against_wall(self) -> bool:
            return self.flags.value & 0x02 > 0


    @dataclass(slots=True)
    class PSMoveVehicle(Packet):
        """
            Sent when a player moves in a vehicle.
            Fields are the same as in Set Player Position and Rotation.
            Note that all fields use absolute positioning and do not allow for relative positioning.
        """
        RESOURCE = 'move_vehicle'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x20

        x: Field | Double
        y: Field | Double
        z: Field | Double
        yaw: Field | Float
        pitch: Field | Float
        on_ground: Field | Boolean


    @dataclass(slots=True)
    class PSPaddleBoat(Packet):
        """
            Used to visually update whether boat paddles are turning.
            The server will update the Boat entity metadata to match the values here.
        """
        RESOURCE = 'paddle_boat'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x21

        left_paddle_turning: Field | Boolean
        right_paddle_turning: Field | Boolean


    @dataclass(slots=True)
    class PSPickItemFromBlock(Packet):
        """
            Used to swap out an empty space on the hotbar with the item in the given inventory slot.
            The Notchian client uses this for pick block functionality (middle click) to retrieve items from the inventory.
        """
        RESOURCE = 'pick_item_from_block'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x22

        slot_to_use: Field | VarInt


    @dataclass(slots=True)
    class PSPickItemFromEntity(Packet):
        """
            Pick Item From Entity.
        """
        RESOURCE = 'pick_item_from_entity'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x23

        slot_to_use: Field | VarInt


    @dataclass(slots=True)
    class PSPingRequest(Packet):
        """
            Ping Request.
        """
        RESOURCE = 'ping_request'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x24

        payload: Field | Long


    @dataclass(slots=True)
    class PSPlaceRecipe(Packet):
        """
            This packet is sent when a player clicks a recipe in the crafting book that is craftable (white border).
        """
        RESOURCE = 'place_recipe'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x25

        window_id: Field | Byte
        recipe_id: Field | VarInt
        make_all: Field | Boolean


    @dataclass(slots=True)
    class PSPlayerAbilities(Packet):
        """
            The vanilla client sends this packet when the player starts/stops flying
            with the Flags parameter changed accordingly.
        """
        RESOURCE = 'player_abilities'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x26

        flags: Field | Byte

        @property
        def is_flying(self) -> bool:
            return self.flags.value & 0x02 > 0


    @dataclass(slots=True)
    class PSPlayerAction(Packet):
        """
            Sent when the player mines a block.
            A Notchian server only accepts digging packets with coordinates within a 6-unit radius
            between the center of the block and the player's eyes.
        """
        RESOURCE = 'player_action'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x27

        status: Field | VarInt
        location: Field | Position
        face: Field | Byte
        sequence: Field | VarInt


    @dataclass(slots=True)
    class PSPlayerCommand(Packet):
        """
            Sent by the client to indicate that it has performed certain actions:
            sneaking (crouching), sprinting, exiting a bed, jumping with a horse,
            and opening a horse's inventory while riding it.
        """
        RESOURCE = 'player_command'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x28

        entity_id: Field | VarInt
        action_id: Field | VarInt
        jump_boost: Field | VarInt


    @dataclass(slots=True)
    class PSPlayerInput(Packet):
        """
            Player Input.
        """
        RESOURCE = 'player_input'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x29

        flags: Field | Byte

        @property
        def is_forward(self) -> bool:
            return self.flags.value & ENUMS.PlayerInput.FORWARD.value > 0

        @property
        def is_backward(self) -> bool:
            return self.flags.value & ENUMS.PlayerInput.BACKWARD.value > 0

        @property
        def is_left(self) -> bool:
            return self.flags.value & ENUMS.PlayerInput.LEFT.value > 0

        @property
        def is_right(self) -> bool:
            return self.flags.value & ENUMS.PlayerInput.RIGHT.value > 0

        @property
        def is_jump(self) -> bool:
            return self.flags.value & ENUMS.PlayerInput.JUMP.value > 0

        @property
        def is_sneak(self) -> bool:
            return self.flags.value & ENUMS.PlayerInput.SNEAK.value > 0

        @property
        def is_sprint(self) -> bool:
            return self.flags.value & ENUMS.PlayerInput.SPRINT.value > 0


    @dataclass(slots=True)
    class PSPlayerLoaded(Packet):
        """
            Sent by the client after the server starts sending chunks and the player's chunk has loaded.
        """
        RESOURCE = 'player_loaded'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x2A


    @dataclass(slots=True)
    class PSPong(Packet):
        """
            Response to the clientbound packet (Ping) with the same id.
        """
        RESOURCE = 'pong'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x2B
        id_: Field | Int


    @dataclass(slots=True)
    class PSRecipeBookChangeSettings(Packet):
        """
            Replaces Recipe Book Data, type 1.
        """
        RESOURCE = 'recipe_book_change_settings'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x2C

        book_id: Field | VarInt
        book_open: Field | Boolean
        filter_active: Field | Boolean


    @dataclass(slots=True)
    class PSRecipeBookSeenRecipe(Packet):
        """
            Sent when recipe is first seen in recipe book. Replaces Recipe Book Data, type 0.
        """
        RESOURCE = 'recipe_book_seen_recipe'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x2D

        recipe_id: Field | VarInt


    @dataclass(slots=True)
    class PSRenameItem(Packet):
        """
            Sent as a player is renaming an item in an anvil
            (each keypress in the anvil UI sends a new Rename Item packet).
            If the new name is empty, then the item loses its custom name
            (this is different from setting the custom name to the normal name of the item).
            The item name may be no longer than 50 characters long, and if it is longer than that,
            then the rename is silently ignored.
        """
        RESOURCE = 'rename_item'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x2E

        item_name: Field | String


    @dataclass(slots=True)
    class PSResourcePack(Packet):
        """
            Resource Pack Response.
        """
        RESOURCE = 'resource_pack'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x2F

        uuid: Field | UUID
        result: Field | VarInt


    @dataclass(slots=True)
    class PSSeenAdvancements(Packet):
        """
            Seen Advancements.
        """
        RESOURCE = 'seen_advancements'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x30

        action: Field | VarInt
        tab_id: Field | Optional[Identifier] = None

        def __bytes__(self) -> bytes:
            bs = self.action.bytes
            if self.action.value == ENUMS.AdvancementTab.OPEN_TAB:
                bs += self.tab_id.bytes
            return bs

        @classmethod
        def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
            bytes_io = cls.to_bytes_io(bytes_source)
            action = VarInt.decode(bytes_io)
            if action.value == ENUMS.AdvancementTab.OPEN_TAB:
                tab_id = Identifier.decode(bytes_io)
            else:
                tab_id = None
            return cls(action, tab_id)


    @dataclass(slots=True)
    class PSSelectTrade(Packet):
        """
            When a player selects a specific trade offered by a villager NPC.
        """
        RESOURCE = 'select_trade'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x31

        selected_slot: Field | VarInt


    @dataclass(slots=True)
    class PSSetBeacon(Packet):
        """
            Changes the effect of the current beacon.
        """
        RESOURCE = 'set_beacon'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x32

        primary_effect: Field | OptionalVarInt
        secondary_effect: Field | OptionalVarInt


    @dataclass(slots=True)
    class PSSetCarriedItem(Packet):
        """
            Sent when the player changes the slot selection.
        """
        RESOURCE = 'set_carried_item'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x33

        slot: Field | Short


    @dataclass(slots=True)
    class PSSetCommandBlock(Packet):
        """
            Program command block.
        """
        RESOURCE = 'set_command_block'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x34

        location: Field | Position
        command: Field | String
        mode: Field | VarInt

        # 0x01: Track Output
        # (if false, the output of the previous command will not be stored within the command block);
        # 0x02: Is conditional; 0x04: Automatic.
        flags: Field | Byte


    @dataclass(slots=True)
    class PSSetCommandMinecart(Packet):
        """
            Program command block mincart.
        """
        RESOURCE = 'set_command_minecart'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x35

        entity_id: Field | VarInt
        command: Field | String

        # If false, the output of the previous command will not be stored within the command block.
        track_output: Field | Boolean


    @dataclass(slots=True)
    class PSSetCreativeModeSlot(Packet):
        """
            While the user is in the standard inventory (i.e., not a crafting bench) in Creative mode,
            the player will send this packet.
        """
        RESOURCE = 'set_creative_mode_slot'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x36

        slot: Field | Short
        clicked_item: Field | Slot


    @dataclass(slots=True)
    class PSSetJigsawBlock(Packet):
        """
            Sent when Done is pressed on the Jigsaw Block interface.
        """
        RESOURCE = 'set_jigsaw_block'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x37

        location: Field | Position
        name: Field | Identifier
        target: Field | Identifier
        pool: Field | Identifier
        final_state: Field | String
        joint_type: Field | String
        selection_priority: Field | VarInt
        placement_priority: Field | VarInt


    @dataclass(slots=True)
    class PSSetStructureBlock(Packet):
        """
            Program structure block.
        """
        RESOURCE = 'set_structure_block'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x38

        location: Field | Position
        action: Field | VarInt
        mode: Field | VarInt
        name: Field | String
        offset_x: Field | Byte
        offset_y: Field | Byte
        offset_z: Field | Byte
        size_x: Field | Byte
        size_y: Field | Byte
        size_z: Field | Byte
        mirror: Field | VarInt
        rotation: Field | VarInt
        metadata: Field | String
        integrity: Field | Float
        seed: Field | VarLong
        flags: Field | Byte


    @dataclass(slots=True)
    class PSSignUpdate(Packet):
        """
            This message is sent from the client to the server when the “Done” button is pushed after placing a sign.
            The server only accepts this packet after Open Sign Editor, otherwise this packet is silently ignored.
        """
        RESOURCE = 'sign_update'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x39

        location: Field | Position
        is_front_text: Field | Boolean
        line_1: Field | String
        line_2: Field | String
        line_3: Field | String
        line_4: Field | String


    @dataclass(slots=True)
    class PSSwing(Packet):
        """
            Sent when the player's arm swings.
        """
        RESOURCE = 'swing'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x3A

        hand: Field | VarInt


    @dataclass(slots=True)
    class PSTeleportToEntity(Packet):
        """
            Teleports the player to the given entity. The player must be in spectator mode.
        """
        RESOURCE = 'teleport_to_entity'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x3B

        target_player: Field | UUID


    @dataclass(slots=True)
    class PSUseItemOn(Packet):
        """
            Use Item On
        """
        RESOURCE = 'use_item_on'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x3C

        hand: Field | VarInt
        location: Field | Position
        face: Field | VarInt
        cursor_position_x: Field | Float
        cursor_position_y: Field | Float
        cursor_position_z: Field | Float
        inside_block: Field | Boolean
        world_border_hit: Field | Boolean
        sequence: Field | VarInt


    @dataclass(slots=True)
    class PSUseItem(Packet):
        """
            Sent when pressing the Use Item key (default: right click) with an item in hand.
        """
        RESOURCE = 'use_item'
        STATUS = ENUMS.Status.PLAY
        BOUND_TO = ENUMS.BoundTo.SERVER
        PACKET_ID_HEX = 0x3D

        hand: Field | VarInt
        sequence: Field | VarInt
        yaw: Field | Float
        pitch: Field | Float



class PacketFactoryV769:
    PACKET_MAPPER = {}

    for cls_name, packet_cls in PacketsV769.__dict__.items():
        if cls_name.startswith('__'):
            continue

        try:
            if issubclass(packet_cls, Packet):
                PACKET_MAPPER.setdefault(packet_cls.STATUS, {}).setdefault(packet_cls.BOUND_TO, {})[
                    packet_cls.PACKET_ID_HEX
                ] = packet_cls
        except TypeError:
            ...

    @classmethod
    def get_packet_by_id(cls, status: ENUMS.Status, bound_to: ENUMS.BoundTo, packet_id: int) -> Packet | None:
        """
            获取Packet
        :param status:
        :param bound_to:
        :param packet_id:
        :return:
        """
        try:
            return cls.PACKET_MAPPER[status][bound_to][packet_id]
        except KeyError:
            return None

    @classmethod
    def get_packet_by_dp(cls, status: ENUMS.Status, data_packet: DataPacket) -> Packet | None:
        """
            通过 data_packet 获取 Packet
        :param status:
        :param data_packet:
        :return:
        """
        try:
            return cls.PACKET_MAPPER[status][data_packet.bound_to][data_packet.pid]
        except KeyError:
            return None
