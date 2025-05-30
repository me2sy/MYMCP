# -*- coding: utf-8 -*-
"""
    entity
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-05-27 0.2.0 Me2sY  重构

        2025-05-22 0.1.3 Me2sY  完成，注意！未充分测试！

        2025-05-22 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'EntityMetadata'
]

from dataclasses import dataclass
from io import BytesIO
from typing import Self, ClassVar, Optional, Any

from mymcp.data_types import (
    Combined, VarInt, Byte, VarLong, Float, String, TextComponent, OptionalTextComponent, Boolean, Position,
    OptionalPosition, OptionalUUID, NBT, Identifier, IDSet, Int, IDOrX, OptionalIdentifier, UnsignedByte, Field
)
from mymcp.data_types.particle import Particle
from mymcp.data_types.slot import Slot


@dataclass(slots=True)
class WolfVariant(Combined):
    wild_texture: Field | Identifier
    tame_texture: Field | Identifier
    angry_texture: Field | Identifier
    biomes: Field | IDSet


class IDOrWolfVariant(IDOrX):
    ITEM_CLS: ClassVar[WolfVariant] = WolfVariant


@dataclass(slots=True)
class PaintingVariant(Combined):

    width: Field | Int
    height: Field | Int
    asset_id: Field | Identifier
    title: Field | OptionalTextComponent = None
    author: Field | OptionalTextComponent = None


class IDOrPaintingVariant(IDOrX):
    ITEM_CLS: ClassVar[PaintingVariant] = PaintingVariant


EntityMetadataFormatMap = {
    VarInt(0): (Byte,),
    VarInt(1): (VarInt,),
    VarInt(2): (VarLong,),
    VarInt(3): (Float,),
    VarInt(4): (String,),
    VarInt(5): (TextComponent,),
    VarInt(6): (OptionalTextComponent,),
    VarInt(7): (Slot,),
    VarInt(8): (Boolean,),
    VarInt(9): (Float, Float, Float,),
    VarInt(10): (Position,),
    VarInt(11): (OptionalPosition,),
    VarInt(12): (VarInt,),
    VarInt(13): (OptionalUUID,),
    VarInt(14): (VarInt,),
    VarInt(15): (VarInt,),
    VarInt(16): (NBT,),
    VarInt(17): (Particle,),
    VarInt(18): (VarInt, Particle,),
    VarInt(19): (VarInt, VarInt, VarInt,),
    VarInt(20): (VarInt,),
    VarInt(21): (VarInt,),
    VarInt(22): (VarInt,),
    VarInt(23): (IDOrWolfVariant,),
    VarInt(24): (VarInt,),
    VarInt(25): (Boolean, OptionalIdentifier, OptionalPosition),
    VarInt(26): (IDOrPaintingVariant,),
    VarInt(27): (VarInt,),
    VarInt(28): (VarInt,),
    VarInt(29): (Float, Float, Float,),
    VarInt(30): (Float, Float, Float, Float,),
}


@dataclass(slots=True)
class EntityMetadata(Combined):

    index: Field | UnsignedByte
    type_: Field | Optional[VarInt] = None
    values: Field | Optional[tuple[Any, ...]] = None

    def __bytes__(self) -> bytes:
        """
            编码
        :return:
        """
        bs = self.index.bytes
        if self.index.value == 255:
            return bs

        bs += self.type_.bytes

        # particles
        if self.index.value == 18:
            bs += VarInt.encode(len(self.values))
            for particle in self.values:
                bs += particle.bytes
            return bs

        for _ in self.values:
            try:
                bs += _.bytes
            except AttributeError:
                bs += _.encode()

        return bs

    @classmethod
    def decode(cls, bytes_source: BytesIO | bytes, *args, **kwargs) -> Self:
        """
            编码
        :param bytes_source:
        :param args:
        :param kwargs:
        :return:
        """
        bytes_io = cls.to_bytes_io(bytes_source)

        index = UnsignedByte.decode(bytes_io)

        if index.value == 255:
            return cls(index, None, tuple())

        else:
            type_ = VarInt.decode(bytes_io)

            if type_.value == 18:
                array_length = VarInt.decode(bytes_io)
                values = [Particle.decode(bytes_io) for _ in range(array_length.value)]
                return cls(index, type_, tuple(values))

            data_struct = EntityMetadataFormatMap.get(type_, None)
            if data_struct is None:
                raise TypeError(f"{type_} is not a valid entity type")

            data = []
            for _ in data_struct:
                data.append(_.decode(bytes_io))

            return cls(index, type_, tuple(data))
