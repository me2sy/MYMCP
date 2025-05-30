# -*- coding: utf-8 -*-
"""
    protocol
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-05-29 0.2.0 Me2sY  创建，实现 protocol 中特殊结构
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'AdvancementMapping', 'ProgressMapping',
    'Advancement', 'AdvancementDisplay', 'AdvancementProgress',
    'OptionalAdvancementDisplay', 'OptionalSignature256', 'TradeItem', 'Trade'
]

from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Self

from mymcp.data_types import (
    Combined, Field, TextComponent, VarInt, Int, Float, Identifier, DataPacket, OptionalLong, OptionalIdentifier,
    OptionalX, String, Boolean, Byte
)
from mymcp.data_types.slot import Slot, Component


@dataclass(slots=True)
class AdvancementDisplay(Combined):

    title: Field | TextComponent
    description: Field | TextComponent
    icon: Field | Slot
    frame_type: Field | VarInt
    flags: Field | Int
    x_coord: Field | Float
    y_coord: Field | Float
    background_texture: Field | Optional[Identifier] = None

    def __bytes__(self) -> bytes:
        return (
            self.title.bytes + self.description.bytes + self.icon.bytes +
            self.frame_type.bytes + self.flags.bytes +
            self.background_texture.bytes if self.background_texture else b'' +
            self.x_coord.bytes + self.y_coord.bytes
        )

    @classmethod
    def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
        bytes_io = cls.to_bytes_io(bytes_source)

        title = TextComponent.decode(bytes_io)
        description = TextComponent.decode(bytes_io)
        icon = Slot.decode(bytes_io)
        frame_type = VarInt.decode(bytes_io)
        flags = Int.decode(bytes_io)

        if flags.value & 0x01:
            background_texture = Identifier.decode(bytes_io)
        else:
            background_texture = None

        x_coord = Float.decode(bytes_io)
        y_coord = Float.decode(bytes_io)

        return cls(
            title, description, icon, frame_type, flags, x_coord, y_coord, background_texture
        )


class OptionalAdvancementDisplay(OptionalX):
    ITEM_CLS = AdvancementDisplay


@dataclass(slots=True)
class Advancement(Combined):
    parent_id: Field | OptionalIdentifier
    display_data: Field | OptionalAdvancementDisplay
    nested_requirements: Field | list[list[String]]
    sends_telemetry_data: Field | Boolean

    @classmethod
    def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
        bytes_io = cls.to_bytes_io(bytes_source)
        parent_id = OptionalIdentifier.decode(bytes_io)
        display_data = OptionalAdvancementDisplay.decode(bytes_io)
        array_length = VarInt.decode(bytes_io)
        nested = []
        for _ in range(array_length.value):
            nested.append([
                String.decode(bytes_io) for __ in range(VarInt.decode(bytes_io).value)
            ])
        sends_telemetry_data = Boolean.decode(bytes_io)
        return cls(parent_id, display_data, nested, sends_telemetry_data)

    def __bytes__(self) -> bytes:
        bs = self.parent_id.bytes + self.display_data.bytes
        bs += VarInt.encode(len(self.nested_requirements))
        for _ in self.nested_requirements:
            bs += VarInt.encode(len(_))
            for __ in _:
                bs += __.bytes
        return bs + self.sends_telemetry_data.bytes


@dataclass(slots=True)
class AdvancementProgress(Combined):
    criterion_identifier: Field | Identifier
    date_of_achieving: Field | OptionalLong


@dataclass(slots=True)
class AdvancementMapping(Combined):
    key: Field | Identifier
    value: Field | Advancement


@dataclass(slots=True)
class ProgressMapping(Combined):
    key: Field | Identifier
    value: Field | list[AdvancementProgress]


@dataclass(slots=True)
class OptionalSignature256(Combined):
    signature: Field | Optional[list[Byte]] = None

    def __bytes__(self) -> bytes:
        if self.signature:
            return Boolean.TRUE + b''.join(_.bytes for _ in self.signature)
        else:
            return Boolean.FALSE

    @classmethod
    def decode(cls, bytes_source: bytes | DataPacket | BytesIO) -> Self:
        bytes_io = cls.to_bytes_io(bytes_source)
        has_signature = Boolean.decode(bytes_io)
        if has_signature:
            return cls(signature=[Byte.decode(bytes_io) for _ in range(256)])
        else:
            return cls(signature=None)


@dataclass(slots=True)
class TradeItem(Combined):
    item_id: Field | VarInt
    item_count: Field | VarInt
    components: Field | list[Component]


class OptionalTradeItem(OptionalX):
    ITEM_CLS = TradeItem


@dataclass(slots=True)
class Trade(Combined):

    input_item_1: Field | TradeItem
    output_item: Field | Slot
    input_item_2: Field | OptionalTradeItem
    trade_disabled: Field | Boolean
    number_of_trade_uses: Field | Int
    maximum_number_of_trade_uses: Field | Int
    xp: Field | Int
    special_price: Field | Int
    price_multiplier: Field | Float
    demand: Field | Int
