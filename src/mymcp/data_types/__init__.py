# -*- coding: utf-8 -*-
"""
    data_types
    ~~~~~~~~~~~~~~~~~~
    数据结构

    Log:
        2025-05-27 0.2.0 Me2sY  重构结构

        2025-05-17 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'DataType',
    'Boolean',
    'Byte', 'UnsignedByte',
    'Short', 'UnsignedShort',
    'Int', 'Long', 'UnsignedLong',
    'Float', 'Double',
    'VarInt', 'VarLong',
    'String', 'TextComponent', 'JsonTextComponent',
    'Identifier', 'NBT', 'Position', 'Angle', 'UUID',
    'BitSet', 'FixedBitSet', 'IDSet', 'TeleportFlags',

    'DataPacket', 'Field', 'InnerField', 'OptionalGroupField', 'Combined',

    'SoundEvent', 'Node',

    'IDOrX', 'IDOrSoundEvent',

    'OptionalX',
    'OptionalBoolean', 'OptionalInt', 'OptionalFloat', 'OptionalVarInt', 'OptionalLong', 'OptionalString',
    'OptionalTextComponent', 'OptionalPosition', 'OptionalUUID', 'OptionalIdentifier', 'OptionalNBT',
    'OptionalIDSet',
]


from dataclasses import dataclass, field
from inspect import isclass
from io import BytesIO
import json
from socket import socket
import struct
from typing import IO, ClassVar, Self, Any, Sized, Optional, TypeVar, Generic
import uuid

from mutf8 import decode_modified_utf8

from mymcp.data_types.nbt import TagString, TagCompound, TagCompoundNet, NBTFile


@dataclass
class DataType:
    """
        Minecraft Data Type
    """
    PRINT_LENGTH: ClassVar[int] = 100
    FIELD_NAME: ClassVar[str] = ''

    BYTE_ORDER: ClassVar[str] = '>'
    FORMAT: ClassVar[str] = ''

    # 定义时计算出长度，加快解码
    BYTES_LENGTH: ClassVar[int] = -1

    value: Any

    @classmethod
    def encode(cls, value: Any, *args, **kwargs) -> bytes:
        """
            直接编码数据，速度较快
        :return:
        """
        return struct.pack(cls.BYTE_ORDER + cls.FORMAT, value)

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :return:
        """
        return cls(value=struct.unpack(cls.BYTE_ORDER + cls.FORMAT, bytes_io.read(cls.BYTES_LENGTH))[0])

    @classmethod
    def decode_bytes(cls, bytes_data: bytes) -> Self:
        """
            语法糖，直接解析给定 bytes，节省一个创建BytesIO操作
        :param bytes_data:
        :return:
        """
        return cls.decode(BytesIO(bytes_data))

    def __call__(self, *args, **kwargs):
        return self.value

    def __bytes__(self):
        return self.encode(self.value)

    @property
    def bytes(self) -> bytes:
        """
            返回bytes
        :return:
        """
        return self.encode(self.value)

    def bytes_io(self) -> BytesIO:
        """
            返回 BytesIO
        :return:
        """
        return BytesIO(self.bytes)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.value!r})>"[:self.PRINT_LENGTH]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Self.__class__):
            return self.value == other.value
        else:
            return self.value == other


class Boolean(DataType):
    """
        True is encoded as 0x01, false as 0x00.
    """

    FALSE: ClassVar[bytes] = b'\x00'
    TRUE: ClassVar[bytes] = b'\x01'

    FORMAT: ClassVar[str] = '?'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: bool

    def __bool__(self) -> bool:
        return self.value


class Byte(DataType):
    """
        An integer between -128 and 127
        Signed 8-bit integer, two's complement
    """

    FORMAT: ClassVar[str] = 'b'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


class UnsignedByte(DataType):
    """
        An integer between 0 and 255
        Unsigned 8-bit integer
    """

    FORMAT: ClassVar[str] = 'B'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


class Short(DataType):
    """
        An integer between -32768 and 32767
        Signed 16-bit integer, two's complement
    """

    FORMAT: ClassVar[str] = 'h'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


class UnsignedShort(DataType):
    """
        An integer between 0 and 65535
        Unsigned 16-bit integer
    """

    FORMAT: ClassVar[str] = 'H'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


class Int(DataType):
    """
        An integer between -2147483648 and 2147483647
        Signed 32-bit integer, two's complement
    """

    FORMAT: ClassVar[str] = 'i'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


class Long(DataType):
    """
        An integer between -9223372036854775808 and 9223372036854775807
        Signed 64-bit integer, two's complement
    """

    FORMAT: ClassVar[str] = 'q'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


class UnsignedLong(DataType):

    FORMAT: ClassVar[str] = 'Q'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


class Float(DataType):
    """
        A single-precision 32-bit IEEE 754 floating point number
    """

    FORMAT: ClassVar[str] = 'f'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: float


class Double(DataType):
    """
        A double-precision 64-bit IEEE 754 floating point number
    """

    FORMAT: ClassVar[str] = 'd'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: float


class VarInt(DataType):
    """
        Minecraft VarInt
        An integer between -2147483648 and 2147483647
    """

    ENCODE_FORMAT: ClassVar[str] = 'B'
    DECODE_FORMAT: ClassVar[str] = 'i'

    MAX_BYTES: ClassVar[int] = 5
    INT_BITS: ClassVar[int] = 32

    # Size table when you need to get a VarInt Size
    SIZE_TABLE: ClassVar[dict[int, int]] = {2 ** (i * 7): i for i in range(1, 13)}

    value: int

    def __hash__(self):
        return self.value

    @classmethod
    def encode(cls, value: int, *args, **kwargs) -> bytes:
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
            _bytes += struct.pack(cls.BYTE_ORDER + cls.ENCODE_FORMAT, byte | (0x80 if value > 0 else 0))
            if value == 0:
                break
        return _bytes

    @classmethod
    def decode(cls, bytes_from: IO | socket, *args, **kwargs) -> Self:
        """
            VarInt 解析
        :param **kwargs:
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
            if bytes_encountered == 5:
                raise ValueError("Tried to read too long of a VarInt")
        return cls(value=struct.unpack(cls.BYTE_ORDER + cls.DECODE_FORMAT,
            int(number).to_bytes(int(cls.INT_BITS / 8), 'big')
        )[0])

    @classmethod
    def size(cls, value: int | Self) -> int:
        """
            VarInt bytes size
        :param value:
        :return:
        """
        if isinstance(value, VarInt):
            value = value.value

        for max_value, size in cls.SIZE_TABLE.items():
            if value < max_value:
                return size
        raise ValueError("Integer too large")

    def __len__(self) -> int:
        """
            self bytes size
        :return:
        """
        return self.size(self.value)


class VarLong(VarInt):
    """
        Variable-length data encoding a two's complement signed 64-bit integer
    """

    MAX_BYTES: ClassVar[int] = 5
    value: int


class String(DataType):
    """
        A sequence of Unicode scalar values
        UTF-8 string prefixed with its size in bytes as a VarInt.
        Maximum length of n characters, which varies by context;
        up to n × 4 bytes can be used to encode n characters and both of those limits are checked.
        Maximum n value is 32767.
        The + 3 is due to the max size of a valid length VarInt.
    """

    value: str

    @classmethod
    def encode(cls, value: str, *args, **kwargs) -> bytes:
        """
            编码
        :param value:
        :return:
        """
        _string_bytes = value.encode('utf-8')
        return VarInt.encode(len(_string_bytes)) + _string_bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :return:
        """
        return cls(
            value=bytes_io.read(
                VarInt.decode(bytes_io).value
            ).decode('utf-8')
        )


class TextComponent(DataType):
    """
        Encoded as a NBT Tag, with the type of tag used depending on the case:
            As a String Tag: For components only containing text (no styling, no events etc.).
            As a Compound Tag: Every other case.
    """

    value: TagString | TagCompoundNet | str

    @classmethod
    def encode(cls, value: TagString | TagCompoundNet, *args, **kwargs) -> bytes:
        """
            Maybe TagString or TagCompound
        :param value:
        :return:
        """
        if not isinstance(value, (TagString, TagCompoundNet,)):
            raise TypeError("TextComponent can only encode TagString or TagCompoundNet")
        return value.encode()

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :return:
        """
        if bytes_io.read(1) == b'\x08':
            # TagString
            l = UnsignedShort.decode(bytes_io)
            return cls(value=decode_modified_utf8(bytes_io.read(l.value)))
        else:
            return cls(value=TagCompoundNet.decode(bytes_io))


class JsonTextComponent(DataType):
    """
        JSON Text Component
    """

    value: dict

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :return:
        """
        return cls(value=json.loads(String.decode(bytes_io).value))

    @classmethod
    def encode(cls, value: dict, *args, **kwargs) -> bytes:
        """
            编码
        :param value:
        :return:
        """
        return String.encode(json.dumps(value))


class Identifier(String):
    """
        Identifier Type
        Encoded as a String with max length of 32767.
    """


class NBT(DataType):
    """
        NBT
        本版本面向 769 Network Protocol
        NBT为 TagCompoundNetwork
    """

    value: TagCompoundNet

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :return:
        """
        return cls(value=NBTFile.decode_net(bytes_io))

    @classmethod
    def encode(cls, value: TagCompoundNet, *args, **kwargs) -> bytes:
        """
            编码
        :param value:
        :return:
        """
        return value.encode()


class Position(DataType):
    """
        An integer/block position: x (-33554432 to 33554431), z (-33554432 to 33554431) y (-2048 to 2047),
        x as a 26-bit integer,
        followed by z as a 26-bit integer (all signed, two's complement).
        followed by y as a 12-bit integer,
    """

    value: tuple[int, int, int]

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            Decode a Position object from bytes.
        :param bytes_io:
        :return:
        """
        pos_long = UnsignedLong.decode(bytes_io).value
        x = int(pos_long >> 38)
        z = int((pos_long >> 12) & 0x3FFFFFF)
        y = int(pos_long & 0xFFF)

        if x >= pow(2, 25):
            x -= pow(2, 26)
        if y >= pow(2, 11):
            y -= pow(2, 12)
        if z >= pow(2, 25):
            z -= pow(2, 26)

        return cls(value=(x, y, z))

    @classmethod
    def encode(cls, value: tuple[int, int, int] | Sized | dict, *args, **kwargs) -> bytes:
        """
            Encode a Position object to bytes
        :param value:
        :return:
        """
        if isinstance(value, dict):
            x = value.get('x')
            y = value.get('y')
            z = value.get('z')
        elif isinstance(value, Sized):
            if len(value) != 3:
                raise ValueError(f"{value} items count != 3")
            x, y, z = value
        else:
            raise ValueError(f"{value} Error.")

        return Long.encode((((x & 0x3FFFFFF) << 38) | ((z & 0x3FFFFFF) << 12) | (y & 0xFFF)))

    @property
    def x(self) -> int:
        return self.value[0]

    @property
    def y(self) -> int:
        return self.value[1]

    @property
    def z(self) -> int:
        return self.value[2]


class Angle(DataType):

    """
        A rotation angle in steps of 1/256 of a full turn
        Whether this is signed does not matter, since the resulting angles are the same.
    """
    FORMAT: ClassVar[str] = 'b'
    BYTES_LENGTH: ClassVar[int] = struct.calcsize(FORMAT)
    value: int


@dataclass
class UUID(DataType):
    """
        UUID Type
        带默认值
    """
    BYTES_LENGTH: ClassVar[int] = 16
    value: uuid.UUID = field(default_factory=uuid.uuid4)

    def __repr__(self):
        return super().__repr__()

    @classmethod
    def encode(cls, value: uuid.UUID | str | int, *args, **kwargs) -> bytes:
        """
            Encode a UUID
        :param value:
        :return:
        """
        if isinstance(value, uuid.UUID):
            return value.bytes

        elif isinstance(value, str):
            return uuid.UUID(hex=value).bytes

        elif isinstance(value, int):
            return uuid.UUID(int=value).bytes

        else:
            raise ValueError(f"UUID encode {value} Error.")

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            Decode a UUID from bytes.
        :param bytes_io:
        :return:
        """
        return cls(value=uuid.UUID(bytes=bytes_io.read(cls.BYTES_LENGTH)))


class BitSet(DataType):
    """
        A length-prefixed bit set.
    """
    value: list[int]

    @classmethod
    def encode(cls, value: list[int] | tuple[int], *args, **kwargs) -> bytes:
        """
            编码
        :param value:
        :return:
        """
        _bytes = VarInt.encode(len(value))
        for v in value:
            _bytes += Long.encode(v)
        return _bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :return:
        """
        _len = VarInt.decode(bytes_io).value
        return cls(value=[Long.decode(bytes_io).value for _ in range(_len)])


class FixedBitSet(DataType):
    """
        Bit sets of type Fixed BitSet (n) have a fixed length of n bits, encoded as ceil(n / 8) bytes.
        Note that this is different from BitSet, which uses longs.
        中文讲就是 长度为 BITS_LENGTH的一段 Bit（0/1） 转换为 Bytes
        其中长度 为 ceil(BITS_LENGTH / 8) (1Byte = 8Bit) 不足的补 0
        使用前需修改 BITS_ARRAY_LENGTH 或在 decode中传入长度
    """
    # byte 转 01 预查表
    B2I = [
        [(byte >> i) & 1 for i in reversed(range(8))] for byte in range(256)
    ]

    # 目前仅在 Signed Chat Command/Chat Message 中发现使用，长度 20
    # 其他地方使用，建议继承类，修改 BITS_ARRAY_LENGTH 及 BYTES_LENGTH
    BITS_ARRAY_LENGTH: ClassVar[int] = 20        # ceil(20 / 8)
    BYTES_LENGTH: ClassVar[int] = (BITS_ARRAY_LENGTH + 7) // 8

    value: bytes

    @staticmethod
    def to_bytes(bits_array: list[bool|int] | tuple[bool|int]) -> bytes:
        """
            将 Bit array 编码为 bytes，0补位
        :param bits_array:
        :return:
        """
        # 需要 Bytes 长度
        bytes_len = (len(bits_array) + 7) // 8

        # 创建 byte_array
        byte_array = bytearray(bytes_len)

        for bit_index, bit in enumerate(bits_array):
            if bit:
                byte_index = bit_index // 8
                # 置位
                byte_array[byte_index] |= (1 << (7 - bit_index % 8))

        return bytes(byte_array)

    @classmethod
    def encode(cls, value: bytes, *args, **kwargs) -> bytes:
        return value

    @classmethod
    def decode(cls, bytes_io: IO, bits_array_length: int = 0, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :param bits_array_length:
        :return:
        """
        if bits_array_length == 0:
            bits_array_length = cls.BITS_ARRAY_LENGTH

        return cls(value=bytes_io.read((bits_array_length + 7) // 8))

    @property
    def bits_array(self) -> list[int]:
        """
            通过速查表，将bytes 转为 list[0/1]
        :return:
        """
        bits = []
        for byte in self.value:
            bits += self.B2I[byte]

        return bits[:self.BITS_ARRAY_LENGTH]


class IDSet(DataType):
    """
        Represents a set of IDs in a certain registry (implied by context),
        either directly (enumerated IDs) or indirectly (tag name).

        value: {_type:int, tag_name:str, ids:[]}
    """
    value: tuple[VarInt, Identifier | list[VarInt]]

    @classmethod
    def encode(cls, value: tuple[VarInt, Identifier | list[VarInt]], *args, **kwargs) -> bytes:
        """
            Value used to determine the data that follows. It can be either:
                0 - Represents a named set of IDs defined by a tag.
                Anything else - Represents an ad-hoc set of IDs enumerated inline
        :param value:
        :return:
        """
        _type, arg = value
        if _type.value == 0:
            return _type.bytes + arg.bytes
        else:
            bs = _type.bytes
            for varint_id in arg:
                bs += varint_id.bytes
            return bs

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            Value used to determine the data that follows. It can be either:
                0 - Represents a named set of IDs defined by a tag.
                Anything else - Represents an ad-hoc set of IDs enumerated inline
        :param bytes_io:
        :return:
        """
        _type = VarInt.decode(bytes_io)

        if _type.value == 0:
            return cls(value=(_type, Identifier.decode(bytes_io)))
        else:
            ids = []
            for _ in range(_type.value - 1):
                ids.append(VarInt.decode(bytes_io))
            return cls(value=(_type, ids))

    @property
    def _type(self) -> VarInt:
        """
            Value used to determine the data that follows. It can be either:
                0 - Represents a named set of IDs defined by a tag.
                Anything else - Represents an ad-hoc set of IDs enumerated inline.
        :return:
        """
        return self.value[0]

    @property
    def tag_name(self) -> Identifier | None:
        """
            The registry tag defining the ID set. Only present if Type is 0.
        :return:
        """
        return self.value[1] if self.value[0].value == 0 else None

    @property
    def ids(self) -> list[VarInt] | None:
        """
            An array of registry IDs. Only present if Type is not 0.
        :return:
        """
        return None if self.value[0].value == 0 else self.value[1]


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


@dataclass
class DataPacket:
    """
        Data Packet
    """
    length: int
    bound_to: int
    pid: int
    data: bytes
    raw_data: bytes = None

    def __repr__(self):
        return f"<DataPacket>(to:{'CLIENT' if self.bound_to == 0 else 'SERVER'} pid:0x{self.pid:>02x}, length={self.length:>5}, data:{self.data[:500]})"

    def bytes_io(self) -> BytesIO:
        return BytesIO(self.data)

    def to_raw_bytes(self) -> bytes:
        return VarInt.encode(self.pid) + self.data

    def __bytes__(self) -> bytes:
        return self.data

    @property
    def bytes(self) -> bytes:
        return self.data


class Field: ...


class InnerField: ...


class OptionalCondition: ...


OptionGroupName = TypeVar('OptionGroupName')


class OptionalGroupField(Generic[OptionGroupName]): ...


@dataclass
class Combined:
    """
        数据组合
    """
    PRINT_LENGTH: ClassVar[int] = 150

    @staticmethod
    def to_bytes_io(bytes_source: DataPacket | BytesIO | bytes) -> BytesIO:
        """
            转为 BytesIO
        :param bytes_source:
        :return:
        """
        if isinstance(bytes_source, DataPacket):
            return bytes_source.bytes_io()
        elif isinstance(bytes_source, bytes):
            return BytesIO(bytes_source)
        else:
            return bytes_source

    @staticmethod
    def list_to_bytes(value_list: list[DataType]) -> bytes:
        """
            编码 PrefixedArray -> Bytes
        :param value_list:
        :return:
        """
        bs = VarInt.encode(len(value_list))
        for _ in value_list:
            bs += _.bytes
        return bs

    @staticmethod
    def bytes_to_list(bytes_io: BytesIO, data_type: Any) -> tuple[VarInt, list[DataType]]:
        """
            解码 Bytes -> PrefixedArray
        :param bytes_io:
        :param data_type:
        :return:
        """
        array_length = VarInt.decode(bytes_io)
        return array_length, [data_type.decode(bytes_io) for _ in range(array_length.value)]

    def __repr__(self):
        return f"<CB {self.__class__.__name__}>"[:self.PRINT_LENGTH]

    def __bytes__(self) -> bytes:
        """
            to bytes
        :return:
        """
        bs = bytes()
        optional_key_cls = dict()

        for key, key_struct in self.__annotations__.items():
            value = getattr(self, key)

            field_type, data_type = key_struct.__args__

            # 过滤内含参数
            if isclass(field_type) and issubclass(field_type, InnerField):
                continue

            if hasattr(field_type, '__origin__') and issubclass(field_type.__origin__, OptionalGroupField):

                # Optional 标志位
                if field_type not in optional_key_cls:
                    optional_key_cls[field_type] = value
                    bs += value.bytes

                elif optional_key_cls[field_type]:

                    # PrefixedArray
                    if isinstance(value, list):
                        bs += self.list_to_bytes(value)

                    elif isinstance(value, DataType):
                        if value is not None:
                            bs += value.bytes
                continue

            else:
                if isinstance(value, list):
                    bs += self.list_to_bytes(value)
                else:
                    if value is not None:
                        bs += value.bytes
        return bs

    @classmethod
    def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
        """
            解码
        :param bytes_source:
        :return:
        """
        bytes_io = cls.to_bytes_io(bytes_source)

        optional_key_cls = dict()

        values = {}

        for key, key_struct in cls.__annotations__.items():

            field_type, data_type = key_struct.__args__

            # 过滤内含参数
            if isclass(field_type) and issubclass(field_type, InnerField):
                continue

            if hasattr(field_type, '__origin__') and issubclass(field_type.__origin__, OptionalGroupField):

                if field_type not in optional_key_cls:
                    _has = Boolean.decode(bytes_io)
                    optional_key_cls[field_type] = _has
                    values[key] = _has

                elif optional_key_cls[field_type]:
                    if hasattr(data_type, '__origin__') and data_type.__origin__ == list:
                        array_length, values[key] = cls.bytes_to_list(bytes_io, data_type.__args__[0])
                    else:
                        values[key] = data_type.decode(bytes_io)

            else:
                if hasattr(data_type, '__origin__') and data_type.__origin__ == list:
                    array_length, values[key] = cls.bytes_to_list(bytes_io, data_type.__args__[0])
                else:
                    values[key] = data_type.decode(bytes_io)

        return cls(**values)

    @classmethod
    def encode(cls, *args, **kwargs) -> bytes:
        """
            编码
        :param args:
        :param kwargs:
        :return:
        """
        if args:
            return cls(*args).__bytes__()
        else:
            return cls(**kwargs).__bytes__()

    @property
    def dict(self) -> dict[str, Any]:
        """
            Get Dict
        :return:
        """
        return {
            key_name: getattr(self, key_name) for key_name in self.__annotations__.keys()
        }

    @property
    def tuple(self) -> tuple[Any, ...]:
        """
            Get Tuple
        :return:
        """
        return tuple(getattr(self, key_name) for key_name in self.__annotations__.keys())

    @property
    def bytes(self) -> bytes:
        return self.__bytes__()


@dataclass(slots=True)
class SoundEvent(Combined):
    """
        Describes a sound that can be played.
    """
    sound_name: Field | Identifier
    fixed_range: OptionalGroupField[0] | Float


class NodeParser:
    """
        Node 数据解析器
    """
    TYPE_MAP = {
        1: Float,
        2: Double,
        3: Int,
        4: Long
    }

    @classmethod
    def decode(cls, parser_id: VarInt, data_io: IO, *args, **kwargs) -> tuple[DataType, ...]:
        """
            解码
        :param parser_id:
        :param data_io:
        :param args:
        :param kwargs:
        :return:
        """

        _parser_id = parser_id.value

        if _parser_id in [1, 2, 3, 4]:
            flags = Byte.decode(data_io)
            res = [flags]
            if flags.value & 0x01:
                res.append(cls.TYPE_MAP[_parser_id].decode(data_io))
            if flags.value & 0x02:
                res.append(cls.TYPE_MAP[_parser_id].decode(data_io))
            return tuple(res)

        elif _parser_id == 5:
            return (
                VarInt.decode(data_io),
            )
        elif _parser_id == 6:
            return (
                Byte.decode(data_io),
            )
        elif _parser_id == 30:
            return (
                Byte.decode(data_io),
            )
        elif _parser_id == 42:
            return (
                Int.decode(data_io),
            )
        elif _parser_id in [43, 44, 45, 46]:
            return (
                Identifier.decode(data_io),
            )
        else:
            return ()


@dataclass(slots=True)
class Node(Combined):

    flags: Field | Byte
    children: Field | list[VarInt]
    redirect_node: OptionalCondition | VarInt = None
    name: OptionalCondition | String = None
    parser_id: OptionalCondition | VarInt = None
    properties: OptionalCondition | tuple = None
    suggestions_type: OptionalCondition | Identifier = None

    def __bytes__(self) -> bytes:
        bs = self.flags.bytes

        bs += VarInt.encode(len(self.children))
        for _ in self.children:
            bs += _.bytes

        if self.redirect_node is not None:
            bs += self.redirect_node.bytes

        if self.name is not None:
            bs += self.name.bytes

        if self.parser_id is not None:
            bs += self.parser_id.bytes

        if self.properties is not None:
            for _property in self.properties:
                bs += _property.bytes

        if self.suggestions_type is not None:
            bs += self.suggestions_type.bytes

        return bs

    @classmethod
    def decode(cls, data_source: bytes | DataPacket | BytesIO) -> Self:
        """
            解码
        :param data_source:
        :return:
        """
        # print('NODE:', data_source.data)
        bytes_io = cls.to_bytes_io(data_source)

        flags = Byte.decode(bytes_io)
        array_length = VarInt.decode(bytes_io)
        children = [
            VarInt.decode(bytes_io) for _ in range(array_length.value)
        ]

        node_instance = cls(flags, children)

        if flags.value & 0x08:
            node_instance.redirect_node = VarInt.decode(bytes_io)

        if flags.value & 0x03 in [1, 2]:
            node_instance.name = String.decode(bytes_io)

        if flags.value & 0x03 == 2:
            node_instance.parser_id = VarInt.decode(bytes_io)
            node_instance.properties = NodeParser.decode(node_instance.parser_id, bytes_io)

        if flags.value & 0x10:
            node_instance.suggestions_type = Identifier.decode(bytes_io)

        return node_instance


@dataclass
class IDOrX(DataType):

    ITEM_CLS: ClassVar[DataType | Combined]

    _id: VarInt = None
    value: Optional[Any] = None

    def __bytes__(self) -> bytes:
        """
            编码
        :return:
        """
        if self.value is not None:
            try:
                bs = self.value.bytes
            except AttributeError:
                bs = self.value.encode()
        else:
            bs = b''

        if self._id.value == 0:
            return self._id.bytes + bs
        else:
            return self._id.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :param args:
        :param kwargs:
        :return:
        """
        _id = VarInt.decode(bytes_io)
        if _id.value == 0:
            return cls(_id=_id, value=cls.ITEM_CLS.decode(bytes_io))
        else:
            return cls(_id=_id)


class IDOrSoundEvent(IDOrX):
    ITEM_CLS: ClassVar[DataType] = SoundEvent


class OptionalX(DataType):

    ITEM_CLS: ClassVar[DataType]

    @classmethod
    def encode(cls, value: Optional[DataType], *args, **kwargs) -> bytes:
        """
            编码，首位为 Boolean + Value
        :param value:
        :param args:
        :param kwargs:
        :return:
        """
        if value is None:
            return Boolean.FALSE
        else:
            return Boolean.TRUE + value.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_io:
        :param args:
        :param kwargs:
        :return:
        """
        has_value = Boolean.decode(bytes_io)
        if has_value:
            return cls(value=cls.ITEM_CLS.decode(bytes_io))
        else:
            return cls(value=None)

    def __bytes__(self) -> bytes:
        return Boolean.FALSE if self.value is None else Boolean.TRUE + self.value.bytes


class OptionalBoolean(OptionalX):
    ITEM_CLS: ClassVar[DataType] = Boolean

class OptionalInt(OptionalX):
    ITEM_CLS: ClassVar[DataType] = Int

class OptionalLong(OptionalX):
    ITEM_CLS: ClassVar[DataType] = Long

class OptionalVarInt(OptionalX):
    ITEM_CLS: ClassVar[DataType] = VarInt

class OptionalString(OptionalX):
    ITEM_CLS: ClassVar[DataType] = String

class OptionalTextComponent(OptionalX):
    ITEM_CLS: ClassVar[DataType] = TextComponent

class OptionalPosition(OptionalX):
    ITEM_CLS: ClassVar[DataType] = Position

class OptionalUUID(OptionalX):
    ITEM_CLS: ClassVar[DataType] = UUID

class OptionalIdentifier(OptionalX):
    ITEM_CLS: ClassVar[DataType] = Identifier

class OptionalNBT(OptionalX):
    ITEM_CLS: ClassVar[DataType] = NBT

class OptionalFloat(OptionalX):
    ITEM_CLS: ClassVar[DataType] = Float

class OptionalDouble(OptionalX):
    ITEM_CLS: ClassVar[DataType] = Double

class OptionalIDSet(OptionalX):
    ITEM_CLS: ClassVar[DataType] = IDSet
