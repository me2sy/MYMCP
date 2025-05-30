# -*- coding: utf-8 -*-
"""
    slot
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-05-27 0.2.0 Me2sY  架构重构，未充分测试.

        2025-05-22 0.1.3 Me2sY  完成 1.21.4 编写，类别格式太多。。。未充分测试

        2025-05-19 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'Slot', 'ComponentDataStructMap', 'Component', 'SlotDisplay', 'RecipeDisplay'
]

from dataclasses import dataclass
from typing import Optional, IO, Self, ClassVar, Any, Union

from mymcp.data_types import (
    Boolean, VarInt, String, IDSet, NBT, Identifier, TextComponent, Double, Float, IDOrSoundEvent, SoundEvent,
    Int, IDOrX, Byte, Position, Combined, Field, OptionalVarInt, OptionalInt, OptionalIdentifier, OptionalFloat,
    OptionalBoolean, OptionalIDSet, OptionalString, OptionalTextComponent, OptionalUUID
)


@dataclass(slots=True)
class BlockProperty(Combined):
    """
        Is Exact Match	Boolean	Whether this is an exact value match, as opposed to ranged.
        Exact Value	Optional String	Value of the block state property. Only present in exact match mode.
        Min Value	Optional String	Minimum value of the block state property range. Only present in ranged match mode.
        Max Value	Optional String	Maximum value of the block state property range. Only present in ranged match mode.
    """
    name: Field | String
    exact_value: Field | Optional[String] = None
    min_value: Field | Optional[String] = None
    max_value: Field | Optional[String] = None

    def __bytes__(self) -> bytes:
        if self.exact_value is None:
            return self.name.bytes + Boolean.FALSE + self.min_value.bytes + self.max_value.bytes
        else:
            return self.name.bytes + Boolean.TRUE + self.exact_value.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        name = String.decode(bytes_io)
        is_exact_match = Boolean.decode(bytes_io)
        if is_exact_match:
            # Exact Value
            values = [String.decode(bytes_io), None, None]
        else:
            # Minimum Values
            values = [None, String.decode(bytes_io), String.decode(bytes_io)]
        return cls(name, *values)


@dataclass(slots=True)
class BlockPredicate(Combined):

    blocks: Field | Optional[IDSet] = None
    properties: Field | Optional[list[BlockProperty]] = None
    nbt: Field | Optional[NBT] = None

    def __bytes__(self) -> bytes:

        bs = bytes()

        # Blocks
        if self.blocks is None:
            bs += Boolean.FALSE
        else:
            bs += Boolean.TRUE + self.blocks.bytes

        # Properties
        if self.properties is None:
            bs += Boolean.FALSE
        else:
            bs += Boolean.TRUE + VarInt.encode(len(self.properties))
            for prop in self.properties:
                bs += prop.bytes

        # NBT
        if self.nbt is None:
            bs += Boolean.FALSE
        else:
            bs += Boolean.TRUE + self.nbt.bytes

        return bs

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        instance = cls()

        if Boolean.decode(bytes_io):
            instance.blocks = IDSet.decode(bytes_io)

        if Boolean.decode(bytes_io):
            array_length = VarInt.decode(bytes_io)
            instance.properties = [
                BlockProperty.decode(bytes_io) for _ in range(array_length.value)
            ]

        if Boolean.decode(bytes_io):
            instance.nbt = NBT.decode(bytes_io)

        return instance


@dataclass(slots=True)
class Enchantment(Combined):

    type_id: Field | VarInt
    level: Field | VarInt


@dataclass(slots=True)
class Enchantments(Combined):
    enchantments: Field | list[Enchantment]
    show_in_tooltip: Field | Boolean


@dataclass(slots=True)
class CanPlaceOnORBreak(Combined):
    block_predicates: Field | list[BlockPredicate]
    show_in_tooltip: Field | Boolean


@dataclass(slots=True)
class AttributeModifier(Combined):
    attribute_id: Field | VarInt
    modifier_id: Field | Identifier
    value: Field | Double
    operation: Field | VarInt
    slot: Field | VarInt


@dataclass(slots=True)
class AttributeModifiers(Combined):
    attribute_modifiers: Field | list[AttributeModifier]
    show_in_tooltip: Field | Boolean


@dataclass(slots=True)
class ModelData(Combined):
    floats: Field | list[Float]
    flags: Field | list[Boolean]
    strings: Field | list[String]
    colors: Field | list[Int]


@dataclass(slots=True)
class Food(Combined):
    nutrition: Field | VarInt
    saturation_modifier: Field | Float
    can_always_eat: Field | Boolean


@dataclass(slots=True)
class PotionEffectDetail(Combined):
    amplifier: Field | VarInt
    duration: Field | VarInt
    ambient: Field | Boolean
    show_particles: Field | Boolean
    show_icon: Field | Boolean
    hidden_effect: Field | Optional[Self] = None

    def __bytes__(self) -> bytes:
        return self.amplifier.bytes + self.duration.bytes + self.ambient.bytes + self.show_particles.bytes + self.show_icon.bytes + b'' if self.hidden_effect is None else self.hidden_effect.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        amplifier = VarInt.decode(bytes_io)
        duration = VarInt.decode(bytes_io)
        ambient = Boolean.decode(bytes_io)
        show_particles = Boolean.decode(bytes_io)
        show_icon = Boolean.decode(bytes_io)
        return cls(amplifier, duration, ambient, show_particles, show_icon,
                   cls.decode(bytes_io) if Boolean.decode(bytes_io) else None)


@dataclass(slots=True)
class PotionEffect(Combined):
    type_id: Field | VarInt
    effect: Field | PotionEffectDetail


@dataclass(slots=True)
class PotionContents(Combined):
    potion_id: Field | OptionalVarInt
    custom_color: Field | OptionalInt
    custom_effects: Field | list[PotionEffect]
    custom_name: Field | String


@dataclass(slots=True)
class ConsumeEffect(Combined):
    type_: Field | VarInt
    data: Field | Any

    def __bytes__(self) -> bytes:
        if self.type_.value == 0:
            bs = self.type_.bytes + VarInt.encode(len(self.data[0]))
            bs += b''.join(effect.bytes for effect in self.data[0])
            return bs + self.data[1].bytes

        elif self.type_.value in [1, 3, 4]:
            return self.type_.bytes + self.data.type_

        elif self.type_.value == 2:
            return self.type_.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        _type = VarInt.decode(bytes_io)
        if _type.value == 0:
            array_length = VarInt.decode(bytes_io)
            effects = [PotionEffect.decode(bytes_io) for _ in range(array_length.value)]
            probability = Float.decode(bytes_io)
            return cls(_type, (effects, probability,))

        elif _type.value == 1:
            return cls(_type, IDSet.decode(bytes_io))

        elif _type.value == 2:
            return cls(_type, None)

        elif _type.value == 3:
            return cls(_type, Float.decode(bytes_io))

        elif _type.value == 4:
            return cls(_type, SoundEvent.decode(bytes_io))


@dataclass(slots=True)
class Consumable(Combined):
    consume_seconds: Field | Float
    animation: Field | VarInt
    sound: Field | IDOrSoundEvent
    has_consume_particles: Field | Boolean
    effects: Field | list[ConsumeEffect]


@dataclass(slots=True)
class UseCooldown(Combined):
    seconds: Field | Float
    cooldown: Field | OptionalIdentifier


@dataclass(slots=True)
class ToolRule(Combined):
    blocks: Field | IDSet
    speed: Field | OptionalFloat
    correct_drop_for_blocks: Field | OptionalBoolean


@dataclass(slots=True)
class Tool(Combined):
    rules: Field | list[ToolRule]
    default_mining_speed: Field | Float
    damage_per_block: Field | VarInt


@dataclass(slots=True)
class Weapon(Combined):
    damage_per_block: Field | VarInt
    disable_blocking_for: Field | Float


@dataclass(slots=True)
class Equippable(Combined):
    slot: Field | VarInt
    equip_sound: Field | IDOrSoundEvent
    model: Field | OptionalIdentifier
    camera_overlay: Field | OptionalIdentifier
    allowed_entities: Field | OptionalIDSet
    dispensable: Field | Boolean
    swappable: Field | Boolean
    damage_on_hurt: Field | Boolean


@dataclass(slots=True)
class WritableBookContent(Combined):
    raw_content: Field | String
    filtered_content: Field | OptionalString


@dataclass(slots=True)
class Page(Combined):
    raw_content: Field | TextComponent
    filtered_content: Field | OptionalTextComponent


@dataclass(slots=True)
class WrittenBookContent(Combined):
    raw_title: Field | String
    filtered_title: Field | OptionalString
    author: Field | String
    generation: Field | VarInt
    pages: Field | list[Page]
    resolved: Field | Boolean


@dataclass(slots=True)
class Override(Combined):
    armor_material_type: Field | Identifier
    overriden_asset_name: Field | String


@dataclass(slots=True)
class TrimMaterial(Combined):
    suffix: Field | String
    overrides: Field | list[Override]
    description: Field | TextComponent


@dataclass(slots=True)
class TrimPattern(Combined):
    asset_name: Field | String
    template_item: Field | VarInt
    description: Field | TextComponent
    decal: Field | Boolean


class IDOrTrimMaterial(IDOrX):
    ITEM_CLS = TrimMaterial


class IDOrTrimPattern(IDOrX):
    ITEM_CLS = TrimPattern


@dataclass(slots=True)
class Instrument(Combined):
    sound_event: Field | IDOrSoundEvent
    sound_range: Field | Float
    range_: Field | Float
    description: Field | TextComponent


class IDOrInstrument(IDOrX):
    ITEM_CLS = Instrument


@dataclass(slots=True)
class Material(Combined):
    mode: Field | Byte
    material: Field | Union[Identifier, IDOrTrimMaterial]

    def __bytes__(self) -> bytes:
        return self.mode.bytes + self.material.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        mode = Byte.decode(bytes_io)
        if mode.value == 0:
            return cls(mode, Identifier.decode(bytes_io))
        else:
            return cls(mode, IDOrTrimMaterial.decode(bytes_io))


@dataclass(slots=True)
class JukeboxSong(Combined):
    sound_event: Field | IDOrSoundEvent
    description: Field | TextComponent
    duration: Field | Float
    output: Field | VarInt


class IDOrJukeboxSong(IDOrX):
    ITEM_CLS = JukeboxSong


# 1.21.5
# class JukeboxPlayable(DataStruct):
#     def __init__(self, mode: Byte, jukebox_song: Identifier | IDOrJukeboxSong):
#         self.mode: Byte = mode
#         self.jukebox_song: Identifier = jukebox_song
#
#     def encode(self, *args, **kwargs) -> bytes:
#         return self.mode.bytes + self.jukebox_song.bytes
#
#     @classmethod
#     def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
#         mode = Byte.decode(bytes_io)
#         if mode.value == 0:
#             return cls(mode, Identifier.decode(bytes_io))
#         else:
#             return cls(mode, IDOrJukeboxSong.decode(bytes_io))


@dataclass(slots=True)
class JukeboxPlayable(Combined):
    direct_mode: Field | Boolean
    jukebox_song: Field | Union[Identifier, IDOrJukeboxSong]
    show_in_tooltip: Field | Boolean

    def __bytes__(self) -> bytes:
        return self.direct_mode.bytes + self.jukebox_song.bytes + self.show_in_tooltip.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        direct_mode = Boolean.decode(bytes_io)
        if direct_mode:
            return cls(direct_mode, IDOrJukeboxSong.decode(bytes_io), Boolean.decode(bytes_io))
        else:
            return cls(direct_mode, Identifier.decode(bytes_io), Boolean.decode(bytes_io))


@dataclass(slots=True)
class FireworkExplosion(Combined):
    shape: Field | VarInt
    colors: Field | list[Int]
    fade_colors: Field | list[Int]
    has_trail: Field | Boolean
    has_twinkler: Field | Boolean


@dataclass(slots=True)
class SuspiciousStewEffect(Combined):
    type_id: Field | VarInt
    duration: Field | VarInt


@dataclass(slots=True)
class ProfileProperty(Combined):
    name: Field | String
    value: Field | String
    signature: Field | OptionalString


@dataclass(slots=True)
class Profile(Combined):
    name: Field | OptionalString
    unique_id: Field | OptionalUUID
    properties: Field | list[ProfileProperty]


@dataclass(slots=True)
class BannerPatterns(Combined):
    pattern_type: Field | VarInt
    asset_id: Field | OptionalIdentifier
    translation_key: Field | OptionalString
    color: Field | VarInt


@dataclass(slots=True)
class BlockStateProperty(Combined):
    name: Field | String
    value: Field | String


@dataclass(slots=True)
class Bee(Combined):
    entity_data: Field | NBT
    ticks_in_hive: Field | VarInt
    min_ticks_in_hive: Field | VarInt


@dataclass(slots=True)
class Component(Combined):
    type_: Field | VarInt
    data: Field | Any = None

    def __bytes__(self) -> bytes:
        bs = self.type_.bytes

        if self.data is None:
            return bs

        if isinstance(self.data, tuple):
            for _ in self.data:
                try:
                    bs += _.bytes
                except AttributeError:
                    bs += _.encode()
            return bs

        return bs + self.data.bytes

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        ct = VarInt.decode(bytes_io)

        cds: ComponentDataStruct = ComponentDataStructMap.get(ct, None)
        if cds is None:
            raise TypeError(f"Unknown component type: {ct.value}")

        if cds.data_struct is None:
            return cls(ct, None)

        if isinstance(cds.data_struct, tuple):
            data = []
            for _ in cds.data_struct:
                data.append(_.decode(bytes_io))
            return cls(ct, tuple(data))

        if isinstance(cds.data_struct, list):
            data_struct = cds.data_struct[0]
            array_length = VarInt.decode(bytes_io)
            return cls(ct, tuple([data_struct.decode(bytes_io) for _ in range(array_length.value)]))

        return cls(ct, cds.data_struct.decode(bytes_io))


@dataclass(slots=True)
class Slot(Combined):
    item_count: Field | VarInt
    item_id: Field | Optional[VarInt] = None
    number_of_components_to_add: Field | Optional[VarInt] = None
    number_of_components_to_remove: Field | Optional[VarInt] = None
    components_to_add: Field | list[Component] = None
    components_to_remove: Field | list[VarInt] = None

    def __bytes__(self) -> bytes:
        bs = self.item_count.bytes
        if self.item_count.value > 0:
            bs += self.item_id.bytes
            bs += self.number_of_components_to_add.bytes
            bs += self.number_of_components_to_remove.bytes
            for _ in self.components_to_add:
                bs += _.bytes
            for _ in self.components_to_remove:
                bs += _.bytes
        return bs

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        item_count = VarInt.decode(bytes_io)
        if item_count.value == 0:
            return cls(item_count)

        item_id = VarInt.decode(bytes_io)
        number_of_components_to_add = VarInt.decode(bytes_io)
        number_of_components_to_remove = VarInt.decode(bytes_io)

        components_to_add = []
        for _ in range(number_of_components_to_add.value):
            components_to_add.append(Component.decode(bytes_io))

        components_to_remove = []
        for _ in range(number_of_components_to_remove.value):
            components_to_remove.append(VarInt.decode(bytes_io))

        return cls(
            item_count, item_id, number_of_components_to_add,
            number_of_components_to_remove, components_to_add, components_to_remove
        )


@dataclass
class ComponentDataStruct:
    name: str
    tid: int
    data_struct: Optional[Any] = None


# 1.21.4
ComponentDataStructMap = {
    # Customizable data that doesn't fit any specific component.
    VarInt(0): ComponentDataStruct(name='custom_data', tid=0, data_struct=NBT),

    # Maximum stack size for the item.
    VarInt(1): ComponentDataStruct(name='max_stack_size', tid=1, data_struct=VarInt),

    # The maximum damage the item can take before breaking.
    VarInt(2): ComponentDataStruct(name='max_damage', tid=2, data_struct=VarInt),

    # The current damage of the item.
    VarInt(3): ComponentDataStruct(name='damage', tid=3, data_struct=VarInt),

    # Marks the item as unbreakable.
    VarInt(4): ComponentDataStruct(name='unbreakable', tid=4, data_struct=Boolean),

    # Item's custom name.
    # Normally shown in italic, and changeable at an anvil.
    VarInt(5): ComponentDataStruct(name='custom_name', tid=5, data_struct=TextComponent),

    # Override for the item's default name.
    # Shown when the item has no custom name.
    VarInt(6): ComponentDataStruct(name='item_name', tid=6, data_struct=TextComponent),

    # Item's model.
    VarInt(7): ComponentDataStruct(name='item_model', tid=7, data_struct=Identifier),

    # Item's lore.
    VarInt(8): ComponentDataStruct(name='lore', tid=8, data_struct=[TextComponent]),

    # Item's rarity.
    # This affects the default color of the item's name.
    VarInt(9): ComponentDataStruct(name='rarity', tid=9, data_struct=VarInt),

    # The enchantments of the item.
    VarInt(10): ComponentDataStruct(name='enchantments', tid=10, data_struct=Enchantments),

    # List of blocks this block can be placed on when in adventure mode.
    VarInt(11): ComponentDataStruct(name='can_place_on', tid=11, data_struct=CanPlaceOnORBreak),

    # List of blocks this item can break when in adventure mode.
    VarInt(12): ComponentDataStruct(name='can_break', tid=12, data_struct=CanPlaceOnORBreak),

    # The attribute modifiers of the item.
    VarInt(13): ComponentDataStruct(name='attribute_modifiers', tid=13, data_struct=AttributeModifiers),

    # Value for the item predicate when using custom item models.
    VarInt(14): ComponentDataStruct(name='custom_model_data', tid=14, data_struct=ModelData),

    # # Hides the item's tooltip altogether.
    # VarInt(15): ComponentDataStruct(name='tooltip_display', tid=15, data_struct=None),

    VarInt(15): ComponentDataStruct(name='hide_additional_tooltip', tid=15, data_struct=None),

    VarInt(16): ComponentDataStruct(name='hide_tooltip', tid=16, data_struct=None),

    # Accumulated anvil usage cost. The client displays "Too Expensive"
    # if the value is greater than 40 and the player is not in creative mode
    # (more specifically, if they don't have the insta-build flag enabled).
    # This behavior can be overridden by setting the level with the Set Container Property packet.
    VarInt(17): ComponentDataStruct(name='repair_cost', tid=17, data_struct=VarInt),

    # Marks the item as non-interactive on the creative inventory (the first 5 rows of items).
    # This is used internally by the client on the paper icon in the saved hot-bars tab.
    VarInt(18): ComponentDataStruct(name='creative_slot_lock', tid=18, data_struct=None),

    # Overrides the item glint resulted from enchantments
    VarInt(19): ComponentDataStruct(name='enchantment_glint_override', tid=19, data_struct=Boolean),

    # Marks the projectile as intangible (cannot be picked-up).
    VarInt(20): ComponentDataStruct(name='intangible_projectile', tid=20, data_struct=NBT),

    # Makes the item restore the player's hunger bar when consumed.
    VarInt(21): ComponentDataStruct(name='food', tid=21, data_struct=Food),

    # Makes the item consumable.
    VarInt(22): ComponentDataStruct(name='consumable', tid=22, data_struct=Consumable),

    # This specifies the item produced after using the current item. In the Notchian server, this is used for stews, which turn into bowls.
    VarInt(23): ComponentDataStruct(name='use_remainder', tid=23, data_struct=Slot),

    # Cooldown to apply on use of the item.
    VarInt(24): ComponentDataStruct(name='use_cooldown', tid=24, data_struct=UseCooldown),

    # Marks this item as damage resistant.
    # The client won't render the item as being on-fire if this component is present.
    VarInt(25): ComponentDataStruct(name='damage_resistant', tid=25, data_struct=Identifier),

    # Alters the speed at which this item breaks certain blocks
    VarInt(26): ComponentDataStruct(name='tool', tid=26, data_struct=Tool),

    # # Item treated as a weapon
    # VarInt(27): ComponentDataStruct(name='weapon', tid=27, data_struct=Weapon),

    # Allows the item to be enchanted by an enchanting table.
    VarInt(27): ComponentDataStruct(name='enchantable', tid=27, data_struct=VarInt),

    # Allows the item to be equipped by the player.
    VarInt(28): ComponentDataStruct(name='equippable', tid=28, data_struct=Equippable),

    # Items that can be combined with this item in an anvil to repair it.
    VarInt(29): ComponentDataStruct(name='repairable', tid=29, data_struct=IDSet),

    # Makes the item function like elytra.
    VarInt(30): ComponentDataStruct(name='glider', tid=30, data_struct=None),

    # Custom textures for the item tooltip.
    VarInt(31): ComponentDataStruct(name='tooltip_style', tid=31, data_struct=Identifier),

    # Makes the item function like a totem of undying.
    VarInt(32): ComponentDataStruct(name='death_protection', tid=32, data_struct=list[ConsumeEffect]),

    # # TODO: add
    # VarInt(33): ComponentDataStruct(name='blocks_attacks', tid=33, data_struct=None),

    # The enchantments stored in this enchanted book.
    VarInt(33): ComponentDataStruct(name='stored_enchantments', tid=33, data_struct=Enchantments),

    # Color of dyed leather armor.
    VarInt(34): ComponentDataStruct(name='dyed_color', tid=34, data_struct=(Int, Boolean,)),

    # Color of the markings on the map item model.
    VarInt(35): ComponentDataStruct(name='map_color', tid=35, data_struct=Int),

    # The ID of the map.
    VarInt(36): ComponentDataStruct(name='map_id', tid=36, data_struct=VarInt),

    # Icons present on a map.
    VarInt(37): ComponentDataStruct(name='map_decorations', tid=37, data_struct=NBT),

    # Used internally by the client when expanding or locking a map. Display extra information on the item's tooltip when the component is present.
    VarInt(38): ComponentDataStruct(name='map_post_processing', tid=38, data_struct=VarInt),

    # Projectiles loaded into a charged crossbow.
    VarInt(39): ComponentDataStruct(name='charged_projectiles', tid=39, data_struct=[Slot]),

    # Contents of a bundle.
    VarInt(40): ComponentDataStruct(name='bundle_contents', tid=40, data_struct=[Slot]),

    # Visual and effects of a potion item.
    VarInt(41): ComponentDataStruct(name='potion_contents', tid=41, data_struct=PotionContents),

    # # TODO: add desc
    # VarInt(42): ComponentDataStruct(name='potion_duration_scale', tid=42, data_struct=Float),

    # Effects granted by a suspicious stew.
    VarInt(42): ComponentDataStruct(name='suspicious_stew_effects', tid=42, data_struct=[SuspiciousStewEffect]),

    # Content of a writable book.
    VarInt(43): ComponentDataStruct(name='writable_book_content', tid=43, data_struct=WritableBookContent),

    # Content of a written and signed book.
    VarInt(44): ComponentDataStruct(name='written_book_content', tid=44, data_struct=WrittenBookContent),

    # Armor's trim pattern and color
    VarInt(45): ComponentDataStruct(name='trim', tid=45, data_struct=(IDOrTrimMaterial, IDOrTrimPattern)),

    # State of the debug stick
    VarInt(46): ComponentDataStruct(name='debug_stick_state', tid=46, data_struct=NBT),

    # Data for the entity to be created from this item.
    VarInt(47): ComponentDataStruct(name='entity_data', tid=47, data_struct=NBT),

    # Data of the entity contained in this bucket.
    VarInt(48): ComponentDataStruct(name='bucket_entity_data', tid=48, data_struct=NBT),

    # Data of the block entity to be created from this item.
    VarInt(49): ComponentDataStruct(name='block_entity_data', tid=49, data_struct=NBT),

    # The sound played when using a goat horn.
    VarInt(50): ComponentDataStruct(name='instrument', tid=50, data_struct=IDOrInstrument),

    # # TODO: add
    # VarInt(53): ComponentDataStruct(name='provides_trim_material', tid=53, data_struct=Material),

    # Amplifier for the effect of an ominous bottle.
    VarInt(51): ComponentDataStruct(name='ominous_bottle_amplifier', tid=51, data_struct=VarInt),

    # The song this item will play when inserted into a jukebox.
    # The Notchian client assumes that the server will always represent the jukebox song either by name,
    # or reference an entry on its respective registry.
    # Trying to directly specify a jukebox song (when Jukebox Song Type is 0) will cause the client
    # to fail to parse it and subsequently disconnect, which is likely an unintended bug.
    VarInt(52): ComponentDataStruct(name='jukebox_playable', tid=52, data_struct=JukeboxPlayable),

    # # TODO: add
    # VarInt(56): ComponentDataStruct(name='provides_banner_pattern', tid=56, data_struct=Identifier),

    # The recipes this knowledge book unlocks.
    VarInt(53): ComponentDataStruct(name='recipes', tid=53, data_struct=NBT),

    # The lodestone this compass points to.
    VarInt(54): ComponentDataStruct(name='lodestone_tracker', tid=54,
                                    data_struct=(Boolean, Identifier, Position, Boolean)),

    # Properties of a firework star.
    VarInt(55): ComponentDataStruct(name='firework_explosion', tid=55, data_struct=FireworkExplosion),

    # Properties of a firework.
    VarInt(56): ComponentDataStruct(name='fireworks', tid=56, data_struct=(VarInt, [FireworkExplosion])),

    # Game Profile of a player's head.
    VarInt(57): ComponentDataStruct(name='profile', tid=57, data_struct=Profile),

    # Sound played by a note block when this player's head is placed on top of it.
    VarInt(58): ComponentDataStruct(name='note_block_sound', tid=58, data_struct=Identifier),

    # Patterns of a banner or banner applied to a shield.
    VarInt(59): ComponentDataStruct(name='banner_patterns', tid=59, data_struct=[BannerPatterns]),

    # Base color of the banner applied to a shield.
    VarInt(60): ComponentDataStruct(name='base_color', tid=60, data_struct=VarInt),

    # Decorations on the four sides of a pot.
    VarInt(61): ComponentDataStruct(name='pot_decorations', tid=61, data_struct=[VarInt]),

    # Items inside a container of any type.
    VarInt(62): ComponentDataStruct(name='container', tid=62, data_struct=[Slot]),

    # State of a block.
    VarInt(63): ComponentDataStruct(name='block_state', tid=63, data_struct=[BlockStateProperty]),

    # Bees inside a hive.
    VarInt(64): ComponentDataStruct(name='bees', tid=64, data_struct=[Bee]),

    # Name of the necessary key to open this container.
    VarInt(65): ComponentDataStruct(name='lock', tid=65, data_struct=NBT),

    # Loot table for an unopened container.
    VarInt(66): ComponentDataStruct(name='container_loot', tid=66, data_struct=NBT),
}


@dataclass(slots=True)
class SlotDisplay(Combined):

    EMPTY: ClassVar[int] = 0
    ANY_FUEL: ClassVar[int] = 1
    ITEM: ClassVar[int] = 2
    ITEM_STACK: ClassVar[int] = 3
    TAG: ClassVar[int] = 4
    SMITHING_TRIM: ClassVar[int] = 5
    WITH_REMAINDER: ClassVar[int] = 6
    COMPOSITE: ClassVar[int] = 7

    slot_display_type: Field | VarInt
    data: Field | tuple


    def __bytes__(self) -> bytes:
        bs = self.slot_display_type.bytes
        for _ in self.data:
            bs += _.bytes
        return bs

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        slot_display_type = VarInt.decode(bytes_io)
        if slot_display_type.value in [cls.EMPTY, cls.ANY_FUEL]:
            return cls(slot_display_type=slot_display_type, data=())

        elif slot_display_type.value == cls.ITEM:
            return cls(slot_display_type=slot_display_type, data=(VarInt.decode(bytes_io),))

        elif slot_display_type.value == cls.ITEM_STACK:
            return cls(slot_display_type=slot_display_type, data=(Slot.decode(bytes_io),))

        elif slot_display_type.value == cls.TAG:
            return cls(slot_display_type=slot_display_type, data=(Identifier.decode(bytes_io),))

        elif slot_display_type.value == cls.SMITHING_TRIM:
            return cls(
                slot_display_type=slot_display_type,
                data=(
                    cls.decode(bytes_io), cls.decode(bytes_io), cls.decode(bytes_io)
                )
            )

        elif slot_display_type.value == cls.WITH_REMAINDER:
            return cls(
                slot_display_type=slot_display_type,
                data=(cls.decode(bytes_io), cls.decode(bytes_io),)
            )

        elif slot_display_type.value == cls.COMPOSITE:
            array_length = VarInt.decode(bytes_io)
            data = []
            for _ in range(array_length.value):
                data.append(cls.decode(bytes_io))
            return cls(slot_display_type=slot_display_type, data=tuple(data))


@dataclass(slots=True)
class RecipeDisplay(Combined):
    """
        https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Recipes
    """

    CRAFTING_SHAPELESS: ClassVar[int] = 0
    CRAFTING_SHAPED: ClassVar[int] = 1
    FURNACE: ClassVar[int] = 2
    STONECUTTER: ClassVar[int] = 3
    SMITHING: ClassVar[int] = 4

    recipe_display_type: Field | VarInt
    data: Field | tuple

    def __bytes__(self) -> bytes:
        bs = self.recipe_display_type.bytes
        for _ in self.data:
            bs += _.bytes
        return bs

    @classmethod
    def decode(cls, bytes_io: IO, *args, **kwargs) -> Self:
        recipe_display_type = VarInt.decode(bytes_io)
        if recipe_display_type.value == RecipeDisplay.CRAFTING_SHAPELESS:
            array_length = VarInt.decode(bytes_io)
            data = [SlotDisplay.decode(bytes_io) for _ in range(array_length.value)]
            return cls(
                recipe_display_type,
                (
                    data,
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                )
            )
        elif recipe_display_type.value == RecipeDisplay.CRAFTING_SHAPED:
            width = VarInt.decode(bytes_io)
            height = VarInt.decode(bytes_io)
            array_length = VarInt.decode(bytes_io)
            return cls(
                recipe_display_type,
                (
                    width, height,
                    [SlotDisplay.decode(bytes_io) for _ in range(array_length.value)],
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                )
            )
        elif recipe_display_type.value == RecipeDisplay.FURNACE:
            return cls(
                recipe_display_type,
                (
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                    VarInt.decode(bytes_io),
                    Float.decode(bytes_io),
                )
            )
        elif recipe_display_type.value == RecipeDisplay.STONECUTTER:
            return cls(
                recipe_display_type,
                (
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                )
            )
        elif recipe_display_type.value == RecipeDisplay.SMITHING:
            return cls(
                recipe_display_type,
                (
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                    SlotDisplay.decode(bytes_io),
                )
            )
