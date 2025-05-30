# -*- coding: utf-8 -*-
"""
    nbt
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-05-29 0.2.0 Me2sY  修复 TagEnd

        2025-05-16 0.1.0 Me2sY 想了想还是自己写吧，替代pyNBT
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'TagEnd', 'TagByte', 'TagShort', 'TagInt',
    'TagLong', 'TagFloat', 'TagDouble',
    'TagByteArray', 'TagString', 'TagList',
    'TagCompound', 'TagCompoundNet',
    'TagIntArray', 'TagLongArray',
    'NBTFile'
]

from dataclasses import dataclass
import struct
from typing import Any, Self, IO, ClassVar, Iterator

from mutf8 import decode_modified_utf8, encode_modified_utf8


@dataclass
class Tag:
    """
        NBT 标签
    """
    tag_format: ClassVar[str] = None
    tag_type_id: ClassVar[int] = -1

    value: Any
    name: str = None

    def __bytes__(self) -> bytes:
        return self.encode_type_id + self.encode_name + self.encode_value

    @property
    def bytes(self) -> bytes:
        return self.__bytes__()

    def encode(self) -> bytes:
        """
            编码
        :return:
        """
        return self.encode_type_id + self.encode_name + self.encode_value

    @property
    def encode_value(self) -> bytes:
        """
            编码Value
        :return:
        """
        if isinstance(self.value, bytes):
            return self.value
        else:
            return struct.pack(self.tag_format, self.value)

    @property
    def encode_type_id(self) -> bytes:
        """
            编码类别
        :return:
        """
        return struct.pack('>B', self.tag_type_id)

    @property
    def encode_name(self) -> bytes:
        """
            编码名称
        :return:
        """
        if self.name:
            name_bytes = encode_modified_utf8(self.name)
            return struct.pack('>H', len(name_bytes)) + name_bytes
        else:
            return b'\x00\x00'

    @classmethod
    def decode(cls, bytes_io: IO) -> Self:
        """
            解码
        :param bytes_io:
        :return:
        """
        # 解码 Tag Name
        name = cls.decode_name(bytes_io)

        # 解码 Value
        value = cls.decode_value(bytes_io)

        return cls(name=name, value=value)

    @staticmethod
    def decode_name(bytes_io: IO) -> str | None:
        """
            解码 Tag Name
        :param bytes_io:
        :return:
        """
        name_len = struct.unpack('>H', bytes_io.read(2))[0]
        if name_len > 0:
            return decode_modified_utf8(bytes_io.read(name_len))
        else:
            return None

    @classmethod
    def decode_value(cls, bytes_io: IO) -> Any:
        """
            解码 值
        :param bytes_io:
        :return:
        """
        return struct.unpack(cls.tag_format, bytes_io.read(struct.calcsize(cls.tag_format)))[0]


@dataclass
class TagEnd(Tag):
    """
        Signifies the end of a TAG_Compound.
        It is only ever used inside a TAG_Compound, a TAG_List that has it's type id set to TAG_Compound
        or as the type for a TAG_List if the length is 0 or negative, and is not named even when in a TAG_Compound
    """
    tag_type_id = 0
    tag_format = '>B'

    value: bytes = b'\x00'

    def encode(self) -> bytes:
        return b'\x00'

    @classmethod
    def decode(cls, bytes_io: IO) -> Self:
        bytes_io.read(1)
        return cls()

    @property
    def encode_value(self) -> bytes:
        return b'\x00'


class TagByte(Tag):
    """
        A single signed byte
    """
    tag_type_id = 1
    tag_format = '>b'


class TagShort(Tag):
    """
        A single signed, big endian 16-bit integer
    """
    tag_type_id = 2
    tag_format = '>h'


class TagInt(Tag):
    """
        A single signed, big endian 32-bit integer
    """
    tag_type_id = 3
    tag_format = '>i'


class TagLong(Tag):
    """
        A single signed, big endian 64-bit integer
    """
    tag_type_id = 4
    tag_format = '>q'


class TagFloat(Tag):
    """
        A single, big endian IEEE-754 single-precision floating point number (NaN possible)
    """
    tag_type_id = 5
    tag_format = '>f'


class TagDouble(Tag):
    """
        A single, big endian IEEE-754 double-precision floating point number (NaN possible)
    """
    tag_type_id = 6
    tag_format = '>d'


class TagArray(Tag):
    """
        Array Tag
    """
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>({len(self.value)} Tags)"

    def __len__(self):
        return len(self.value)

    def __iter__(self) -> Iterator[Tag]:
        for _ in self.value:
            yield _

    def __getitem__(self, item: int) -> Tag:
        return self.value[item]

    def __setitem__(self, item: int, value: Tag) -> None:
        self.value[item] = value

    def __delitem__(self, item: int) -> None:
        del self.value[item]

    @classmethod
    def decode_value(cls, bytes_io: IO) -> tuple[bytes, ...]:
        """
            解码值
        :param bytes_io:
        :return:
        """
        array_len = struct.unpack('>i', bytes_io.read(4))[0]
        array_format = f'>{array_len}{cls.tag_format[-1]}'
        return struct.unpack(array_format, bytes_io.read(struct.calcsize(array_format)))

    @property
    def encode_value(self) -> bytes:
        """
            ValueLen + Value
        :return:
        """
        return struct.pack(
            f">i{len(self.value)}{self.tag_format[-1]}", len(self.value), *self.value
        )


class TagByteArray(TagArray):
    """
        A length-prefixed array of signed bytes. The prefix is a signed integer (thus 4 bytes)
    """
    tag_type_id = 7
    tag_format = '>b'


class TagString(Tag):
    """
        	A length-prefixed modified UTF-8 string.
        	The prefix is an unsigned short (thus 2 bytes) signifying the length of the string in bytes
    """
    tag_type_id = 8

    @classmethod
    def decode_value(cls, bytes_io: IO) -> str:
        """
            解码文字
        :param bytes_io:
        :return:
        """
        string_len = struct.unpack('>H', bytes_io.read(2))[0]
        if string_len == 0:
            return ''
        else:
            return decode_modified_utf8(bytes_io.read(string_len))

    @property
    def encode_value(self) -> bytes:
        """
            UTF8
        :return:
        """
        string_bytes = encode_modified_utf8(self.value)
        return struct.pack('>H', len(string_bytes)) + string_bytes


@dataclass
class TagList(Tag):
    """
        A list of nameless tags, all of the same type.
        The list is prefixed with the Type ID of the items it contains (thus 1 byte),
        and the length of the list as a signed integer (a further 4 bytes).
        If the length of the list is 0 or negative, the type may be 0 (TAG_End) but otherwise it must be any other type.
        (The notchian implementation uses TAG_End in that situation,
        but another reference implementation by Mojang uses 1 instead;
        parsers should accept any type if the length is <= 0).
    """
    tag_type_id = 9

    items_type: Any = None

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.items_type.__class__.__name__}) {self.name}>({len(self.value)} Tags)"

    @classmethod
    def decode(cls, bytes_io: IO) -> Self | TagEnd:
        """
            解码
        :param bytes_io:
        :return:
        """
        name = cls.decode_name(bytes_io)
        items_type = NBTFile.TAG_MAPPER.get(struct.unpack('>b', bytes_io.read(1))[0])
        child_len = struct.unpack('>i', bytes_io.read(4))[0]
        if child_len <= 0:
            return TagEnd()
        else:
            value = []
            for i in range(child_len):
                value.append(items_type(value=items_type.decode_value(bytes_io)))
            return cls(name=name, value=value, items_type=items_type)

    @property
    def encode_value(self) -> bytes:
        if len(self.value) == 0:
            return self.items_type(value=None).encode_type_id + b'\x00\x00\x00\x00'
        else:
            bs = self.items_type(value=None).encode_type_id + struct.pack('>i', len(self.value))
            for item in self.value:
                bs += item.encode_value
            return bs


class TagCompound(Tag):
    """
        Effectively a list of named tags. Order is not guaranteed.
    """

    tag_type_id = 10

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>({len(self.value)} Tags)"

    @classmethod
    def decode_value(cls, bytes_io: IO) -> list[Tag]:
        """
            解码 Value
        :param bytes_io:
        :return:
        """

        tags = []

        while True:
            tag_cls = NBTFile.TAG_MAPPER.get(struct.unpack('>b', bytes_io.read(1))[0])
            if tag_cls == TagEnd:
                return tags
            else:
                tags.append(tag_cls.decode(bytes_io))


    @property
    def encode_value(self) -> bytes:
        """
            编码值
        :return:
        """
        bs = b''
        for item in self.value:
            bs += item.encode()
        bs += TagEnd().encode()
        return bs


class TagCompoundNet(TagCompound):
    """
        Since 1.20.2 (Protocol 764) NBT sent over the network has been updated to exclude the name from
        the root TAG_COMPOUND.
        This only applies to network NBT. Player data, world data, etc... will not be affected.
    """
    @classmethod
    def decode(cls, bytes_io: IO) -> Self:
        """
            Name and Length of Name are None
        :param bytes_io: 
        :return: 
        """
        return cls(value=cls.decode_value(bytes_io))

    def encode(self) -> bytes:
        """
            Name and Length of Name are None
        :return: 
        """
        return self.encode_type_id + self.encode_value


class TagIntArray(TagArray):
    """
        A length-prefixed array of signed integers.
        The prefix is a signed integer (thus 4 bytes) and indicates the number of 4 byte integers.
    """
    tag_type_id = 11
    tag_format = '>i'


class TagLongArray(TagArray):
    """
        A length-prefixed array of signed longs.
        The prefix is a signed integer (thus 4 bytes) and indicates the number of 8 byte longs.
    """
    tag_type_id = 12
    tag_format = '>q'


class NBTFile:
    """
        NBT文件
    """
    TAG_MAPPER: ClassVar[dict[int, Tag]] = {
        0: TagEnd,
        1: TagByte,
        2: TagShort,
        3: TagInt,
        4: TagLong,
        5: TagFloat,
        6: TagDouble,
        7: TagByteArray,
        8: TagString,
        9: TagList,
        10: TagCompound,
        11: TagIntArray,
        12: TagLongArray,
    }
    
    @classmethod
    def decode(cls, bytes_io: IO) -> TagCompound | TagEnd:
        """
            解码
        :param bytes_io:
        :return:
        """
        fb = bytes_io.read(1)
        if fb == b'\x00':
            return TagEnd()

        elif fb != b'\n':
            raise ValueError(r"NBTFile decode error. Start Must Be TagCompound Type ID b'\n'")

        return TagCompound.decode(bytes_io)

    @classmethod
    def decode_net(cls, bytes_io: IO) -> TagCompoundNet | TagEnd:
        """
            解码网络格式TagCompound
        :param bytes_io:
        :return:
        """
        fb = bytes_io.read(1)
        if fb == b'\x00':
            return TagEnd()

        elif fb != b'\n':
            raise ValueError(r"NBTFile decode error. Start Must Be TagCompoundNet Type ID b'\n'")

        return TagCompoundNet.decode(bytes_io)

    @classmethod
    def encode(cls, tag_compound: TagCompound | TagCompoundNet) -> bytes:
        """
            编码
        :param tag_compound:
        :return:
        """
        return tag_compound.encode()
