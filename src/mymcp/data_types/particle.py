# -*- coding: utf-8 -*-
"""
    particle
    ~~~~~~~~~~~~~~~~~~
    粒子效果 Protocol Version 769

    Log:
        2025-05-27 0.2.0 Me2sY  重构

        2025-05-22 0.1.3 Me2sY  完成 1.21.4 编解码功能

        2025-05-19 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'DATA_TYPE_MAP', 'Particle'
]

from dataclasses import dataclass
from typing import IO, Self, Any

from mymcp.data_types import VarInt, Int, Float, Double, Position, Combined, Field
from mymcp.data_types.slot import Slot


DATA_TYPE_MAP = {
    # minecraft:block BlockState
    1: (VarInt,),

    # minecraft:block_marker BlockState
    2: (VarInt,),

    # minecraft:dust RGB Scale
    # The color, encoded as 0xRRGGBB; top bits are ignored.
    # Scale. The scale, will be clamped between 0.01 and 4.
    13: (Int, Float,),

    # minecraft:dust_color_transition   From To RGB  Scale
    14: (Int, Int, Float,),

    # minecraft:entity_effect   The ARGB components of the color encoded as an Int
    20: (Int,),

    # minecraft:falling_dust BlockState
    28: (VarInt,),

    # minecraft:sculk_charge	Roll How much the particle will be rotated when displayed.
    36: (Float,),

    # # minecraft:item	The item that will be used.
    45: (Slot,),

    # minecraft:vibration
    # Position Source Type	VarInt	The type of the vibration source (0 for `minecraft:block`, 1 for `minecraft:entity`)
    # Block Position    Position    The position of the block the vibration originated from. Only present if Position Type is minecraft:block.
    # Entity ID VarInt  The ID of the entity the vibration originated from. Only present if Position Type is minecraft:entity.
    # Entity eye height Float   The height of the entity's eye relative to the entity. Only present if Position Type is minecraft:entity.
    # Ticks	VarInt	The amount of ticks it takes for the vibration to travel from its source to its destination.
    46: (VarInt, Position, VarInt, Float, VarInt),

    47: (Double, Double, Double, Int, VarInt),

    # minecraft:shriek	The time in ticks before the particle is displayed
    101: (VarInt,),

    # minecraft:dust_pillar	 BlockState The ID of the block state.
    107: (VarInt,),

    # minecraft:block_crumble The ID of the block state.
    111: (VarInt,),
}


@dataclass(slots=True)
class Particle(Combined):
    """
        粒子效果
    """
    particle: Field | VarInt
    particle_data: Field | tuple[Any, ...]

    def encode(self, *args, **kwargs) -> bytes:
        bs = self.particle.bytes
        for _ in self.particle_data:
            bs += _.bytes
        return bs

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        particle_id = VarInt.decode(bytes_io)
        data_struct = DATA_TYPE_MAP.get(particle_id, None)
        if data_struct is None:
            return cls(particle_id, ())

        data = []
        for _ in data_struct:
            data.append(_.decode(bytes_io))
        return cls(particle_id, tuple(data))

    def __bytes__(self) -> bytes:
        bs = self.particle.bytes
        for _ in self.particle_data:
            bs += _.bytes
        return bs
