# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~~~~
    
    Log:
         2025-02-08 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.0'

__all__ = [
    'ProtocolEnum',
    'Field', 'FieldsArray', 'DataPacket',
    'Codec', 'Packet',
    'HandshakeProtocols', 'StatusProtocols', 'LoginProtocols', 'ConfigurationProtocols', 'PlayProtocols',
    'ProtocolFactory'
]

import os
import zlib
from dataclasses import dataclass, field as dataclass_field
from enum import Enum, IntEnum
from inspect import isclass
from io import BytesIO
from typing import IO, Any, Tuple, Callable, Iterable
from collections import OrderedDict

from mymcp.data_type import *


class ProtocolEnum:
    """
        定义协议 Enum
    """

    # 767 in Minecraft 1.21
    # 769 in Minecraft 1.21.4
    PROTOCOL_VERSION = 769

    class Direction(Enum):
        CS = 0
        SC = 1
        CLIENT = 0
        SERVER = 1
        CP = 0
        SP = 1

    class Status(Enum):
        """
            当前状态
        """
        HANDSHAKING = 0
        STATUS = 1
        LOGIN = 2
        CONFIGURATION = 3
        PLAY = 4

    class HandShaking(Enum):
        """
            HandShaking Next Status
        """
        STATUS = 1
        LOGIN = 2
        TRANSFER = 3

    class Hand(Enum):
        """
            Hand Type
        """
        MAIN = 0
        OFF = 1

    class Difficulty(Enum):
        """
            difficulty level
        """
        PEACEFUL = 0
        EASY = 1
        NORMAL = 2
        HARD = 3

    class TeleportFlags(Enum):
        """
           A bit field represented as an Int, specifying how a teleportation is to be applied on each axis.
           In the lower 8 bits of the bit field,
           a set bit means the teleportation on the corresponding axis is relative,
           and an unset bit that it is absolute.
        """
        x = 0x0001
        y = 0x0002
        z = 0x0004
        yaw = 0x0008
        pitch = 0x0010
        velocity_x = 0x0020
        velocity_y = 0x0040
        velocity_z = 0x0080

    class ClientStatusAction(Enum):
        """
            0x04 play CS
        """
        PERFORM_RESPAWN = 0
        REQUEST_STATS = 1

    class ClientSettingsChatMode(Enum):
        """
            0x05 play CS
        """
        ENABLED = 0
        COMMANDS_ONLY = 1
        HIDDEN = 2

    class InteractEntityType(Enum):
        """
            0x0d play CS
        """
        INTERACT = 0
        ATTACK = 1
        INTERACT_AT = 2

    class PlayerAction(Enum):
        """
            Digging
        """
        START_DIGGING = 0
        CANCELLED_DIGGING = 1
        FINISHED_DIGGING = 2
        DROP_ITEM_STACK = 3
        DROP_ITEM = 4
        SHOOT_ARROW__FINISH_EATING = 5
        SWAP_ITEM_IN_HAND = 6

    class EntityAction(Enum):
        """
            Sent by the client to indicate that it has performed certain actions:
            sneaking (crouching), sprinting, exiting a bed,
            jumping with a horse, and opening a horse's inventory while riding it.
        """
        START_SNEAKING = 0
        STOP_SNEAKING = 1
        LEAVE_BED = 2
        START_SPRINTING = 3
        STOP_SPRINTING = 4
        START_JUMP_WITH_HORSE = 5
        STOP_JUMP_WITH_HORSE = 6
        OPEN_HORSE_INVENTORY = 7
        START_FLYING_WITH_ELYTRA = 8

    class BookId(Enum):

        CRAFTING = 0
        FURNACE = 1
        BLAST_FURNACE = 2
        SMOKER = 3

    class ResourcePackStatus(Enum):

        SUCCESSFULLY_LOADED = 0
        DECLINED = 1
        FAILED_DOWNLOAD = 2
        ACCEPTED = 3
        DOWNLOADED = 4
        INVALID_URL = 5
        FAILED_TO_RELOAD = 6
        DISCARDED = 7

    class AdvancementTab(Enum):

        OPEN_TAB = 0
        CLOSED_SCREEN = 1

    class CommandBlockMode(Enum):

        SEQUENCE = 0
        AUTO = 1
        REDSTONE = 2

    class StructureBlockAction(Enum):

        UPDATE_DATA = 0
        SAVE_THE_STRUCTURE = 1
        LOAD_THE_STRUCTURE = 2
        DETECT_SIZE = 3

    class StructureBlockMode(Enum):

        SAVE = 0
        LOAD = 1
        CORNER = 2
        DATA = 3

    class StructureBlockMirror(Enum):

        NONE = 0
        LEFT_RIGHT = 1
        FRONT_BACK = 2

    class StructureBlockRotation(Enum):

        NONE = 0
        CLOCKWISE_90 = 1
        CLOCKWISE_180 = 2
        COUNTERCLOCKWISE_90 = 3

    class Face(Enum):
        """
            Face direction
        """
        BOTTOM = 0
        TOP = 1
        NORTH = 2
        SOUTH = 3
        WEST = 4
        EAST = 5

    class Color(Enum):
        """
            Color
        """
        PINK = 0
        BLUE = 1
        RED = 2
        GREEN = 3
        YELLOW = 4
        PURPLE = 5
        WHITE = 6

    class Division(Enum):
        NO_DIVISION = 0
        NOTCHES_6 = 1
        NOTCHES_10 = 2
        NOTCHES_12 = 3
        NOTCHES_20 = 4

    class SpawnPaintingDirection(Enum):
        SOUTH = 0
        WEST = 1
        NORTH = 2
        EAST = 3

    class SculkVibrationSignalIdentifier(Enum):
        BLOCK = 'block'
        ENTITY = 'entity'

    class EntityAnimation(Enum):
        SWING_MAIN_ARM = 0
        TAKE_DAMAGE = 1
        LEAVE_BED = 2
        SWING_OFFHAND = 3
        CRITICAL_EFFECT = 4
        MAGIC_CRITICAL_EFFECT = 5

    class DiggingStatusServer(Enum):
        """
            Digging for Server
        """
        START_DIGGING = 0
        CANCELLED_DIGGING = 1
        FINISHED_DIGGING = 2

    class BlockEntityDataAction(Enum):

        SET_DATA_OF_A_MOB_SPAWNER = 1
        SET_COMMAND_BLOCK_TEXT = 2
        SET_THE_LEVEL = 3
        SET_ROTATION_AND_SKIN_OF_MOB_HEAD = 4
        DECLARE_A_CONDUIT = 5
        SET_BASE_COLOR = 6
        SET_THE_DATA_FOR_A_STRUCTURE_TILE_ENTITY = 7
        SET_THE_DESTINATION_FOR_A_END_GATEWAY = 8
        SET_THE_TEXT_ON_A_SIGN = 9
        DECLARE_A_BED = 11
        SET_DATA_OF_A_JIGSAW_BLOCK = 12
        SET_ITEMS_IN_A_CAMPFIRE = 13
        BEEHIVE_INFORMATION = 14

    class ChatMessagePosition(Enum):

        CHAT_BOX = 0
        SYSTEM_MESSAGE = 1
        GAME_INFO = 2

    class BossBarAction(Enum):

        ADD = 0
        REMOVE = 1
        UPDATE_HEALTH = 2
        UPDATE_TITLE = 3
        UPDATE_STYLE = 4
        UPDATE_FLAGS = 5

    class UpdateScoreAction(Enum):

        CREATE = 0
        REMOVE = 1
        UPDATE = 2

    class UpdateTeamsMethod(Enum):

        CREATE_TEAM = 0
        REMOVE_TEAM = 1
        UPDATE_TEAM_INFO = 2
        ADD_ENTITIES_TO_TEAM = 3
        REMOVE_ENTITIES_FROM_TEAM = 4

    class SoundCategory(Enum):

        MASTER = 0
        MUSIC = 1
        RECORD = 2
        WEATHER = 3
        BLOCK = 4
        HOSTILE = 5
        NEUTRAL = 6
        PLAYER = 7
        AMBIENT = 8
        VOICE = 9

    class GameMode(Enum):

        SURVIVAL = 0
        CREATIVE = 1
        ADVENTURE = 2
        SPECTATOR = 3

    class UnlockRecipesAction(Enum):

        INIT = 0
        ADD = 1
        REMOVE = 2

    class PlayerInfo(Enum):

        ADD_PLAYER = 0
        UPDATE_GAMEMODE = 1
        UPDATE_LATENCY = 2
        UPDATE_DISPLAY_NAME = 3
        REMOVE_PLAYER = 4

    class FacePlayer(Enum):

        FEET = 0
        EYES = 1

    class InteractType(Enum):

        INTERACT = 0
        ATTACH = 1
        INTERACT_AT = 2

    class PlayerInput(Enum):

        FORWARD = 0x01
        BACKWARD = 0x02
        LEFT = 0x04
        RIGHT = 0x08
        JUMP = 0x10
        SNEAK = 0x20
        SPRINT = 0x40

    class EntityType(IntEnum):

        ACACIA_BOAT = 0
        ACACIA_BOAT_WITH_CHEST = 1
        ALLAY = 2
        AREA_EFFECT_CLOUD = 3
        ARMADILLO = 4
        ARMOR_STAND = 5
        ARROW = 6
        AXOLOTL = 7
        BAMBOO_RAFT_WITH_CHEST = 8
        BAMBOO_RAFT = 9
        BAT = 10
        BEE = 11
        BIRCH_BOAT = 12
        BIRCH_BOAT_WITH_CHEST = 13
        BLAZE = 14
        BLOCK_DISPLAY = 15
        BOGGED = 16
        BREEZE = 17
        BREEZE_WIND_CHARGE = 18
        CAMEL = 19
        CAT = 20
        CAVE_SPIDER = 21
        CHERRY_BOAT = 22
        CHERRY_BOAT_WITH_CHEST = 23
        MINECART_WITH_CHEST = 24
        CHICKEN = 25
        COD = 26
        MINECART_WITH_COMMAND_BLOCK = 27
        COW = 28
        CREAKING = 29
        CREEPER = 30
        DARK_OAK_BOAT = 31
        DARK_OAK_BOAT_WITH_CHEST = 32
        DOLPHIN = 33
        DONKEY = 34
        DRAGON_FIREBALL = 35
        DROWNED = 36
        THROWN_EGG = 37
        ELDER_GUARDIAN = 38
        ENDERMAN = 39
        ENDERMITE = 40
        ENDER_DRAGON = 41
        THROWN_ENDER_PEARL = 42
        END_CRYSTAL = 43
        EVOKER = 44
        EVOKER_FANGS = 45
        THROWN_BOTTLE_O_ENCHANTING = 46
        EXPERIENCE_ORB = 47
        EYE_OF_ENDER = 48
        FALLING_BLOCK = 49
        FIREBALL = 50
        FIREWORK_ROCKET = 51
        FOX = 52
        FROG = 53
        MINECART_WITH_FURNACE = 54
        GHAST = 55
        GIANT = 56
        GLOW_ITEM_FRAME = 57
        GLOW_SQUID = 58
        GOAT = 59
        GUARDIAN = 60
        HOGLIN = 61
        MINECART_WITH_HOPPER = 62
        HORSE = 63
        HUSK = 64
        ILLUSIONER = 65
        INTERACTION = 66
        IRON_GOLEM = 67
        ITEM = 68
        ITEM_DISPLAY = 69
        ITEM_FRAME = 70
        JUNGLE_BOAT = 71
        JUNGLE_BOAT_WITH_CHEST = 72
        LEASH_KNOT = 73
        LIGHTNING_BOLT = 74
        LLAMA = 75
        LLAMA_SPIT = 76
        MAGMA_CUBE = 77
        MANGROVE_BOAT = 78
        MANGROVE_BOAT_WITH_CHEST = 79
        MARKER = 80
        MINECART = 81
        MOOSHROOM = 82
        MULE = 83
        OAK_BOAT = 84
        OAK_BOAT_WITH_CHEST = 85
        OCELOT = 86
        OMINOUS_ITEM_SPAWNER = 87
        PAINTING = 88
        PALE_OAK_BOAT = 89
        PALE_OAK_BOAT_WITH_CHEST = 90
        PANDA = 91
        PARROT = 92
        PHANTOM = 93
        PIG = 94
        PIGLIN = 95
        PIGLIN_BRUTE = 96
        PILLAGER = 97
        POLAR_BEAR = 98
        POTION = 99
        PUFFERFISH = 100
        RABBIT = 101
        RAVAGER = 102
        SALMON = 103
        SHEEP = 104
        SHULKER = 105
        SHULKER_BULLET = 106
        SILVERFISH = 107
        SKELETON = 108
        SKELETON_HORSE = 109
        SLIME = 110
        SMALL_FIREBALL = 111
        SNIFFER = 112
        SNOWBALL = 113
        SNOW_GOLEM = 114
        MINECART_WITH_MONSTER_SPAWNER = 115
        SPECTRAL_ARROW = 116
        SPIDER = 117
        SPRUCE_BOAT = 118
        SPRUCE_BOAT_WITH_CHEST = 119
        SQUID = 120
        STRAY = 121
        STRIDER = 122
        TADPOLE = 123
        TEXT_DISPLAY = 124
        PRIMED_TNT = 125
        MINECART_WITH_TNT = 126
        TRADER_LLAMA = 127
        TRIDENT = 128
        TROPICAL_FISH = 129
        TURTLE = 130
        VEX = 131
        VILLAGER = 132
        VINDICATOR = 133
        WANDERING_TRADER = 134
        WARDEN = 135
        WIND_CHARGE = 136
        WITCH = 137
        WITHER = 138
        WITHER_SKELETON = 139
        WITHER_SKULL = 140
        WOLF = 141
        ZOGLIN = 142
        ZOMBIE = 143
        ZOMBIE_HORSE = 144
        ZOMBIE_VILLAGER = 145
        ZOMBIFIED_PIGLIN = 146
        PLAYER = 147
        FISHING_BOBBER = 148


@dataclass
class Field:
    """
        Packet Field
    """
    name: str
    data_type: DataType | Any
    enum: Any = None

    # If last field is a bool to control this field, fill the field name
    optional_field_name: str = None
    optional_condition: Callable = dataclass_field(default=lambda x: x)


@dataclass
class FieldsArray:
    """
        ArrayField
    """
    name: str
    data_types: list[Field]

    # array len field name or default len value
    name_of_num_field: str | int

    # If last field is a bool to control this field, fill the field name
    optional_field_name: str = None
    optional_condition: Callable = dataclass_field(default=lambda x: x)

    def decode(self, bytes_io: IO, n: int) -> list[OrderedDict[str, object]]:

        results = []

        # 遍历 fields
        for _ in range(n):

            # 单个记录
            result = OrderedDict()

            for field in self.data_types:
                if field.optional_field_name is None or field.optional_condition(
                        result.get(field.optional_field_name, False)
                ):
                    if isinstance(field, FieldsArray):

                        # Array INSIDE
                        result[field.name] = field.decode(
                            bytes_io,
                            result.get(
                                field.name_of_num_field
                            ) if type(field.name_of_num_field) is str else field.name_of_num_field,
                        )

                    else:
                        result[field.name] = field.data_type.decode(bytes_io)

            results.append(result)

        return results


@dataclass
class DataPacket:
    length: int
    pid: int
    data: bytes

    def __repr__(self):
        return f"DataPacket(length={self.length}, pid:0x{self.pid:>02x}, data:{self.data[:2000]})"

    def bytes_io(self) -> IO:
        return BytesIO(self.data)

    def to_raw_bytes(self) -> bytes:
        return VarInt.encode(self.pid) + self.data


class Codec:
    """
        编解码器
    """

    SUCCESS = 0
    UNFINISHED = 1
    END = 2

    def __init__(self):
        self.bytes_io = BytesIO()
        self.last_pos = 0
        self.compression_threshold = -1

    def decode_a_packet(self) -> Tuple[int, DataPacket | None]:
        """
            解析Packet
        :return:
        """
        try:
            packet_length = VarInt.decode(self.bytes_io)
        except EOFError:
            return self.END, None
        except ValueError:
            return self.UNFINISHED, None

        try:
            # Without Compressed
            if self.compression_threshold < 0:
                packet_id = VarInt.decode(self.bytes_io)
                data = self.bytes_io.read(packet_length - VarInt.size(packet_id))
                return self.SUCCESS, DataPacket(packet_length, packet_id, data)

            # Compressed
            data_length = VarInt.decode(self.bytes_io)

            if data_length == 0:    # data_length = 0 means not compressed
                return self.SUCCESS, DataPacket(
                    packet_length, VarInt.decode(self.bytes_io), self.bytes_io.read(packet_length - 2)
                )

            _data_io = BytesIO(
                zlib.decompress(
                    self.bytes_io.read(packet_length - VarInt.size(data_length))
                )
            )
            return self.SUCCESS, DataPacket(packet_length, VarInt.decode(_data_io), _data_io.read())

        except (EOFError, zlib.error):
            # 解析 Packet 错误 bytes未传输完成
            return self.UNFINISHED, None

    def decode(self, raw_bytes: bytes) -> Iterable[DataPacket] | None:
        """
            解析数据流
        :param raw_bytes:
        :return:
        """
        # 写入bytes_io
        self.bytes_io.write(raw_bytes)

        # 指针返回初始位置
        self.bytes_io.seek(self.last_pos, os.SEEK_SET)

        # 循环读取至流尾端
        while True:
            flag, data_packet = self.decode_a_packet()
            if flag == self.END:
                # 指针归零 新BytesIO
                self.last_pos = 0
                self.bytes_io = BytesIO()
                break

            elif flag == self.UNFINISHED:
                # 当前流未完成，等待继续写入
                break

            elif flag == self.SUCCESS:
                # 更新指针位置
                self.last_pos = self.bytes_io.tell()
                yield data_packet

        return None

    def encode(self, data_packet: DataPacket) -> bytes:
        bs = data_packet.to_raw_bytes()
        if self.compression_threshold >= 0:
            if len(bs) < self.compression_threshold:
                bs = b'\x00' + bs
            else:
                bs = VarInt.encode(len(bs)) + zlib.compress(bs)
        return VarInt.encode(len(bs)) + bs


class Packet:

    """
        Protocol Packet
    """

    PACKET_ID_HEX = -1
    STATUS = ProtocolEnum.Status.HANDSHAKING
    DIRECT = ProtocolEnum.Direction.CS
    FIELDS: list[Field] = []

    def __repr__(self):
        return f"0x{self.PACKET_ID_HEX:>02x} {self.__class__.__name__}"

    @classmethod
    def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:

        result = OrderedDict()

        for field in cls.FIELDS:

            if field.optional_field_name is None or field.optional_condition(
                    result.get(field.optional_field_name, False)
            ):

                # if field is an Array
                if isinstance(field, FieldsArray):
                    result[field.name] = field.decode(
                        bytes_io,
                        result.get(
                            field.name_of_num_field
                        ) if type(field.name_of_num_field) is str else field.name_of_num_field,
                    )
                else:
                    result[field.name] = field.data_type.decode(bytes_io)

        return result

    @classmethod
    def encode(cls, **kwargs) -> DataPacket:
        bs = bytes()
        for field in cls.FIELDS:
            if field.optional_field_name is None or field.optional_condition(
                kwargs.get(field.optional_field_name, False)
            ):
                if isinstance(field, FieldsArray):
                    raise NotImplementedError('FieldsArray Not Implemented')
                bs += field.data_type.encode(kwargs.get(field.name))
        return DataPacket(len(bs), cls.PACKET_ID_HEX, bs)


from mymcp.protocols.handshake import HandshakeProtocols
from mymcp.protocols.status import StatusProtocols
from mymcp.protocols.login import LoginProtocols
from mymcp.protocols.configuration import ConfigurationProtocols
from mymcp.protocols.play import PlayProtocols


class ProtocolFactory:

    STATUS_MAPPER = {
        ProtocolEnum.Status.HANDSHAKING: HandshakeProtocols,
        ProtocolEnum.Status.STATUS: StatusProtocols,
        ProtocolEnum.Status.LOGIN: LoginProtocols,
        ProtocolEnum.Status.CONFIGURATION: ConfigurationProtocols,
        ProtocolEnum.Status.PLAY: PlayProtocols,
    }

    PROTO_MAPPER = {}

    for _status, status_cls in STATUS_MAPPER.items():
        PROTO_MAPPER[_status] = {
            ProtocolEnum.Direction.CS: {
                cls.PACKET_ID_HEX: cls
                for cls in getattr(status_cls, 'Client2Server').__dict__.values()
                if isclass(cls) and hasattr(cls, 'PACKET_ID_HEX')
            },
            ProtocolEnum.Direction.SC: {
                cls.PACKET_ID_HEX: cls
                for cls in getattr(status_cls, 'Server2Client').__dict__.values()
                if isclass(cls) and hasattr(cls, 'PACKET_ID_HEX')
            }
        }

    @classmethod
    def get_proto(
            cls,
            direction: ProtocolEnum.Direction,
            run_status: ProtocolEnum.Status,
            packet_id: int
    ) -> Packet | None:
        """
            获取Protocol
        :param direction:   packet 方向 server->client | client->server
        :param run_status:  当前状态
        :param packet_id:
        :return:
        """
        return cls.PROTO_MAPPER[run_status][direction].get(packet_id)
