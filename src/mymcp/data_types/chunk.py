# -*- coding: utf-8 -*-
"""
    chunk
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-05-26 0.2.0 Me2sY  重构结构

        2025-05-22 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'ChunkData', 'LightData', 'ChunkSection', 'BlockEntity',
    'PalettedContainer', 'PalettedContainerBiomes', 'PalettedContainerBlocks'
]

from dataclasses import dataclass
from io import BytesIO
from typing import ClassVar, Self, Union

from mymcp.data_types import (
    UnsignedByte, VarInt, Short, NBT, BitSet, Combined, Field, UnsignedLong, InnerField, Byte, DataPacket
)


@dataclass
class PalettedContainer(Combined):

    SINGLE_VALUED: ClassVar[int] = 0
    INDIRECT_MIN: ClassVar[int] = 4
    INDIRECT_MAX: ClassVar[int] = 8
    DIRECT: ClassVar[int] = 15

    TYPE_SINGLE_VALUE: ClassVar[int] = 0
    TYPE_INDIRECT: ClassVar[int] = 1
    TYPE_DIRECT: ClassVar[int] = 2

    bits_per_entry: Field | UnsignedByte
    palette: Field | Union[VarInt, list[VarInt], None] = None
    data_array: Field | list[UnsignedLong] = None
    paletted_type: InnerField | int = -1

    def __bytes__(self) -> bytes:
        """
            编码
        :return:
        """
        bs = self.bits_per_entry.bytes
        if self.palette is not None:
            bs += self.palette.bytes
        return bs + self.list_to_bytes(self.data_array)

    @classmethod
    def decode(cls, bytes_source: bytes | BytesIO, *args, **kwargs) -> Self:
        """
            解码
        :param bytes_source:
        :param args:
        :param kwargs:
        :return:
        """
        bytes_io = cls.to_bytes_io(bytes_source)
        bits_per_entry = UnsignedByte.decode(bytes_io)

        if bits_per_entry.value == cls.SINGLE_VALUED:
            palette = VarInt.decode(bytes_io)
            paletted_type = cls.TYPE_SINGLE_VALUE

        elif cls.INDIRECT_MIN <= bits_per_entry.value <= cls.INDIRECT_MAX:
            palette = cls.bytes_to_list(bytes_io, VarInt)[1]
            paletted_type = cls.TYPE_INDIRECT

        elif bits_per_entry.value >= cls.DIRECT:
            palette = None
            paletted_type = cls.TYPE_DIRECT

        else:
            raise ValueError(f'Invalid bits_per_entry {bits_per_entry}')

        return cls(bits_per_entry, palette, cls.bytes_to_list(bytes_io, UnsignedLong)[1], paletted_type)


@dataclass
class PalettedContainerBlocks(PalettedContainer): ...


@dataclass
class PalettedContainerBiomes(PalettedContainer):

    INDIRECT_MIN: ClassVar[int] = 1
    INDIRECT_MAX: ClassVar[int] = 3
    DIRECT: ClassVar[int] = 6


@dataclass
class ChunkSection(Combined):

    block_count: Field | Short
    block_states: Field | PalettedContainerBlocks
    biomes: Field | PalettedContainerBiomes


@dataclass
class BlockEntity(Combined):

    packed_xz: Field | UnsignedByte
    y: Field | Short
    type_: Field | VarInt
    data: Field | NBT


@dataclass
class ChunkData(Combined):

    heightmaps: Field | NBT
    chunk_byte_size: Field | VarInt
    chunk_sections: Field | list[ChunkSection]
    block_entities: Field | list[BlockEntity]
    dimension_chunk_size: InnerField | int = 24

    def __repr__(self):
        return f"<ChunkData>({self.chunk_byte_size} {len(self.chunk_sections)})"

    def __bytes__(self) -> bytes:
        bs = self.heightmaps.bytes + self.chunk_byte_size.bytes + b''.join(_.bytes for _ in self.chunk_sections)
        return bs + self.list_to_bytes(self.block_entities)

    @classmethod
    def decode(
            cls, bytes_source: bytes | BytesIO | DataPacket, dimension_chunk_size: int = 24, *args, **kwargs
    ) -> Self:
        bytes_io = cls.to_bytes_io(bytes_source)
        heightmaps = NBT.decode(bytes_io)
        chunk_byte_size = VarInt.decode(bytes_io)
        chunk_sections = [
            ChunkSection.decode(bytes_io) for _ in range(dimension_chunk_size)
        ]
        block_entities = cls.bytes_to_list(bytes_io, BlockEntity)[1]
        return cls(
            heightmaps, chunk_byte_size, chunk_sections, block_entities, dimension_chunk_size=dimension_chunk_size
        )


@dataclass(slots=True)
class LightData(Combined):

    @dataclass(slots=True)
    class LightArray(Combined):
        lights: Field | list[Byte]

    sky_light_mask: Field | BitSet
    block_light_mask: Field | BitSet
    empty_sky_light_mask: Field | BitSet
    empty_block_light_mask: Field | BitSet
    sky_light_arrays: Field | list[LightArray]
    block_light_arrays: Field | list[LightArray]
