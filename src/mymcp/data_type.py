# -*- coding: utf-8 -*-
"""
    data_type
    ~~~~~~~~~~~~~~~~~~
    Data Type in Minecraft 1.21.4

    Log:
        2025-02-10 0.1.2 Me2sY  优化结构
        2025-02-08 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.2'

__all__ = [
    'DataType',
    'Boolean', 'Byte', 'UnsignedByte',
    'Short', 'UnsignedShort',
    'Int', 'Long', 'UnsignedLong',
    'Float', 'Double',
    'VarInt', 'VarLong',
    'String', 'TextComponent', 'JsonTextComponent',
    'Identifier',

    # Not Finished Yet
    'Slot',

    'NBT', 'Position', 'Angle', 'UUID',
    'BitSet', 'FixedBitSet',
    'Particle', 'EntityMetadata', 'SoundEvent', 'TeleportFlags',

    'IDSet', 'Node',

    'SlotDisplay', 'RecipeDisplay',

    # Advancements
    'CriterionProcess', 'AdvancementProcess', 'AdvancementDisplay', 'Advancement',

    # Chunk
    'ChunkSection', 'ChunkData', 'LightData',
    'decode_palette', 'block_ids', 'Chunk',

]

import os
from dataclasses import dataclass
import json
from io import BytesIO
import math
import pathlib

from mutf8 import decode_modified_utf8
import numpy as np
import pandas as pd
from socket import socket
import struct
from typing import IO, Sized, Iterable, Tuple
import uuid

from pynbt import NBTFile


# Block IDS

block_ids = {}
with pathlib.Path(__file__).parent.joinpath('blocks.json').open('r') as f:
    blocks = json.load(f)
    for key, value in blocks.items():
        for ind, item in enumerate(value['states']):
            block_ids[item['id']] = {
                'name': key,
                'index': ind,
                'item': item
            }


class DataType:
    """
        Minecraft Data Type
    """

    STRUCT_ALIGN = '>'
    STRUCT_FORMAT = ''
    BYTES_LENGTH = 0
    PY_OBJ = object

    @classmethod
    def encode(cls, value: PY_OBJ) -> bytes:
        """
            字节化
        :param value:
        :return:
        """
        return struct.pack(cls.STRUCT_ALIGN + cls.STRUCT_FORMAT, value)

    @classmethod
    def decode(cls, bytes_io: IO) -> PY_OBJ:
        """
            解析至python数据对象
        :param bytes_io:
        :return:
        """
        return struct.unpack(cls.STRUCT_ALIGN + cls.STRUCT_FORMAT, bytes_io.read(cls.BYTES_LENGTH))[0]


class Boolean(DataType):
    """
        Either False or True
        True is encoded as 0x01, False as 0x00.
    """

    STRUCT_FORMAT = '?'
    BYTES_LENGTH = 1
    PY_OBJ = bool


class Byte(DataType):
    """
        An integer between -128 and 127
        Signed 8-bit integer, two's complement
    """
    STRUCT_FORMAT = 'b'
    BYTES_LENGTH = 1
    PY_OBJ = int


class UnsignedByte(DataType):
    """
        An integer between 0 and 255
        Unsigned 8-bit integer
    """

    STRUCT_FORMAT = 'B'
    BYTES_LENGTH = 1
    PY_OBJ = int


class Short(DataType):
    """
        An integer between -32768 and 32767
        Signed 16-bit integer, two's complement
    """

    STRUCT_FORMAT = 'h'
    BYTES_LENGTH = 2
    PY_OBJ = int


class UnsignedShort(DataType):
    """
        An integer between 0 and 65535
        Unsigned 16-bit integer
    """

    STRUCT_FORMAT = 'H'
    BYTES_LENGTH = 2
    PY_OBJ = int


class Int(DataType):
    """
        An integer between -2147483648 and 2147483647
        Signed 32-bit integer, two's complement
    """

    STRUCT_FORMAT = 'i'
    BYTES_LENGTH = 4
    PY_OBJ = int


class Long(DataType):
    """
        An integer between -9223372036854775808 and 9223372036854775807
        Signed 64-bit integer, two's complement
    """

    STRUCT_FORMAT = 'q'
    BYTES_LENGTH = 8
    PY_OBJ = int


class UnsignedLong(DataType):
    """
        An integer between -9223372036854775808 and 9223372036854775807
        Signed 64-bit integer, two's complement
    """

    STRUCT_FORMAT = 'Q'
    BYTES_LENGTH = 8
    PY_OBJ = int


class Float(DataType):
    """
        A single-precision 32-bit IEEE 754 floating point number
    """
    STRUCT_FORMAT = 'f'
    BYTES_LENGTH = 4
    PY_OBJ = float


class Double(DataType):
    """
        A double-precision 64-bit IEEE 754 floating point number
    """
    STRUCT_FORMAT = 'd'
    BYTES_LENGTH = 8
    PY_OBJ = float


class VarInt(DataType):
    """
        Minecraft VarInt
        An integer between -2147483648 and 2147483647
    """

    MAX_BYTES = 5
    INT_BITS = 32
    READ_FORMAT = 'i'

    STRUCT_FORMAT = 'B'
    PY_OBJ = int

    SIZE_TABLE = {2 ** (i * 7): i for i in range(1, 13)}

    @classmethod
    def decode(cls, bytes_from: IO | socket) -> PY_OBJ:
        """
            VarInt 解析
        :param bytes_from:
        :return:
        """

        number = 0
        bytes_encountered = 0

        while True:
            try:
                byte = bytes_from.read(1)
            except:
                byte = bytes_from.recv(1)
            if len(byte) < 1:
                raise EOFError("Unexpected end of message.")

            byte = ord(byte)
            number |= (byte & 0x7F) << 7 * bytes_encountered
            if not byte & 0x80:
                break

            bytes_encountered += 1
            if bytes_encountered == cls.MAX_BYTES:
                raise ValueError("Tried to read too long of a VarInt")
        return struct.unpack(
            cls.STRUCT_ALIGN + cls.READ_FORMAT,
            int(number).to_bytes(int(cls.INT_BITS / 8), 'big')
        )[0]

    @classmethod
    def encode(cls, value: int) -> bytes:
        """
            python >> 负数补1情况
        :param value:
        :return:
        """
        _bytes = bytes()
        value = int(value)
        times = 0
        while True:
            times += 1
            byte = value & 0x7F
            value = (value >> 7) & int((2 ** (cls.INT_BITS - 7 * times) - 1))
            _bytes += struct.pack(cls.STRUCT_ALIGN + cls.STRUCT_FORMAT, byte | (0x80 if value > 0 else 0))
            if value == 0:
                break
        return _bytes

    @classmethod
    def size(cls, value: int) -> int:
        """
            VarInt Size
        :param value:
        :return:
        """
        for max_value, size in cls.SIZE_TABLE.items():
            if value < max_value:
                return size
        raise ValueError("Integer too large")


class VarLong(VarInt):

    MAX_BYTES = 10
    INT_BITS = 32
    READ_FORMAT = 'l'


class String(DataType):
    """
        A sequence of Unicode scalar values
        UTF-8 string prefixed with its size in bytes as a VarInt.
        Maximum length of n characters, which varies by context;
        up to n × 4 bytes can be used to encode n characters and both of those limits are checked.
        Maximum n value is 32767.
        The + 3 is due to the max size of a valid length VarInt.
    """

    PY_OBJ = str
    CODE_TYPE = 'utf-8'

    @classmethod
    def decode(cls, bytes_io: IO) -> PY_OBJ:
        return bytes_io.read(VarInt.decode(bytes_io)).decode(cls.CODE_TYPE)

    @classmethod
    def encode(cls, value: PY_OBJ) -> bytes:
        _bytes = value.encode(cls.CODE_TYPE)
        return VarInt.encode(len(_bytes)) + _bytes


class TextComponent(DataType):
    """
        Encoded as a NBT Tag, with the type of tag used depending on the case:
            As a String Tag: For components only containing text (no styling, no events etc.).
            As a Compound Tag: Every other case.
    """

    TAG_STRING = b'\x08'

    @classmethod
    def decode(cls, bytes_io: IO) -> str | NBTFile:
        if bytes_io.read(1) == cls.TAG_STRING:
            l = struct.unpack('>H', bytes_io.read(2))[0]
            text = decode_modified_utf8(bytes_io.read(l))
            return text
        else:
            bytes_io.seek(-1, os.SEEK_CUR)
            return NBT.decode(bytes_io)


class JsonTextComponent(DataType):
    """
        JSON Text Component
    """
    PY_OBJ = dict

    @classmethod
    def decode(cls, bytes_io: IO) -> PY_OBJ:
        return json.loads(String.decode(bytes_io))

    @classmethod
    def encode(cls, value: PY_OBJ) -> bytes:
        return String.encode(json.dumps(value))


class Identifier(String):
    """
        Identifier Type
        Encoded as a String with max length of 32767.
    """


class SoundEvent(DataType):

    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['sound_name'] = Identifier.decode(bytes_io)
        res['has_fixed_range'] = Boolean.decode(bytes_io)
        if res['has_fixed_range']:
            res['fixed_range'] = Float.decode(bytes_io)
        return res

    @classmethod
    def encode(cls, value: dict) -> bytes:
        """
            {sound_name: str, has_fixed_range: bool, fixed_range: Float}
        :param value:
        :return:
        """
        bs = bytes()
        bs += Identifier.encode(value['sound_name'])
        bs += Boolean.encode(value['has_fixed_range'])
        if value['has_fixed_range']:
            bs += Float.encode(value['fixed_range'])
        return bs


class TrimMaterial(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['asset_name'] = String.decode(bytes_io)
        res['ingredient'] = VarInt.decode(bytes_io)
        res['item_model_index'] = Float.decode(bytes_io)

        n = VarInt.decode(bytes_io)
        res['override'] = []
        for _ in range(n):
            res['override'].append([
                VarInt.decode(bytes_io),
                String.decode(bytes_io)
            ])
        res['description'] = TextComponent.decode(bytes_io)
        return res


class TrimPattern(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['asset_name'] = String.decode(bytes_io)
        res['template_item'] = VarInt.decode(bytes_io)
        res['description'] = TextComponent.decode(bytes_io)
        res['decal'] = Boolean.decode(bytes_io)
        return res


class UUID(DataType):
    """
        A UUID
    """

    BYTES_LENGTH = 16
    PY_OBJ = uuid.UUID

    @classmethod
    def decode(cls, bytes_io: IO) -> PY_OBJ:
        """
            解码UUID
        :param bytes_io:
        :return:
        """
        return cls.PY_OBJ(bytes=bytes_io.read(cls.BYTES_LENGTH))

    @classmethod
    def encode(cls, value: PY_OBJ) -> bytes:
        """
            转码UUID
        :param value:
        :return:
        """
        return value.bytes


class Position(DataType):
    """
        An integer/block position: x (-33554432 to 33554431), z (-33554432 to 33554431) y (-2048 to 2047),
        x as a 26-bit integer,
        followed by z as a 26-bit integer (all signed, two's complement).
        followed by y as a 12-bit integer,
    """

    BYTES_LENGTH = 8

    def __init__(self, x: int = None, y: int = None, z: int = None):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other: 'Position'):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self):
        return f"Position({self.x}, {self.y}, {self.z})"

    @classmethod
    def decode(cls, bytes_io: IO) -> "Position":
        """
            Get a Position object from bytes.
        :param bytes_io:
        :return:
        """
        pos_long = UnsignedLong.decode(bytes_io)
        x = int(pos_long >> 38)
        z = int((pos_long >> 12) & 0x3FFFFFF)
        y = int(pos_long & 0xFFF)

        if x >= pow(2, 25):
            x -= pow(2, 26)
        if y >= pow(2, 11):
            y -= pow(2, 12)
        if z >= pow(2, 25):
            z -= pow(2, 26)

        return cls(x, y, z)

    @classmethod
    def encode(cls, value: 'Position' | Sized) -> bytes:
        """
            Postion to bytes
        :param value:
        :return:
        """
        if isinstance(value, Position):
            x = value.x
            y = value.y
            z = value.z
        else:
            if len(value) != 3:
                raise ValueError(f"{value} items count != 3")
            x, y, z = value

        return UnsignedLong.encode((((x & 0x3FFFFFF) << 38) | ((z & 0x3FFFFFF) << 12) | (y & 0xFFF)))


class IDSet(DataType):
    """
        Represents a set of IDs in a certain registry (implied by context),
        either directly (enumerated IDs) or indirectly (tag name).

        value: {_type:int, tag_name:str, ids:[]}
    """
    PY_OBJ = dict

    @classmethod
    def decode(cls, bytes_io: IO) -> PY_OBJ:
        _type = VarInt.decode(bytes_io)
        _tag_name = None
        _ids = []

        if _type == 0:
            _tag_name = Identifier.decode(bytes_io)
        else:
            for _ in range(_type - 1):
                _ids.append(VarInt.decode(bytes_io))

        return {
            '_type': _type,
            'tag_name': _tag_name,
            'ids': _ids,
        }

    @classmethod
    def encode(cls, value: PY_OBJ) -> bytes:
        bs = VarInt.encode(value['_type'])
        if value['_type'] == 0:
            bs += Identifier.encode(value['tag_name'])
        else:
            for _ in range(value['_type'] - 1):
                bs += VarInt.encode(value['ids'][_])
        return bs


class NBT(DataType):
    """
        NBT Type
    """
    @classmethod
    def decode(cls, bytes_io: IO, network_nbt: bool = True) -> NBTFile:
        """
            Network NBT
            Since 1.20.2 (Protocol 764) NBT sent over the network has been updated
            to exclude the name from the root TAG_COMPOUND
            >= 1.20.2 Protocol 764 TAG_Compound With NO Length of Name
            So pyNBT With some error HERE.
        :param bytes_io:
        :param network_nbt:
        :return:
        """
        if network_nbt:
            pos = bytes_io.tell()

            fb = bytes_io.read(1)
            if fb == b'\x00':
                return NBTFile()

            else:
                bytes_io.seek(pos)

            # Insert Length of Name in stream
            _bytes_io = BytesIO(b'\n\00\00' + bytes_io.read()[1:])
            _nbt_file = NBTFile(_bytes_io)
            bytes_io.seek(pos + _bytes_io.tell() - 2, 0)
        else:
            _nbt_file = NBTFile(bytes_io)
        return _nbt_file

    @classmethod
    def encode(cls, value) -> bytes:
        ...


class Slot(DataType):
    """
        Slot Type
        The Slot data structure defines how an item is represented when inside an inventory window of any kind, such as a chest or furnace.
        TODO encode
    """
    class BlockPredicate(DataType):

        class BlockProperty(DataType):
            @classmethod
            def decode(cls, bytes_io: IO) -> dict:
                res = dict()
                name = String.decode(bytes_io)
                is_exact_match = Boolean.decode(bytes_io)

                res['name'] = name
                res['is_exact_match'] = is_exact_match

                if is_exact_match:
                    res['exact_value'] = String.decode(bytes_io)
                else:
                    res['min_value'] = String.decode(bytes_io)
                    res['max_value'] = String.decode(bytes_io)

                return res

        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['has_blocks'] = Boolean.decode(bytes_io)
            if res['has_blocks']:
                res['blocks'] = IDSet.decode(bytes_io)

            res['has_properties'] = Boolean.decode(bytes_io)
            if res['has_properties']:
                res['properties'] = []
                prop_n = VarInt.decode(bytes_io)
                for _ in range(prop_n):
                    res['properties'].append(cls.BlockProperty.decode(bytes_io))

            res['has_nbt'] = Boolean.decode(bytes_io)
            if res['has_nbt']:
                res['nbt'] = NBT.decode(bytes_io)

            return res

    class IDOrSoundEvent(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['_id'] = VarInt.decode(bytes_io)
            if res['_id'] == 0:
                res['sound'] = SoundEvent.decode(bytes_io)
            else:
                res['_id'] += 1
            return res

    class IDOrTrimMaterial(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['_id'] = VarInt.decode(bytes_io)
            if res['_id'] == 0:
                res['material'] = TrimMaterial.decode(bytes_io)
            else:
                res['_id'] += 1
            return res

    class IDOrTrimPattern(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['_id'] = VarInt.decode(bytes_io)
            if res['_id'] == 0:
                res['pattern'] = TrimPattern.decode(bytes_io)
            else:
                res['_id'] += 1
            return res

    class ConsumeEffect(DataType):

        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['_type'] = VarInt.decode(bytes_io)
            if res['_type'] == 0:
                # Error In Docs
                ...
            elif res['_type'] == 1:
                res['effects'] = IDSet.decode(bytes_io)

            elif res['_type'] == 3:
                res['diameter'] = Float.decode(bytes_io)

            elif res['_type'] == 4:
                res['sound'] = SoundEvent.decode(bytes_io)

            return res

    class Rule(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['blocks'] = IDSet.decode(bytes_io)
            res['has_speed'] = Boolean.decode(bytes_io)
            if res['has_speed']:
                res['speed'] = Float.decode(bytes_io)
            res['has_correct_drop_for_blocks'] = Boolean.decode(bytes_io)
            if res['has_correct_drop_for_blocks']:
                res['correct_drop_for_blocks'] = Boolean.decode(bytes_io)
            return res

    class Equipped(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            # 0: mainhand, 1: feet, 2: legs, 3: chest, 4: head, 5: offhand, 6: body
            res['slot'] = VarInt.decode(bytes_io)
            res['equip_sound'] = Slot.IDOrSoundEvent.decode(bytes_io)

            res['has_model'] = Boolean.decode(bytes_io)
            if res['has_model']:
                res['model'] = Identifier.decode(bytes_io)

            res['has_camera_overlay'] = Boolean.decode(bytes_io)
            if res['has_camera_overlay']:
                res['camera_overlay'] = Identifier.decode(bytes_io)

            res['has_allowed_entities'] = Boolean.decode(bytes_io)
            if res['has_allowed_entities']:
                res['allowed_entities'] = IDSet.decode(bytes_io)

            res['dispensable'] = Boolean.decode(bytes_io)
            res['swappable'] = Boolean.decode(bytes_io)
            res['damage_on_hurt'] = Boolean.decode(bytes_io)
            return res

    class PotionEffect(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['type_id'] = VarInt.decode(bytes_io)
            res['amplifier'] = VarInt.decode(bytes_io)
            res['duration'] = VarInt.decode(bytes_io)
            res['ambient'] = Boolean.decode(bytes_io)
            res['show_particles'] = Boolean.decode(bytes_io)
            res['show_icon'] = Boolean.decode(bytes_io)
            res['has_hidden_effect'] = Boolean.decode(bytes_io)
            if res['has_hidden_effect']:
                res['hidden_effect'] = cls.decode(bytes_io)
            return res

    class PotionContents(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()

            res['has_potion_id'] = Boolean.decode(bytes_io)
            if res['has_potion_id']:
                res['potion_id'] = VarInt.decode(bytes_io)

            res['has_custom_color'] = Boolean.decode(bytes_io)
            if res['has_custom_color']:
                res['custom_color'] = Int.decode(bytes_io)

            n = VarInt.decode(bytes_io)
            res['custom_effects'] = []
            for _ in range(n):
                res['custom_effects'].append(Slot.PotionEffect.decode(bytes_io))

            res['custom_name'] = String.decode(bytes_io)
            return res

    class Instrument(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['sound_event'] = Slot.IDOrSoundEvent.decode(bytes_io)
            res['use_duration'] = Float.decode(bytes_io)
            res['range'] = Float.decode(bytes_io)
            res['description'] = TextComponent.decode(bytes_io)
            return res

    class IDOrInstrument(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['_id'] = VarInt.decode(bytes_io)
            if res['_id'] == 0:
                res['instrument'] = Slot.Instrument.decode(bytes_io)
            else:
                res['_id'] += 1
            return res

    class JukeboxSong(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['sound_event'] = Slot.IDOrSoundEvent.decode(bytes_io)
            res['description'] = TextComponent.decode(bytes_io)
            res['duration'] = Float.decode(bytes_io)
            res['output'] = VarInt.decode(bytes_io)     # The output strength given by a comparator. Between 0 and 15.
            return res

    class IDOrJukeboxSong(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['_id'] = VarInt.decode(bytes_io)
            if res['_id'] == 0:
                res['jukebox_song'] = Slot.JukeboxSong.decode(bytes_io)
            else:
                res['_id'] += 1
            return res

    class JukeboxPlayable(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['direct_mode'] = Boolean.decode(bytes_io)
            if res['direct_mode']:
                res['jukebox_song'] = Slot.IDOrJukeboxSong.decode(bytes_io)
            else:
                res['jukebox_song_name'] = Identifier.decode(bytes_io)
            res['show_in_tooltip'] = Boolean.decode(bytes_io)
            return res

    class FireworkExplosion(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['shape'] = VarInt.decode(bytes_io)

            noc = VarInt.decode(bytes_io)
            res['colors'] = []
            for _ in range(noc):
                res['colors'].append(Int.decode(bytes_io))

            nof = VarInt.decode(bytes_io)
            res['fade_colors'] = []
            for _ in range(nof):
                res['fade_colors'].append(Int.decode(bytes_io))

            res['has_trail'] = Boolean.decode(bytes_io)
            res['has_twinkler'] = Boolean.decode(bytes_io)
            return res

    class BannerPatterns(DataType):
        @classmethod
        def decode(cls, bytes_io: IO) -> dict:
            res = dict()
            res['layers'] = []
            nol = VarInt.decode(bytes_io)
            for _ in range(nol):
                _layer = dict()
                _layer['pattern_type'] = VarInt.decode(bytes_io)
                if _layer['pattern_type'] == 0:
                    _layer['asset_id'] = Identifier.decode(bytes_io)
                    _layer['translation_key'] = String.decode(bytes_io)
                _layer['color'] = VarInt.decode(bytes_io)
                res['layers'].append(_layer)
            return res

    @dataclass
    class Optional:
        data_type: list

        def decode(self, bytes_io: IO) -> Tuple[bool, list]:
            opt = Boolean.decode(bytes_io)
            if opt:
                res = []
                for _dtype in self.data_type:
                    res.append(_dtype.decode(bytes_io))
                return True, res
            else:
                return False, []


    @dataclass
    class Array:
        data_type: list

        def decode(self, bytes_io: IO) -> list[list]:
            n = VarInt.decode(bytes_io)
            res = []
            for _ in range(n):
                array_res = []
                for _dtype in self.data_type:
                    array_res.append(_dtype.decode(bytes_io))
                res.append(array_res)
            return res

    STRUCTURED_COMPONENTS = {

        # custom_data
        0: [NBT],

        # Maximum stack size for the item.	 Ranges from 1 to 99
        1: [VarInt],

        # The maximum damage the item can take before breaking
        2: [VarInt],

        # The current damage of the item
        3: [VarInt],

        # unbreakable
        4: [Boolean],

        # custom_name
        5: [TextComponent],

        # item_name
        6: [TextComponent],

        # Item's model
        7: [Identifier],

        # Item's lore
        8: [Array(data_type=[TextComponent])],

        # Item's rarity. This affects the default color of the item's name
        9: [VarInt],

        # The enchantments of the item
        10: [Array(data_type=[VarInt, VarInt]), Boolean],

        # can_place_on  List of blocks this block can be placed on when in adventure mode
        11: [Array(data_type=[BlockPredicate]), Boolean],

        # can_break  List of blocks this item can break when in adventure mode
        12: [Array(data_type=[BlockPredicate]), Boolean],

        # The attribute modifiers of the item
        13: [Array(data_type=[
            VarInt, UUID, String, Double, VarInt, VarInt
        ]), Boolean],

        # custom_model_data
        14: [VarInt],

        # hide_additional_tooltip
        15: [],

        # hide_tooltip
        16: [],

        # repair_cost
        17: [VarInt],

        # creative_slot_lock
        18: [],

        # enchantment_glint_override
        19: [VarInt],

        # intangible_projectile
        20: [],

        # Makes the item restore the player's hunger bar when consumed
        21: [VarInt, Float, Boolean],

        # Makes the item consumable
        22: [Float, VarInt, IDOrSoundEvent, Boolean, Array(data_type=[ConsumeEffect])],

        # TODO
        # use_remainder
        23: [],  # SLOT

        # TODO
        # cooldown group not found. Maybe Error in Docs
        24: [],

        # damage_resistant
        25: [Identifier],

        # Alters the speed at which this item breaks certain blocks
        26: [Array(data_type=[Rule]), Float, VarInt],

        # Allows the item to be enchanted by an enchanting table
        27: [VarInt],

        # Allows the item to be equipped by the player
        28: [Equipped],

        # Items that can be combined with this item in an anvil to repair it
        29: [IDSet],

        # glider Makes the item function like elytra
        30: [],

        # Custom textures for the item tooltip.
        31: [Identifier],

        # Makes the item function like a totem of undying.
        32: [Array(data_type=[ConsumeEffect])],

        # The enchantments stored in this enchanted book.
        33: [Array(data_type=[VarInt, VarInt]), Boolean],

        # Color of dyed leather armor.
        34: [Int, Boolean],

        # Color of the markings on the map item model
        35: [Int],

        # The ID of the map
        36: [VarInt],

        # Icons present on a map
        37: [NBT],

        # map_post_processing
        38: [VarInt],   # 0 Lock 1 Scale

        # TODO
        # Projectiles loaded into a charged crossbow
        39: [], # Array Slot

        # TODO
        # Contents of a bundle.
        40: [], # Array Slot

        # Visual and effects of a potion item
        41: [PotionContents],

        # Effects granted by a suspicious stew
        42: [Array(data_type=[VarInt, VarInt])],

        # Content of a writable book.
        43: [Array(data_type=[String, Optional(data_type=[String])])],

        # Content of a written and signed book
        44: [
            String,
            Optional(data_type=[String]),
            String, VarInt,
            Array(data_type=[TextComponent, Optional(data_type=[TextComponent])]),
            Boolean
        ],

        # Armor's trim pattern and color
        45: [IDOrTrimMaterial, IDOrTrimPattern, Boolean],

        # State of the debug stick
        46: [NBT],

        # Data for the entity to be created from this item
        47: [NBT],

        # Data of the entity contained in this bucket
        48: [NBT],

        # Data of the block entity to be created from this item
        49: [NBT],

        # The sound played when using a goat horn
        50: [IDOrInstrument],

        # Amplifier for the effect of an ominous bottle. Between 0 and 4
        51: [VarInt],

        # jukebox_playable
        52: [JukeboxPlayable],

        # The recipes this knowledge book unlocks
        53: [NBT],

        # lodestone_tracker
        54: [Optional(data_type=[Identifier, Position]), Boolean],

        # Properties of a firework star
        55: [FireworkExplosion],

        # Properties of a firework
        56: [VarInt, Array(data_type=[FireworkExplosion])],

        # Game Profile of a player's head
        57: [
            Optional(data_type=[String]),
            Optional(data_type=[UUID]),
            Array(data_type=[
                String,
                String,
                Optional(data_type=[String])
        ])],

        # note_block_sound
        58: [Identifier],

        # banner_patterns
        59: [BannerPatterns],

        # base_color
        60: [VarInt],

        # pot_decorations
        61: [Array(data_type=[VarInt])],

        # TODO
        # container
        62: [],

        # block_state
        63: [Array(data_type=[String, String])],

        # Bees inside a hive
        64: [Array(data_type=[NBT, VarInt, VarInt])],

        # lock
        65: [NBT],

        # container_loot
        66: [NBT]
    }


    @classmethod
    def decode(cls, bytes_io: IO):
        item_count = VarInt.decode(bytes_io)
        if item_count == 0:
            return {
                'item_count': 0
            }

        item_id = VarInt.decode(bytes_io)
        number_of_components_to_add = VarInt.decode(bytes_io)
        number_of_components_to_remove = VarInt.decode(bytes_io)

        components_to_add = []
        for _ in range(number_of_components_to_add):
            component_type = VarInt.decode(bytes_io)
            components = []
            data_struct = cls.STRUCTURED_COMPONENTS.get(component_type, None)
            if data_struct:
                for _dtype in data_struct:
                    components.append(_dtype.decode(bytes_io))
            components_to_add.append(components)

        components_to_remove = []
        for _ in range(number_of_components_to_remove):
            components_to_remove.append(VarInt.decode(bytes_io))

        return {
            'item_count': item_count,
            'item_id': item_id,
            'number_of_components_to_add': number_of_components_to_add,
            'components_to_add': components_to_add,
            'number_of_components_to_remove': number_of_components_to_remove,
            'components_to_remove': components_to_remove
        }

    @classmethod
    def encode(cls, value: dict) -> bytes:
        """
            TODO
            Oh God...
        :param value:
        :return:
        """


class Angle(DataType):

    """
        A rotation angle in steps of 1/256 of a full turn
        Whether or not this is signed does not matter, since the resulting angles are the same.
    """

    STRUCT_FORMAT = 'b'
    BYTES_LENGTH = 1
    PY_OBJ = int


class BitSet(DataType):
    """
        A length-prefixed bit set.
    """

    @classmethod
    def decode(cls, bytes_io: IO) -> [int]:
        """
            Decode bytes into a list of ints(long).
        :param bytes_io:
        :return:
        """
        length = VarInt.decode(bytes_io)
        return [Long.decode(bytes_io) for _ in range(length)]

    @classmethod
    def encode(cls, value: list[int]) -> bytes:
        """
            Encode a list of ints(long).
        :param value:
        :return:
        """
        _bytes = VarInt.encode(len(value))
        for v in value:
            _bytes += Long.encode(v)
        return _bytes


class FixedBitSet(DataType):
    """
        Bit sets of type Fixed BitSet (n) have a fixed length of n bits, encoded as ceil(n / 8) bytes.
        Note that this is different from BitSet, which uses longs.
    """

    COUNT = 0

    @classmethod
    def decode(cls, bytes_io: IO) -> bytes:
        return bytes_io.read(3)

    @classmethod
    def encode(cls, value: str) -> bytes:
        return b'\x00' * math.ceil(cls.COUNT / 8)


class Particle(DataType):
    """
        minecraft:particle_type
        https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Particles
    """
    TYPE_MAP = {
        # minecraft:block BlockState
        1: [VarInt],

        # minecraft:block_marker BlockState
        2: [VarInt],

        # minecraft:dust RGB Scale
        # The color, encoded as 0xRRGGBB; top bits are ignored.
        # Scale. The scale, will be clamped between 0.01 and 4.
        13: [Int, Float],

        # minecraft:dust_color_transition   From To RGB  Scale
        14: [Int, Int, Float],

        # minecraft:entity_effect   The ARGB components of the color encoded as an Int
        20: [Int],

        # minecraft:falling_dust BlockState
        28: [VarInt],

        # minecraft:sculk_charge	Roll How much the particle will be rotated when displayed.
        35: [Float],

        # minecraft:item	The item that will be used.
        44: [Slot],

        # minecraft:vibration
        # Position Source Type	VarInt	The type of the vibration source (0 for `minecraft:block`, 1 for `minecraft:entity`)
        # Block Position    Position    The position of the block the vibration originated from. Only present if Position Type is minecraft:block.
        # Entity ID VarInt  The ID of the entity the vibration originated from. Only present if Position Type is minecraft:entity.
        # Entity eye height Float   The height of the entity's eye relative to the entity. Only present if Position Type is minecraft:entity.
        # Ticks	VarInt	The amount of ticks it takes for the vibration to travel from its source to its destination.
        45: [VarInt, Position, VarInt, Float, VarInt],

        # minecraft:shriek	The time in ticks before the particle is displayed
        99: [VarInt],

        # minecraft:dust_pillar	 BlockState The ID of the block state.
        105: [VarInt],

    }

    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        """
            解析particle
        :param bytes_io:
        :return:
        """
        _id = VarInt.decode(bytes_io)
        return {
            'id': _id,
            'data': [type_cls.decode(bytes_io) for type_cls in cls.TYPE_MAP.get(_id, [])]
        }

    @classmethod
    def encode(cls, value: dict) -> bytes:
        """
            转码
        :param value: {'id': Particle_ID, 'data': []}
        :return:
        """
        _id = value['id']
        data_bytes = VarInt.encode(_id)

        for ind, type_cls in enumerate(cls.TYPE_MAP.get(_id, [])):
            data_bytes += type_cls.encode(value['data'][ind])

        return data_bytes


class EntityMetadata(DataType):
    """
        Minecraft entity metadata
    """

    TYPE_MAP = {
        index: cls for index, cls in enumerate(
            [
                [Byte],
                [VarInt],
                [VarLong],
                [Float],
                [String],
                [TextComponent],
                [Boolean, TextComponent],
                [Slot],
                [Boolean],
                [Float, Float, Float],      # 9 Rotation
                [Position],
                [Boolean, Position],        # 11 OptPosition
                [VarInt],       # 12 Direction Down = 0, Up = 1, North = 2, South = 3, West = 4, East = 5
                [Boolean, UUID],    # 13 OptUUID
                [VarInt],       # 14 OptBlockID
                [VarInt],       # 15
                [NBT],
                [Particle],
                [],     # HardCode In Functions Particles
                [VarInt, VarInt, VarInt],   # 19 villager type, villager profession, level (See below.)
                [VarInt],       # 20 0 for absent; 1 + actual value otherwise. Used for entity IDs.
                [VarInt],       # 21 VarInt Enum	STANDING = 0, FALL_FLYING = 1, SLEEPING = 2, SWIMMING = 3, SPIN_ATTACK = 4, SNEAKING = 5, LONG_JUMPING = 6, DYING = 7, CROAKING = 8, USING_TONGUE = 9, SITTING = 10, ROARING = 11, SNIFFING = 12, EMERGING = 13, DIGGING = 14, (1.21.3: SLIDING = 15, SHOOTING = 16, INHALING = 17)
                [VarInt],
                [Identifier],
                [VarInt],
                [Boolean, Identifier, Position],    # 25 dimension identifier, position; only if the Boolean is set to true.
                [Identifier],
                [VarInt],       # 27 IDLING = 0, FEELING_HAPPY = 1, SCENTING = 2, SNIFFING = 3, SEARCHING = 4, DIGGING = 5, RISING = 6
                [VarInt],       # 28 IDLE = 0, ROLLING = 1, SCARED = 2, UNROLLING = 3
                [Float, Float, Float],          # 29 Vector3 x, y, z
                [Float, Float, Float, Float],   # 30 Quaternion x, y, z, w
            ])}

    @classmethod
    def decode(cls, bytes_io: IO):
        """
            Decode entity metadata
        :param bytes_io:
        :return:
        """

        meta_data = []
        while True:
            index = UnsignedByte.decode(bytes_io)

            # Break when Index is 0xff
            if index == 0xff:
                break

            value_type = VarInt.decode(bytes_io)

            if not cls.TYPE_MAP.__contains__(value_type):
                raise ValueError(f"MetaData Value_type: {value_type} NOT FOUND!")

            _meta_data = {
                'index': index, 'data_type': value_type, 'value': []

            }

            type_cls_list = cls.TYPE_MAP[value_type]
            if len(type_cls_list) > 1 and type_cls_list[0] == Boolean:   # optValue

                _meta_data['value'].append(Boolean.decode(bytes_io))

                # Decode Optional Values
                if _meta_data['value'][0]:
                    for _ in type_cls_list[1:]:
                        _meta_data['value'].append(_.decode(bytes_io))

            # Particles
            elif value_type == 18:
                particle_n = VarInt.decode(bytes_io)
                for _ in range(particle_n):
                    _meta_data['value'].append(Particle.decode(bytes_io))
            else:
                for type_cls in type_cls_list:
                    _meta_data['value'].append(type_cls.decode(bytes_io))

            meta_data.append(_meta_data)
        return meta_data

    @classmethod
    def encode(cls, value: Iterable) -> bytes:
        """
            Encode entity metadata
        :param value: [{'index': UnsignedByte, 'data_type': VarInt Enum, 'value': []}, {metadata}]
        :return:
        """
        meta_bytes = bytes()
        for meta in value:
            meta_bytes += UnsignedByte.encode(meta['index'])
            data_type = meta['data_type']
            if not cls.TYPE_MAP.__contains__(data_type):
                raise ValueError(f"MetaData Value_type: {data_type} NOT FOUND!")

            data_type_cls = cls.TYPE_MAP[data_type]
            meta_bytes += VarInt.encode(meta['data_type'])

            for index, type_cls in enumerate(data_type_cls):
                _value = meta['value'][index]
                if _value is None:
                    break
                meta_bytes += type_cls.encode(_value)

        return meta_bytes + b'\xff'


class TeleportFlags(Int):
    """
        0x0001	Relative X
        0x0002	Relative Y
        0x0004	Relative Z
        0x0008	Relative Yaw
        0x0010	Relative Pitch
        0x0020	Relative Velocity X
        0x0040	Relative Velocity Y
        0x0080	Relative Velocity Z
        0x0100	Rotate velocity according to the change in rotation, before applying the velocity change in this packet. Combining this with absolute rotation works as expected—the difference in rotation is still used.
    """


class Node(DataType):
    """
        Details See
        https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Command_Data
        TODO Finish parser LATER!
    """

    PARSERS = {
        0: lambda x: Boolean.decode(x),

        17: lambda x: TextComponent.decode(x),
        18: lambda x: TextComponent.decode(x),

        28: lambda x: Angle.decode(x),
        32: lambda x: String.decode(x),

        34: lambda x: Identifier.decode(x),
    }

    @classmethod
    def decode(cls, bytes_io: IO):

        res = {}

        flags = Byte.decode(bytes_io)

        res['flags'] = flags

        node_type = flags & 0x03
        is_executable = flags & 0x04
        has_redirect = flags & 0x08
        has_suggestions_type = flags & 0x10

        children_count = VarInt.decode(bytes_io)

        children = []
        for _ in range(children_count):
            children.append(VarInt.decode(bytes_io))

        res['children'] = children

        if has_redirect:
            res['redirect_node'] = VarInt.decode(bytes_io)

        if node_type in (1, 2):
            res['name'] = String.decode(bytes_io)

        if node_type == 2:
            res['parser_id'] = VarInt.decode(bytes_io)

            parser = cls.PARSERS.get(res['parser_id'])
            if parser:
                res['properties'] = parser(bytes_io)

            # TODO parser Work HERE

        if has_suggestions_type:
            res['suggestions_type'] = Identifier.decode(bytes_io)

        return res

    @classmethod
    def encode(cls, value) -> bytes:
        """
            TODO ... Somebody help!
        :param value:
        :return:
        """
        pass


class SlotDisplay(DataType):

    EMPTY = 0
    ANY_FUEL = 1
    ITEM = 2
    ITEM_STACK = 3
    TAG = 4
    SMITHING_TRIM = 5
    WITH_REMAINDER = 6
    COMPOSITE = 7

    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()

        res['slot_display_type'] = VarInt.decode(bytes_io)

        if res['slot_display_type'] in (cls.EMPTY, cls.ANY_FUEL):
            res['data'] = None
        elif res['slot_display_type'] == cls.ITEM:
            res['data'] = VarInt.decode(bytes_io)
        elif res['slot_display_type'] == cls.ITEM_STACK:
            res['data'] = Slot.decode(bytes_io)
        elif res['slot_display_type'] == cls.TAG:
            res['data'] = Identifier.decode(bytes_io)
        elif res['slot_display_type'] == cls.SMITHING_TRIM:
            res['data'] = {
                'base': cls.decode(bytes_io),
                'material': cls.decode(bytes_io),
                'pattern': cls.decode(bytes_io),
            }
        elif res['slot_display_type'] == cls.WITH_REMAINDER:
            res['data'] = {
                'ingredient': cls.decode(bytes_io),
                'remainder': cls.decode(bytes_io),
            }
        elif res['slot_display_type'] == cls.COMPOSITE:
            n = VarInt.decode(bytes_io)
            res['data'] = []
            for _ in range(n):
                res['data'].append(cls.decode(bytes_io))

        return res


class RecipeDisplay(DataType):
    """
        https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Recipes
    """

    CRAFTING_SHAPELESS = 0
    CRAFTING_SHAPED = 1
    FURNACE = 2
    STONECUTTER = 3
    SMITHING = 4

    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['recipe_display_type'] = VarInt.decode(bytes_io)

        if res['recipe_display_type'] == cls.CRAFTING_SHAPELESS:
            res['data'] = {
                'ingredients': [],
            }
            n = VarInt.decode(bytes_io)
            for _ in range(n):
                res['data']['ingredients'].append(SlotDisplay.decode(bytes_io))

            res['data']['result'] = SlotDisplay.decode(bytes_io)
            res['data']['crafting_station'] = SlotDisplay.decode(bytes_io)

        elif res['recipe_display_type'] == cls.CRAFTING_SHAPED:
            res['data'] = {
                'width': VarInt.decode(bytes_io),
                'height': VarInt.decode(bytes_io),
                'ingredients': [],
            }
            n = VarInt.decode(bytes_io)
            for _ in range(n):
                res['data']['ingredients'].append(SlotDisplay.decode(bytes_io))
            res['data']['result'] = SlotDisplay.decode(bytes_io)
            res['data']['crafting_station'] = SlotDisplay.decode(bytes_io)

        elif res['recipe_display_type'] == cls.FURNACE:
            res['data'] = {
                'ingredient': SlotDisplay.decode(bytes_io),
                'fuel': SlotDisplay.decode(bytes_io),
                'result': SlotDisplay.decode(bytes_io),
                'crafting_station': SlotDisplay.decode(bytes_io),
                'cooking_time': VarInt.decode(bytes_io),
                'experience': Float.decode(bytes_io)
            }

        elif res['recipe_display_type'] == cls.STONECUTTER:
            res['data'] = {
                'ingredient': SlotDisplay.decode(bytes_io),
                'result': SlotDisplay.decode(bytes_io),
                'crafting_station': SlotDisplay.decode(bytes_io)
            }

        elif res['recipe_display_type'] == cls.SMITHING:
            res['data'] = {
                'template': SlotDisplay.decode(bytes_io),
                'base': SlotDisplay.decode(bytes_io),
                'additional': SlotDisplay.decode(bytes_io),
                'result': SlotDisplay.decode(bytes_io),
                'crafting_station': SlotDisplay.decode(bytes_io)
            }

        return res


# For Advancements
class CriterionProcess(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['achieved'] = Boolean.decode(bytes_io)
        if res['achieved']:
            res['date_of_achieving'] = Long.decode(bytes_io)
        return res


class AdvancementProcess(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['size'] = VarInt.decode(bytes_io)
        res['criteria'] = []
        for _ in range(res['size']):
            res['criteria'].append([
                {
                    'criterion_identifier': Identifier.decode(bytes_io),
                    'criterion_progress': CriterionProcess.decode(bytes_io),
                }
            ])
        return res


class AdvancementDisplay(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['title'] = TextComponent.decode(bytes_io)
        res['description'] = TextComponent.decode(bytes_io)
        res['icon'] = Slot.decode(bytes_io)
        res['frame_type'] = VarInt.decode(bytes_io)
        res['flags'] = Int.decode(bytes_io)
        if res['flags'] & 0x01:
            res['background_texture'] = Identifier.decode(bytes_io)

        res['x_coord'] = Float.decode(bytes_io)
        res['y_coord'] = Float.decode(bytes_io)
        return res


class Advancement(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['has_parents'] = Boolean.decode(bytes_io)
        if res['has_parents']:
            res['parent_id'] = Identifier.decode(bytes_io)

        res['has_display'] = Boolean.decode(bytes_io)
        if res['has_display']:
            res['display_data'] = AdvancementDisplay.decode(bytes_io)

        res['array_length'] = VarInt.decode(bytes_io)
        res['requirements'] = []
        for _ in range(res['array_length']):
            _l = VarInt.decode(bytes_io)
            res['requirements'].append([
                String.decode(bytes_io) for __ in range(_l)
            ])

        res['sends_telemetry_data'] = Boolean.decode(bytes_io)
        return res


# Chunk

def decode_palette(bits_per_entry: int, data_int: int, palette: list = None) -> list[int]:
    _bytes = bin(data_int).replace('0b', '').rjust(64, '0')
    _bytes = _bytes[::-1]
    blocks = []
    for _ in [_bytes[i:i+bits_per_entry] for i in range(0, len(_bytes), bits_per_entry)]:
        if len(_) < bits_per_entry:
            continue

        _ = _[::-1]
        try:
            if palette is None:
                blocks.append(int(_, 2))
            else:
                blocks.append(palette[int(_, 2)])
        except Exception as e:
            print('Error', _, int(_, 2), len(palette), e)
            continue
    return blocks


class PalettedContainerBlocks(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        bpe = UnsignedByte.decode(bytes_io)
        res['bits_per_entry'] = bpe

        if bpe == 0:
            res['single_valued'] = VarInt.decode(bytes_io)
            res['_type'] = 0
        elif 4 <= bpe <= 8:
            c = VarInt.decode(bytes_io)
            res['indirect'] = [
                VarInt.decode(bytes_io) for _ in range(c)
            ]
            res['_type'] = 1
        elif bpe >= 15:
            res['_type'] = 2

        _len = VarInt.decode(bytes_io)

        res['data_array'] = [
            UnsignedLong.decode(bytes_io) for _ in range(_len)
        ]
        return res


class PalettedContainerBiomes(DataType):
    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        bpe = UnsignedByte.decode(bytes_io)
        res['bits_per_entry'] = bpe

        if bpe == 0:
            res['single_valued'] = VarInt.decode(bytes_io)
            res['_type'] = 0

        elif 1 <= bpe <= 3:
            _len = VarInt.decode(bytes_io)
            res['indirect'] = [
                VarInt.decode(bytes_io) for _ in range(_len)
            ]
            res['_type'] = 1

        elif bpe >= 6:
            res['_type'] = 2

        _len = VarInt.decode(bytes_io)
        res['data_array'] = [
            UnsignedLong.decode(bytes_io) for _ in range(_len)
        ]
        return res


class ChunkSection(DataType):

    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['block_count'] = Short.decode(bytes_io)
        res['block_states'] = PalettedContainerBlocks.decode(bytes_io)
        res['biomes'] = PalettedContainerBiomes.decode(bytes_io)
        return res


class ChunkData(DataType):

    @classmethod
    def decode(cls, bytes_io: IO, dimension_chunk_size: int = 24) -> dict:
        res = dict()

        res['heightmaps'] = NBT.decode(bytes_io)

        res['chunk_byte_size'] = VarInt.decode(bytes_io)

        res['chunk_sections'] = [
            ChunkSection.decode(bytes_io) for _ in range(dimension_chunk_size)
        ]

        block_entities = VarInt.decode(bytes_io)
        res['block_entities'] = [
            {
                'packed_xz': UnsignedByte.decode(bytes_io),
                'y': Short.decode(bytes_io),
                '_type': VarInt.decode(bytes_io),
                'data': NBT.decode(bytes_io),
            }  for _ in range(block_entities)
        ]

        return res


class LightData(DataType):

    @classmethod
    def decode(cls, bytes_io: IO) -> dict:
        res = dict()
        res['sky_light_mask'] = BitSet.decode(bytes_io)
        res['block_light_mask'] = BitSet.decode(bytes_io)
        res['empty_sky_light_mask'] = BitSet.decode(bytes_io)
        res['empy_block_light_mask'] = BitSet.decode(bytes_io)

        for key in ['sky_light_arrays', 'block_light_arrays']:
            _len = VarInt.decode(bytes_io)
            res[key] = []
            for _ in range(_len):
                VarInt.decode(bytes_io)     # Prefixed Array Length. Always 2048
                res[key].append([Byte.decode(bytes_io) for __ in range(2048)])

        return res


rows = []
for chunk_sec in range(-4, 20):
    for y in range(16):
        for z in range(16):
            for x in range(16):
                rows.append([
                    x, y + chunk_sec * 16, z, chunk_sec
                ])

chunk_df_24d = pd.DataFrame(rows, columns=['x', 'y', 'z', 'chunk_y'])

rows = []
for chunk_sec in range(0, 16):
    for y in range(16):
        for z in range(16):
            for x in range(16):
                rows.append([
                    x, y + chunk_sec * 16, z, chunk_sec
                ])

chunk_df_16d = pd.DataFrame(rows, columns=['x', 'y', 'z', 'chunk_y'])


@dataclass
class Chunk:
    """
        Chunk Data in x,z
    """

    x: int
    z: int
    heightmaps: np.ndarray
    blocks: np.ndarray
    dimension: int

    def __repr__(self):
        return f"Chunk {self.dimension} {self.x:>5}:{self.z:<5}"

    @classmethod
    def decode_result(
            cls,
            dimension: int,
            chunk_x: int, chunk_z: int,
            data: dict, **kwargs
    ) -> 'Chunk':
        """
            Decode Chunk Data to Chunk
        :param chunk_x:
        :param chunk_z:
        :param data:
        :param dimension:
        :param kwargs:
        :return:
        """

        # Heightmaps
        # 16 * 16 y with x,z
        heightmaps = []
        for _ in data['heightmaps']['MOTION_BLOCKING'].value:
            # ceil(log2(world height + 1)) = 9
            heightmaps += decode_palette(9, _)

        # blocks
        chunk_sections = data['chunk_sections']

        blocks_data = []

        for chunk_index, chunk_section in enumerate(chunk_sections):

            paletted_container = chunk_section['block_states']

            if paletted_container['_type'] == 0:
                blocks_data += [paletted_container['single_valued'] for _ in range(4096)]
            else:
                _blocks = []
                for data_int in paletted_container['data_array']:
                    _blocks += decode_palette(
                        bits_per_entry=paletted_container['bits_per_entry'],
                        data_int=data_int,
                        palette=paletted_container['indirect'] if paletted_container['_type'] == 1 else None,
                    )
                blocks_data += _blocks[:4096]

        return Chunk(
            x=chunk_x, z=chunk_z,
            heightmaps=np.array(heightmaps[:256], dtype=np.uint32).reshape((16, 16)),
            blocks=np.array(blocks_data, dtype=np.uint32).reshape(
                (cls.get_dimension_chunk_size(dimension) * 16, 16, 16)
            ),
            dimension=dimension
        )

    @classmethod
    def get_dimension_chunk_size(cls, dimension: int) -> int:
        return {
            0: 24, # OverWorld With 384
        }.get(dimension, 16)

    @staticmethod
    def to_name(block_id: int) -> str | None:
        """
            获取名称
        :param block_id:
        :return:
        """
        _ = block_ids.get(block_id)
        if _ is None:
            return None
        else:
            return f"{_['name']}_{_['index']}"

    @property
    def df(self) -> pd.DataFrame:
        """
            获取 Dataframe 数据
        :return:
        """
        df = {
            24: chunk_df_24d,
        }.get(self.get_dimension_chunk_size(self.dimension), chunk_df_16d).copy()

        df['block_id'] = self.blocks.ravel()
        df['chunk_x'] = self.x
        df['chunk_z'] = self.z
        df['x'] = df['x'] + self.x * 16
        df['z'] = df['z'] + self.z * 16
        df['dimension'] = self.dimension
        df['block_name'] = df.block_id.apply(self.to_name)
        df['is_top'] = False


        for _x in range(16):
            for _z in range(16):
                df.loc[
                    (df.x == _x + self.x * 16) & (df.z == _z + self.z * 16) &
                    (df.y == self.heightmaps[_x][_z] - (64 if self.get_dimension_chunk_size(self.dimension) == 24 else 0)),
                    'is_top'
                ] = True

        return df[['block_id', 'block_name', 'x', 'y', 'z', 'dimension', 'chunk_x', 'chunk_y', 'chunk_z', 'is_top']]

    def update_block(self, location: Position, block_id: int):
        """
            更新 Block
        :param location:
        :param block_id:
        :return:
        """
        self.blocks[
            location.y + (64 if self.get_dimension_chunk_size(self.dimension) == 24 else 0),
            location.z % 16,
            location.x % 16,
        ] = block_id

    def get_block_id(self, location: Position) -> int:
        """
            获取 Block ID
        :param location:
        :return:
        """
        return int(
            self.blocks[
                location.y + (64 if self.get_dimension_chunk_size(self.dimension) == 24 else 0),
                location.z % 16,
                location.x % 16]
        )
