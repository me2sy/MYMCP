# -*- coding: utf-8 -*-
"""
    play
    ~~~~~~~~~~~~~~~~~~

    Log:
         2025-02-08 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.0'

__all__ = [
    'PlayProtocols'
]

import datetime
import random
from collections import OrderedDict
from typing import IO, Any

from mymcp.data_type import *
from mymcp.protocols import ProtocolEnum, Field, FieldsArray, Packet, DataPacket


class PacketPlay(Packet):
    STATUS = ProtocolEnum.Status.PLAY


class PlayProtocols:

    class Server2Client:

        class SCPlayBundleDelimiter(PacketPlay):
            """
                The delimiter for a bundle of packets.
                When received, the client should store every subsequent packet it receives,
                and wait until another delimiter is received.
                Once that happens, the client is guaranteed to process every packet in the bundle on the same tick,
                and the client should stop storing packets.
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = []

        class SCPlaySpawnEntity(PacketPlay):
            """
                Sent by the server when an entity (aside from Experience Orb) is created.
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('entity_uuid', UUID),

                # ID in the minecraft:entity_type registry (see "type" field in Entity metadata#Entities).
                # https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Entity_metadata#Entities
                Field('_type', VarInt),
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),

                # To get the real pitch, you must divide this by (256.0F / 360.0F)
                Field('pitch', Angle),

                # To get the real yaw, you must divide this by (256.0F / 360.0F)
                Field('yaw', Angle),

                # Only used by living entities, where the head of the entity may differ from the general body rotation.
                Field('head_yaw', Angle),

                # Meaning dependent on the value of the Type field, see Object Data for details.
                # https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Object_Data
                Field('data', VarInt),

                Field('velocity_x', Short),
                Field('velocity_y', Short),
                Field('velocity_z', Short)
            ]

        class SCPlaySpawnExperienceOrb(PacketPlay):
            """
                Spawns one or more experience orbs.
            """
            PACKET_ID_HEX = 0x02
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('count', Short),
            ]

        class SCPlayEntityAnimation(PacketPlay):
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
            PACKET_ID_HEX = 0x03
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('animation', UnsignedByte)
            ]

        class SCPlayAwardStatistics(PacketPlay):
            """
                Sent as a response to Client Status (id 1).
                Will only send the changed values if previously requested.
            """
            PACKET_ID_HEX = 0x04
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('count', VarInt),
                FieldsArray(
                    'statistic',
                    [
                        Field('category_id', VarInt),
                        Field('statistic_id', VarInt),
                        Field('value', VarInt),
                    ],
                    'count'
                )
            ]

        class SCPlayAcknowledgeBlockChange(PacketPlay):
            """
                Acknowledges a user-initiated block change.
                After receiving this packet,
                the client will display the block state sent by the server instead of the one predicted by the client.
            """
            PACKET_ID_HEX = 0x05
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('sequence_id', VarInt),
            ]

        class SCPlaySetBlockDestroyStage(PacketPlay):
            """
                0–9 are the displayable destroy stages and each other number means that
                there is no animation on this coordinate.
            """
            PACKET_ID_HEX = 0x06
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('location', Position),

                # 0–9 to set it, any other value to remove it.
                Field('destroy_stage', Byte),
            ]

        class SCPlayBlockEntityData(PacketPlay):
            """
                Sets the block entity associated with the block at the given location.
            """
            PACKET_ID_HEX = 0x07
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('location', Position),
                Field('_type', VarInt),
                Field('nbt_data', NBT),
            ]

        class SCPlayBlockAction(PacketPlay):
            """
                This packet is used for a number of actions and animations performed by blocks,
                usually non-persistent.
                The client ignores the provided block type and instead uses the block state in their world.
            """
            PACKET_ID_HEX = 0x08
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('location', Position),
                Field('action_id', UnsignedByte),
                Field('action_parameter', UnsignedByte),
                Field('block_type', VarInt),
            ]

        class SCPlayBlockUpdate(PacketPlay):
            """
                Fired whenever a block is changed within the render distance.
            """
            PACKET_ID_HEX = 0x09
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('location', Position),
                Field('block_id', VarInt),
            ]

        class SCPlayBossBar(PacketPlay):
            """
                Boss Bar
            """
            PACKET_ID_HEX = 0x0A
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['uuid'] = UUID.decode(bytes_io)
                result['action'] = VarInt.decode(bytes_io)

                if result['action'] == ProtocolEnum.BossBarAction.ADD.value:
                    result['title'] = TextComponent.decode(bytes_io)
                    result['health'] = Float.decode(bytes_io)
                    result['color'] = VarInt.decode(bytes_io)
                    result['division'] = VarInt.decode(bytes_io)
                    result['flags'] = UnsignedByte.decode(bytes_io)

                elif result['action'] == ProtocolEnum.BossBarAction.REMOVE.value:
                    ...

                elif result['action'] == ProtocolEnum.BossBarAction.UPDATE_HEALTH.value:
                    result['health'] = Float.decode(bytes_io)

                elif result['action'] == ProtocolEnum.BossBarAction.UPDATE_TITLE.value:
                    result['title'] = TextComponent.decode(bytes_io)

                elif result['action'] == ProtocolEnum.BossBarAction.UPDATE_STYLE.value:
                    result['color'] = VarInt.decode(bytes_io)
                    result['dividers'] = VarInt.decode(bytes_io)

                elif result['action'] == ProtocolEnum.BossBarAction.UPDATE_FLAGS.value:
                    result['flags'] = UnsignedByte.decode(bytes_io)

                return result

        class SCPlayChangeDifficulty(PacketPlay):
            """
                Changes the difficulty setting in the client's option menu
            """
            PACKET_ID_HEX = 0x0B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # 0: peaceful, 1: easy, 2: normal, 3: hard.
                Field('difficulty', UnsignedByte),
                Field('difficulty_locked', Boolean)
            ]

        class SCPlayChunkBatchFinished(PacketPlay):
            """
                Marks the end of a chunk batch.
            """
            PACKET_ID_HEX = 0x0C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('batch_size', VarInt)
            ]

        class SCPlayChunkBatchStart(PacketPlay):
            """
                Marks the start of a chunk batch.
                The Notchian client marks and stores the time it receives this packet.
            """
            PACKET_ID_HEX = 0x0D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = []

        class SCPlayChunkBiomes(PacketPlay):
            """
                Chunk Biomes
                The order of X and Z is inverted, because the client reads them as one big-endian Long,
                with Z being the upper 32 bits.
            """
            PACKET_ID_HEX = 0x0E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('number_of_chunks', VarInt),
                FieldsArray(
                    'chunk_biome_data',
                    [
                        Field('chunk_z', Int),
                        Field('chunk_x', Int),
                        Field('size', VarInt),
                        FieldsArray(
                            'data',
                            [
                                Field('data_byte', Byte)
                            ],
                            'size'
                        )
                    ],
                    'number_of_chunks'
                )
            ]

        class SCPlayClearTitles(PacketPlay):
            """
                Clear the client's current title information, with the option to also reset it.
            """
            PACKET_ID_HEX = 0x0F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('reset', Boolean),
            ]

        class SCPlayCommandSuggestionsResponse(PacketPlay):
            """
                The server responds with a list of auto-completions of the last word sent to it.
                In the case of regular chat, this is a player username.
                Command names and parameters are also supported.
                The client sorts these alphabetically before listing them.
            """
            PACKET_ID_HEX = 0x10
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('_id', VarInt),
                Field('start', VarInt),
                Field('length', VarInt),
                Field('count', VarInt),
                FieldsArray(
                    'matches',
                    [
                        Field('match', String),
                        Field('has_tooltip', Boolean),
                        Field('tooltip', TextComponent, optional_field_name='has_tooltip'),
                    ],
                    'count'
                )
            ]

        class SCPlayCommands(PacketPlay):
            """
                Lists all of the commands on the server, and how they are parsed.
                This is a directed graph, with one root node.
                Each redirect or child node must refer only to nodes that have already been declared.
                # TODO Node Not Finished!
            """
            PACKET_ID_HEX = 0x11
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('count', VarInt),
                FieldsArray(
                    'nodes',
                    [
                        Field('node', Node)
                    ],
                    'count'
                ),
                # Index of the root node in the previous array.
                Field('root_index', VarInt)
            ]

        class SCPlayCloseContainer(PacketPlay):
            """
                This packet is sent from the server to the client when a window is forcibly closed,
                such as when a chest is destroyed while it's open.
                The Notchian client disregards the provided window ID and closes any active window.
            """
            PACKET_ID_HEX = 0x12
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('window_id', UnsignedByte)
            ]

        class SCPlaySetContainerContent(PacketPlay):
            """
                Replaces the contents of a container window.
                Sent by the server upon initialization of a container window or the player's inventory,
                and in response to state ID mismatches (see #Click Container).
            """
            PACKET_ID_HEX = 0x13
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('window_id', UnsignedByte),
                Field('state_id', VarInt),
                Field('count', VarInt),
                FieldsArray(
                    'slot_data',
                    [
                        Field('slot', Slot)
                    ],
                    'count'
                ),
                Field('carried_item', Slot)
            ]

        class SCPlaySetContainerProperty(PacketPlay):
            """
                This packet is used to inform the client that part of a GUI window should be updated.
            """
            PACKET_ID_HEX = 0x14
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('window_id', UnsignedByte),
                Field('property', Short),
                Field('value', Short),
            ]

        class SCPlaySetContainerSlot(PacketPlay):
            """
                Sent by the server when an item in a slot (in a window) is added/removed.
            """
            PACKET_ID_HEX = 0x15
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('window_id', Byte),
                Field('state_id', VarInt),
                Field('slot', Short),
                Field('slot_data', Slot)
            ]

        class SCPlayCookieRequest(PacketPlay):
            """
                Requests a cookie that was previously stored.
            """
            PACKET_ID_HEX = 0x16
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('key', Identifier)
            ]

        class SCPlaySetCooldown(PacketPlay):
            """
                Applies a cooldown period to all items with the given type.
            """
            PACKET_ID_HEX = 0x17
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('item_id', VarInt),
                Field('cooldown_ticks', VarInt),
            ]

        class SCPlayChatSuggestions(PacketPlay):
            """
                Unused by the Notchian server.
                Likely provided for custom servers to send chat message completions to clients.
            """
            PACKET_ID_HEX = 0x18
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # 0: Add, 1: Remove, 2: Set
                Field('action', VarInt),
                Field('count', VarInt),
                FieldsArray(
                    'entries',
                    [
                        Field('entry', String),
                    ],
                    'count'
                )
            ]

        class SCPlayClientboundPluginMessage(PacketPlay):
            """
                Mods and plugins can use this to send their data.
            """
            PACKET_ID_HEX = 0x19
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['channel'] = Identifier.decode(bytes_io)
                result['data'] = bytes_io.read()

                return result

        class SCPlayDamageEvent(PacketPlay):
            """
                Damage Event
            """
            PACKET_ID_HEX = 0x1A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('source_type_id', VarInt),
                Field('source_cause_id', VarInt),
                Field('source_direct_id', VarInt),
                Field('has_source_position', Boolean),
                Field('source_position_x', Double, optional_field_name='has_source_position'),
                Field('source_position_y', Double, optional_field_name='has_source_position'),
                Field('source_position_z', Double, optional_field_name='has_source_position')
            ]

        class SCPlayDebugSample(PacketPlay):
            """
                Sample data that is sent periodically after the client has subscribed with Debug Sample Subscription.
            """
            PACKET_ID_HEX = 0x1B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('sample_length', VarInt),
                FieldsArray(
                    'samples',
                    [
                        Field('sample', Long)
                    ],
                    'sample_length'
                ),
                Field('sample_type', VarInt),
            ]

        class SCPlayDeleteMessage(PacketPlay):
            """
                Removes a message from the client's chat.
                This only works for messages with signatures, system messages cannot be deleted with this packet.
            """
            PACKET_ID_HEX = 0x1C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('message_id', VarInt),
                FieldsArray(
                    'signature',
                    [
                        Field('signature_byte', Byte),
                    ],
                    256,
                    optional_field_name='message_id',
                    optional_condition=lambda x: x == 0
                )
            ]

        class SCPlayDisconnect(PacketPlay):
            """
                Sent by the server before it disconnects a client.
                The client assumes that the server has already closed the connection by the time the packet arrives.
            """
            PACKET_ID_HEX = 0x1D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('reason', TextComponent)
            ]

        class SCPlayDisguisedChatMessage(PacketPlay):
            """
                Sends the client a chat message, but without any message signing information.
            """
            PACKET_ID_HEX = 0x1E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('message', TextComponent),
                Field('chat_type', VarInt),
                Field('sender_name', TextComponent),
                Field('has_target_name', Boolean),
                Field('target_name', TextComponent, optional_field_name='has_target_name'),
            ]

        class SCPlayEntityEvent(PacketPlay):
            """
                Entity statuses generally trigger an animation for an entity.
                The available statuses vary by the entity's type (and are available to subclasses of that type as well).
            """
            PACKET_ID_HEX = 0x1F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', Int),

                # See https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Entity_statuses
                # for a list of which statuses are valid for each type of entity.
                Field('entity_status', Byte),
            ]

        class SCPlayTeleportEntity(PacketPlay):
            """
                This packet is sent by the server when an entity moves more than 8 blocks.
            """
            PACKET_ID_HEX = 0x20
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('velocity_x', Double),
                Field('velocity_y', Double),
                Field('velocity_z', Double),

                # Rotation on the X axis, in degrees.
                Field('yam', Float),

                # Rotation on the Y axis, in degrees.
                Field('pitch', Float),

                Field('on_ground', Boolean),
            ]

        class SCPlayExplosion(PacketPlay):
            """
                Sent when an explosion occurs (creepers, TNT, and ghast fireballs).
            """
            PACKET_ID_HEX = 0x21
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('has_player_motion', Boolean),
                Field('player_motion_x', Double, optional_field_name='has_player_motion'),
                Field('player_motion_y', Double, optional_field_name='has_player_motion'),
                Field('player_motion_z', Double, optional_field_name='has_player_motion'),
                Field('explosion_particle', Particle),
                Field('explosion_sound', Slot.IDOrSoundEvent)
            ]

        class SCPlayUnloadChunk(PacketPlay):
            """
                Tells the client to unload a chunk column.
            """
            PACKET_ID_HEX = 0x22
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # Block coordinate divided by 16, rounded down.
                Field('chunk_z', Int),

                # Block coordinate divided by 16, rounded down.
                Field('chunk_x', Int),
            ]

        class SCPlayGameEvent(PacketPlay):
            """
                Used for a wide variety of game events, from weather to bed use to game mode to demo messages.
            """
            PACKET_ID_HEX = 0x23
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('event', UnsignedByte),
                Field('value', Float),
            ]

        class SCPlayOpenHorseScreen(PacketPlay):
            """
                This packet is used exclusively for opening the horse GUI.
                Open Screen is used for all other GUIs.
                The client will not open the inventory if the Entity ID does not point to an horse-like animal.
            """
            PACKET_ID_HEX = 0x24
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('window_id', VarInt),
                Field('slot_count', VarInt),
                Field('entity_id', Int),
            ]

        class SCPlayHurtAnimation(PacketPlay):
            """
                Plays a bobbing animation for the entity receiving damage.
            """
            PACKET_ID_HEX = 0x25
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),

                # The direction the damage is coming from in relation to the entity
                Field('yaw', Float)
            ]

        class SCPlayInitializeWorldBorder(PacketPlay):
            """
                Initial world border.
            """
            PACKET_ID_HEX = 0x26
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('x', Double),
                Field('z', Double),
                Field('old_diameter', Double),
                Field('new_diameter', Double),
                Field('speed', VarLong),
                Field('portal_teleport_boundary', VarInt),
                Field('warning_blocks', VarInt),
                Field('warning_time', VarInt)
            ]

        class SCPlayClientboundKeepAlive(PacketPlay):
            """
                The server will frequently send out a keep-alive, each containing a random ID.
                The client must respond with the same payload (see Serverbound Keep Alive).
                If the client does not respond to a Keep Alive packet within 15 seconds after it was sent,
                the server kicks the client.
                Vice versa, if the server does not send any keep-alives for 20 seconds,
                the client will disconnect and yields a "Timed out" exception.
                The Notchian server uses a system-dependent time in milliseconds to generate the keep alive ID value.
            """
            PACKET_ID_HEX = 0x27
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('keep_alive_id', Long),
            ]

        class SCPlayChunkDataAndUpdateLight(PacketPlay):
            """
                Sent when a chunk comes into the client's view distance,
                specifying its terrain, lighting and block entities.
            """
            PACKET_ID_HEX = 0x28
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('chunk_x', Int),
                Field('chunk_z', Int),
                Field('data', ChunkData),
                Field('light', LightData)
            ]

        class SCPlayWorldEvent(PacketPlay):
            """
                Sent when a client is to play a sound or particle effect.
            """
            PACKET_ID_HEX = 0x29
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('event', Int),
                Field('location', Position),
                Field('data', Int),
                Field('disable_relative_volume', Boolean),
            ]

        class SCPlayParticle(PacketPlay):
            """
                Displays the named particle
            """
            PACKET_ID_HEX = 0x2A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('long_distance', Boolean),
                Field('always_visible', Boolean),
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('offset_x', Float),
                Field('offset_y', Float),
                Field('offset_z', Float),
                Field('max_speed', Float),
                Field('particle_count', Int),
                Field('particle', Particle)
            ]

        class SCPlayUpdateLight(PacketPlay):
            """
                Updates light levels for a chunk. See Light for information on how lighting works in Minecraft.
                https://minecraft.wiki/w/Light
            """
            PACKET_ID_HEX = 0x2B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('chunk_x', VarInt),
                Field('chunk_z', VarInt),
                Field('data', LightData)
            ]

        class SCPlayLogin(PacketPlay):
            """
                Player Login
            """
            PACKET_ID_HEX = 0x2C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', Int),
                Field('is_hardcore', Boolean),
                Field('dimension_count', VarInt),
                FieldsArray(
                    'dimension_names',
                    [
                        Field('dimension_name', Identifier),
                    ],
                    'dimension_count'
                ),
                Field('max_players', VarInt),
                Field('view_distance', VarInt),
                Field('simulation_distance', VarInt),
                Field('reduced_debug_info', Boolean),
                Field('enable_respawn_screen', Boolean),
                Field('do_limited_crafting', Boolean),
                Field('dimension_type', VarInt),
                Field('dimension_name', Identifier),
                Field('hashed_seed', Long),

                # 0: Survival, 1: Creative, 2: Adventure, 3: Spectator.
                Field('game_mode', UnsignedByte),

                # -1: Undefined (null), 0: Survival, 1: Creative, 2: Adventure, 3: Spectator.
                # The previous game mode. Vanilla client uses this for the debug (F3 + N & F3 + F4) game mode switch.
                # (More information needed)
                Field('previous_game_mode', Byte),
                Field('is_debug', Boolean),
                Field('is_flat', Boolean),

                Field('has_death_location', Boolean),
                Field('death_dimension_name', Identifier, optional_field_name='has_death_location'),
                Field('death_location', Position, optional_field_name='has_death_location'),

                Field('portal_cooldown', VarInt),
                Field('sea_level', VarInt),
                Field('enforces_secure_chat', Boolean)
            ]

        class SCPlayMapData(PacketPlay):
            """
                Updates a rectangular area on a map item.
            """
            PACKET_ID_HEX = 0x2D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('map_id', VarInt),
                Field('scale', Byte),
                Field('locked', Boolean),
                Field('has_icons', Boolean),
                Field('icon_count', VarInt, optional_field_name='has_icons'),
                FieldsArray(
                    'icons',
                    [
                        Field('_type', VarInt),
                        Field('x', Byte),
                        Field('z', Byte),
                        Field('direction', Byte),
                        Field('has_display_name', Boolean),
                        Field('display_name', TextComponent, optional_field_name='has_display_name'),
                    ],
                    'icon_count',
                    optional_field_name='has_icons'
                ),
                Field('columns', UnsignedByte),
                Field('rows', UnsignedByte, optional_field_name='columns', optional_condition=lambda x: x > 0),
                Field('color_patch_x', UnsignedByte, optional_field_name='columns', optional_condition=lambda x: x > 0),
                Field('color_patch_z', UnsignedByte, optional_field_name='columns', optional_condition=lambda x: x > 0),
                Field('length', VarInt, optional_field_name='columns', optional_condition=lambda x: x > 0),
                FieldsArray(
                    'data',
                    [
                        Field('data_byte', UnsignedByte),
                    ],
                    'length',
                    optional_field_name='columns',
                    optional_condition=lambda x: x > 0
                )
            ]

        class SCPlayMerchantOffers(PacketPlay):
            """
                The list of trades a villager NPC is offering.
                TODO Not Finished YET
            """
            PACKET_ID_HEX = 0x2E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = []

        class SCPlayUpdateEntityPosition(PacketPlay):
            """
                This packet is sent by the server when an entity moves a small distance.
                The change in position is represented as a fixed-point number with 12 fraction bits and 4 integer bits.
                As such, the maximum movement distance along each axis is 8 blocks in the negative direction,
                or 7.999755859375 blocks in the positive direction.
                If the movement exceeds these limits, Teleport Entity should be sent instead.
            """
            PACKET_ID_HEX = 0x2F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('delta_x', Short),
                Field('delta_y', Short),
                Field('delta_z', Short),
                Field('on_ground', Boolean)
            ]

        class SCPlayUpdateEntityPositionAndRotation(PacketPlay):
            """
                This packet is sent by the server when an entity rotates and moves.
                See #Update Entity Position for how the position is encoded.
                https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Protocol#Update_Entity_Position
            """
            PACKET_ID_HEX = 0x30
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('delta_x', Short),
                Field('delta_y', Short),
                Field('delta_z', Short),
                Field('yaw', Angle),
                Field('pitch', Angle),
                Field('on_ground', Boolean)
            ]

        class SCPlayMoveMinecraftAlongTrack(PacketPlay):
            """
                Move Minecraft Along Track.
            """
            PACKET_ID_HEX = 0x31
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('step_count', VarInt),
                FieldsArray(
                    'steps',
                    [
                        Field('x', Double),
                        Field('y', Double),
                        Field('z', Double),
                        Field('velocity_x', Double),
                        Field('velocity_y', Double),
                        Field('velocity_z', Double),
                        Field('yaw', Angle),
                        Field('pitch', Angle),
                        Field('weight', Float),
                    ],
                    'step_count',
                )
            ]

        class SCPlayUpdateEntityRotation(PacketPlay):
            """
                This packet is sent by the server when an entity rotates.
            """
            PACKET_ID_HEX = 0x32
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('yaw', Angle),
                Field('pitch', Angle),
                Field('on_ground', Boolean)
            ]

        class SCPlayMoveVehicle(PacketPlay):
            """
                Note that all fields use absolute positioning and do not allow for relative positioning.
            """
            PACKET_ID_HEX = 0x33
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('yaw', Float),
                Field('pitch', Float),
            ]

        class SCPlayOpenBook(PacketPlay):
            """
                Sent when a player right clicks with a signed book. This tells the client to open the book GUI.
            """
            PACKET_ID_HEX = 0x34
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # 0: Main hand, 1: Off hand.
                Field('hand', VarInt),
            ]

        class SCPlayOpenScreen(PacketPlay):
            """
                This is sent to the client when it should open an inventory,
                such as a chest, workbench, furnace, or other container.
                Resending this packet with already existing window id,
                will update the window title and window type without closing the window.
            """
            PACKET_ID_HEX = 0x35
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('window_id', VarInt),
                Field('window_type', VarInt),
                Field('window_title', TextComponent),
            ]

        class SCPlayOpenSignEditor(PacketPlay):
            """
                Sent when the client has placed a sign and is allowed to send Update Sign.
                There must already be a sign at the given location (which the client does not do automatically) -
                send a Block Update first.
            """
            PACKET_ID_HEX = 0x36
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('location', Position),
                Field('is_front_text', Boolean),
            ]

        class SCPlayPing(PacketPlay):
            """
                Packet is not used by the Notchian server. When sent to the client,
                client responds with a Pong packet with the same id.
            """
            PACKET_ID_HEX = 0x37
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('_id', VarInt),
            ]

        class SCPlayPingResponse(PacketPlay):
            """
                Ping Response.
            """
            PACKET_ID_HEX = 0x38
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('payload', Long)
            ]

        class SCPlayPlaceGhostRecipe(PacketPlay):
            """
                Response to the serverbound packet (Place Recipe), with the same recipe ID.
                Appears to be used to notify the UI.
            """
            PACKET_ID_HEX = 0x39
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('window_id', VarInt),
                Field('recipe_display', RecipeDisplay),
            ]

        class SCPlayPlayerAbilities(PacketPlay):
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
            PACKET_ID_HEX = 0x3A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('flags', Byte),
                Field('flying_speed', Float),
                Field('field_of_view_modifier', Float),
            ]

        class SCPlayPlayerChatMessage(PacketPlay):
            """
                Sends the client a chat message from a player
            """
            PACKET_ID_HEX = 0x3B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('sender', UUID),
                Field('index', VarInt),
                Field('message_signature_present', Boolean),
                FieldsArray('message_signature_bytes', [Field('bytes', Byte)], 256, 'message_signature_present'),
                Field('message', String),
                Field('timestamp', Long),
                Field('salt', Long),
                Field('total_previous_messages', VarInt),
                FieldsArray('p_message', [
                    Field('message_id', VarInt),
                    FieldsArray('pm_signature', [Field('bytes', Byte)], 256, 'message_signature_present'),
                ], 'total_previous_messages'),
                Field('unsigned_content_present', Boolean),
                Field('unsigned_content', TextComponent, optional_field_name='unsigned_content_present'),
                Field('filter_type', VarInt),
                Field(
                    'filter_type_bites', BitSet, optional_field_name='filter_type', optional_condition=lambda x: x == 2
                ),
                Field('chat_type', VarInt),
                Field('sender_name', TextComponent),
                Field('has_target_name', Boolean),
                Field('target_name', TextComponent, optional_field_name='has_target_name')
            ]

        class SCPlayEndCombat(PacketPlay):
            """
                Unused by the Notchian client.
                This data was once used for twitch.tv metadata circa 1.8.
            """
            PACKET_ID_HEX = 0x3C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('duration', VarInt)
            ]

        class SCPlayEnterCombat(PacketPlay):
            """
                Unused by the Notchian client. This data was once used for twitch.tv metadata circa 1.8.
            """
            PACKET_ID_HEX = 0x3D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = []

        class SCPlayCombatDeath(PacketPlay):
            """
                Used to send a respawn screen.
            """
            PACKET_ID_HEX = 0x3E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('player_id', VarInt),
                Field('message', TextComponent),
            ]

        class SCPlayPlayerInfoRemove(PacketPlay):
            """
                Used by the server to remove players from the player list.
            """
            PACKET_ID_HEX = 0x3F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('number_of_players', VarInt),
                FieldsArray(
                    'players',
                    [
                        Field('player_id', UUID),
                    ],
                    'number_of_players'
                )
            ]

        class SCPlayPlayerInfoUpdate(PacketPlay):
            """
                Sent by the server to update the user list (<tab> in the client).
            """
            PACKET_ID_HEX = 0x40
            DIRECT = ProtocolEnum.Direction.SC

            MASK_ADD_PLAYER = 0x01
            MASK_INITIALIZE_CHAT = 0x02
            MASK_UPDATE_GAME_MODE = 0x04
            MASK_UPDATE_LISTED = 0x08
            MASK_UPDATE_LATENCY = 0x10
            MASK_UPDATE_DISPLAY_NAME = 0x20
            MASK_UPDATE_LIST_PRIORITY = 0x40
            MASK_UPDATE_HAT = 0x80

            @classmethod
            def decode(cls, bytes_io: IO) -> list:

                res = []

                action = Byte.decode(bytes_io)

                number_of_players = VarInt.decode(bytes_io)

                for i in range(number_of_players):

                    player_actions = {
                        'uuid': UUID.decode(bytes_io)
                    }

                    if action & cls.MASK_ADD_PLAYER > 0:
                        player_actions[cls.MASK_ADD_PLAYER] = {
                            'name': String.decode(bytes_io),
                            'property': []
                        }
                        nop = VarInt.decode(bytes_io)
                        for _ in range(nop):
                            _name = String.decode(bytes_io)
                            _value = String.decode(bytes_io)
                            _is_signed = Boolean.decode(bytes_io)
                            if _is_signed:
                                _signature = String.decode(bytes_io)
                            else:
                                _signature = ''

                            player_actions[cls.MASK_ADD_PLAYER]['property'].append({
                                'name': _name,
                                'value': _value,
                                'is_signed': _is_signed,
                                'signature': _signature
                            })

                    if action & cls.MASK_INITIALIZE_CHAT > 0:
                        has_signature_data = Boolean.decode(bytes_io)
                        player_actions[cls.MASK_INITIALIZE_CHAT] = {
                            'has_signature_data': has_signature_data
                        }
                        if has_signature_data:
                            chat_session_id = UUID.decode(bytes_io)
                            public_key_expiry_time = Long.decode(bytes_io)
                            encoded_public_key_size = VarInt.decode(bytes_io)
                            encoded_public_key = bytes()
                            for _ in range(encoded_public_key_size):
                                encoded_public_key += Byte.decode(bytes_io).to_bytes()

                            public_key_signature_size = VarInt.decode(bytes_io)
                            public_key_signature = bytes()
                            for _ in range(public_key_signature_size):
                                public_key_signature += Byte.decode(bytes_io).to_bytes()

                            player_actions[cls.MASK_INITIALIZE_CHAT]['signature_data'] = {
                                'chat_session_id': chat_session_id,
                                'public_key_expiry_time': public_key_expiry_time,
                                'encoded_public_key_size': encoded_public_key_size,
                                'encoded_public_key': encoded_public_key,
                                'public_key_signature': public_key_signature,
                                'public_key_signature_data': public_key_signature
                            }

                    if action & cls.MASK_UPDATE_GAME_MODE > 0:
                        player_actions[cls.MASK_UPDATE_GAME_MODE] = {
                            'game_mode': VarInt.decode(bytes_io)
                        }

                    if action & cls.MASK_UPDATE_LISTED > 0:
                        player_actions[cls.MASK_UPDATE_LISTED] = {
                            'listed': Boolean.decode(bytes_io)
                        }

                    if action & cls.MASK_UPDATE_LATENCY > 0:
                        player_actions[cls.MASK_UPDATE_LATENCY] = {
                            'ping': VarInt.decode(bytes_io)
                        }

                    if action & cls.MASK_UPDATE_DISPLAY_NAME > 0:
                        has_display_name = Boolean.decode(bytes_io)
                        if has_display_name:
                            player_actions[cls.MASK_UPDATE_DISPLAY_NAME] = {
                                'display_name': TextComponent.decode(bytes_io)
                            }

                    if action & cls.MASK_UPDATE_LIST_PRIORITY > 0:
                        player_actions[cls.MASK_UPDATE_LIST_PRIORITY] = {
                            'priority': VarInt.decode(bytes_io)
                        }

                    if action & cls.MASK_UPDATE_HAT > 0:
                        player_actions[cls.MASK_UPDATE_HAT] = {
                            'hat_visible': Boolean.decode(bytes_io)
                        }

                    res.append(player_actions)

                return res

        class SCPlayLookAt(PacketPlay):
            """
                Used to rotate the client player to face the given location or entity
                (for /teleport [<targets>] <x> <y> <z> facing).
            """
            PACKET_ID_HEX = 0x41
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # Values are feet=0, eyes=1.
                # If set to eyes, aims using the head position; otherwise aims using the feet position.
                Field('feet_or_eyes', VarInt),

                Field('target_x', Double),
                Field('target_y', Double),
                Field('target_z', Double),
                Field('is_entity', Boolean),
                Field('entity_id', VarInt, optional_field_name='is_entity'),
                Field('entity_feel_or_eyes', VarInt, optional_field_name='is_entity'),
            ]

        class SCPlaySynchronizePlayerPosition(PacketPlay):
            """
                Teleports the client, e.g. during login, when using an ender pearl,
                in response to invalid move packets, etc.
                Due to latency, the server may receive outdated movement packets sent
                before the client was aware of the teleport.
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
            PACKET_ID_HEX = 0x42
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('teleport_id', VarInt),
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('velocity_x', Double),
                Field('velocity_y', Double),
                Field('velocity_z', Double),
                Field('yaw', Float),
                Field('pitch', Float),
                Field('flags', Int)
            ]

        class SCPlayPlayerRotation(PacketPlay):
            """
                Player Rotation
            """
            PACKET_ID_HEX = 0x43
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # Rotation on the X axis, in degrees.
                Field('yaw', Float),

                # Rotation on the Y axis, in degrees.
                Field('pitch', Float),
            ]

        class SCPlayRecipeBookAdd(PacketPlay):
            """
                Recipe Book Add.
            """
            PACKET_ID_HEX = 0x44
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('recipe_count', VarInt),
                FieldsArray(
                    'recipes',
                    [
                        Field('recipe_id', VarInt),
                        Field('display', RecipeDisplay),
                        Field('group_id', VarInt),
                        Field('category_id', VarInt),
                        Field('has_ingredients', Boolean),
                        Field('ingredient_count', VarInt, optional_field_name='has_ingredients'),
                        FieldsArray(
                            'ingredients',
                            [
                                Field('ingredient_id', IDSet),
                            ],
                            'ingredient_count',
                            optional_field_name='has_ingredients'
                        ),

                        # 0x01: show notification; 0x02: highlight as new
                        Field('flags', Byte)
                    ],
                    'recipe_count'
                ),
                Field('replace', Boolean)
            ]

        class SCPlayRecipeBookRemove(PacketPlay):
            """
                Recipe Book Remove.
            """
            PACKET_ID_HEX = 0x45
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('recipe_count', VarInt),
                FieldsArray(
                    'recipes',
                    [
                        Field('recipe_id', VarInt),
                    ],
                    'recipe_count',
                )
            ]

        class SCPlayRecipeBookSettings(PacketPlay):
            """
                Recipe Book Settings.
            """
            PACKET_ID_HEX = 0x46
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('crafting_recipe_book_open', Boolean),
                Field('crafting_recipe_book_filter_active', Boolean),
                Field('smelting_recipe_book_open', Boolean),
                Field('smelting_recipe_book_filter_active', Boolean),
                Field('blast_furnace_recipe_book_open', Boolean),
                Field('blast_furnace_recipe_book_filter_active', Boolean),
                Field('smoker_recipe_book_open', Boolean),
                Field('smoker_recipe_book_filter_active', Boolean),
            ]

        class SCPlayRemoveEntities(PacketPlay):
            """
                Sent by the server when an entity is to be destroyed on the client.
            """
            PACKET_ID_HEX = 0x47
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('count', VarInt),
                FieldsArray('entities', [Field('entity_id', VarInt)], 'count')
            ]

        class SCPlayRemoveEntityEffect(PacketPlay):
            """
                Remove Entity Effect.
            """
            PACKET_ID_HEX = 0x48
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),

                # Effect ID See
                # https://minecraft.wiki/w/Status_effect#Effect_list
                Field('effect_id', VarInt),
            ]

        class SCPlayResetScore(PacketPlay):
            """
                This is sent to the client when it should remove a scoreboard item.
            """
            PACKET_ID_HEX = 0x49
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_name', String),
                Field('has_objective_name', Boolean),
                Field('objective_name', String, optional_field_name='has_objective_name'),
            ]

        class SCPlayRemoveResourcePack(PacketPlay):
            """
                Remove Resource Pack.
            """
            PACKET_ID_HEX = 0x4A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('has_uuid', Boolean),
                Field('uuid', UUID, optional_field_name='has_uuid'),
            ]

        class SCPlayAddResourcePack(PacketPlay):
            """
                Add Resource Pack.
            """
            PACKET_ID_HEX = 0x4B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('uuid', UUID),
                Field('url', String),
                Field('hash', String),
                Field('forced', Boolean),
                Field('has_prompt_message', Boolean),
                Field('prompt_message', TextComponent, optional_field_name='has_prompt_message'),
            ]

        class SCPlayRespawn(PacketPlay):
            """
                To change the player's dimension (overworld/nether/end),
                send them a respawn packet with the appropriate dimension,
                followed by prechunks/chunks for the new dimension,
                and finally a position and look packet.
                You do not need to unload chunks, the client will do it automatically.
            """
            PACKET_ID_HEX = 0x4C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # The ID of type of dimension in the minecraft:dimension_type registry,
                # defined by the Registry Data packet.
                Field('dimension_type', VarInt),

                Field('dimension_name', Identifier),
                Field('hashed_seed', Long),

                # 0: Survival, 1: Creative, 2: Adventure, 3: Spectator.
                Field('game_mode', UnsignedByte),

                # -1: Undefined (null), 0: Survival, 1: Creative, 2: Adventure, 3: Spectator.
                # The previous game mode.
                # Vanilla client uses this for the debug (F3 + N & F3 + F4) game mode switch. (More information needed)
                Field('previous_game_mode', Byte),

                Field('is_debug', Boolean),
                Field('is_flat', Boolean),

                Field('has_death_location', Boolean),
                Field('death_dimension_name', Identifier, optional_field_name='has_death_location'),
                Field('death_location', Position, optional_field_name='has_death_location'),
                Field('portal_cooldown', VarInt),
                Field('sea_level', VarInt),

                # Bit mask. 0x01: Keep attributes, 0x02: Keep metadata.
                # Tells which data should be kept on the client side once the player has respawned.
                Field('flags', Byte)
            ]

        class SCPlaySetHeadRotation(PacketPlay):
            """
                Changes the direction an entity's head is facing.
                While sending the Entity Look packet changes the vertical rotation of the head,
                sending this packet appears to be necessary to rotate the head horizontally.
            """
            PACKET_ID_HEX = 0x4D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('head_yaw', Angle),
            ]

        class SCPlayUpdateSectionBlocks(PacketPlay):
            """
                Fired whenever 2 or more blocks are changed within the same chunk on the same tick.
            """
            PACKET_ID_HEX = 0x4E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('chunk_section_position', Long),
                Field('blocks_array_size', VarInt),
                FieldsArray('blocks', [
                    Field('block', VarLong)
                ], 'blocks_array_size')
            ]

        class SCPlaySelectAdvancementsTab(PacketPlay):
            """
                Sent by the server to indicate that the client should switch advancement tab.
                Sent either when the client switches tab in the GUI or when an advancement in another tab is made.
            """
            PACKET_ID_HEX = 0x4F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('has_id', Boolean),

                # The Identifier can be one of the following:
                # minecraft:story/root
                # minecraft:nether/root
                # minecraft:end/root
                # minecraft:adventure/root
                # minecraft:husbandry/root
                Field('identifier', Identifier, optional_field_name='has_id'),
            ]

        class SCPlayServerData(PacketPlay):
            """
                Server data.
            """
            PACKET_ID_HEX = 0x50
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('motd', TextComponent),
                Field('has_icon', Boolean),
                Field('size', VarInt, optional_field_name='has_icon'),
                FieldsArray(
                    'icon',
                    [
                        Field('icon_bytes', Byte)
                    ],
                    'size',
                    optional_field_name='has_icon',
                )
            ]

        class SCPlaySetActionBarText(PacketPlay):
            """
                Displays a message above the hotbar.
            """
            PACKET_ID_HEX = 0x51
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('action_bar_text', TextComponent),
            ]

        class SCPlaySetBorderCenter(PacketPlay):
            """
                Set Border Center.
            """
            PACKET_ID_HEX = 0x52
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('x', Double),
                Field('y', Double),
            ]

        class SCPlaySetBorderLerpSize(PacketPlay):
            """
                Set Border Lerp Size.
            """
            PACKET_ID_HEX = 0x53
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('old_diameter', Double),
                Field('new_diameter', Double),
                Field('speed', VarLong)
            ]

        class SCPlaySetBorderSize(PacketPlay):
            """
                Set Border Size.
            """
            PACKET_ID_HEX = 0x54
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('diameter', Double),
            ]

        class SCPlaySetBorderWarningDelay(PacketPlay):
            """
                Set Border Warning Delay.
            """
            PACKET_ID_HEX = 0x55
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('warning_time', VarInt),
            ]

        class SCPlaySetBorderWarningDistance(PacketPlay):
            """
                Set Border Warning Distance.
            """
            PACKET_ID_HEX = 0x56
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('warning_blocks', VarInt),
            ]

        class SCPlaySetCamera(PacketPlay):
            """
                Sets the entity that the player renders from.
            """
            PACKET_ID_HEX = 0x57
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('camera_id', VarInt),
            ]

        class SCPlaySetCenterChunk(PacketPlay):
            """
                Sets the center position of the client's chunk loading area.
            """
            PACKET_ID_HEX = 0x58
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('chunk_x', VarInt),
                Field('chunk_z', VarInt),
            ]

        class SCPlaySetRenderDistance(PacketPlay):
            """
                Sent by the integrated singleplayer server when changing render distance.
                This packet is sent by the server when the client reappears in the overworld after leaving the end.
            """
            PACKET_ID_HEX = 0x59
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('view_distance', VarInt),
            ]

        class SCPlaySetCursorItem(PacketPlay):
            """
                Replaces or sets the inventory item that's being dragged with the mouse.
            """
            PACKET_ID_HEX = 0x5A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('carried_item', Slot)
            ]

        class SCPlaySetDefaultSpawnPosition(PacketPlay):
            """
                Sent by the server after login to specify the coordinates of the spawn point
                 (the point at which players spawn at, and which the compass points to).
                 It can be sent at any time to update the point compasses point at.
            """
            PACKET_ID_HEX = 0x5B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('location', Position),
                Field('angle', Float),
            ]

        class SCPlayDisplayObjective(PacketPlay):
            """
                This is sent to the client when it should display a scoreboard.
            """
            PACKET_ID_HEX = 0x5C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # The position of the scoreboard.
                # 0: list, 1: sidebar, 2: below name, 3 - 18: team specific sidebar, indexed as 3 + team color.
                Field('position', VarInt),
                Field('score_name', String),
            ]

        class SCPlaySetEntityMetadata(PacketPlay):
            """
                Updates one or more metadata properties for an existing entity.
                Any properties not included in the Metadata field are left unchanged.
            """
            PACKET_ID_HEX = 0x5D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('metadata', EntityMetadata)
            ]

        class SCPlayLinkEntities(PacketPlay):
            """
                This packet is sent when an entity has been leashed to another entity.
            """
            PACKET_ID_HEX = 0x5E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('attached_entity_id', Int),
                Field('holding_entity_id', Int),
            ]

        class SCPlaySetEntityVelocity(PacketPlay):
            """
                Velocity is in units of 1/8000 of a block per server tick (50ms);
                for example, -1343 would move (-1343 / 8000) = −0.167875 blocks per tick (or −3.3575 blocks per second).
            """
            PACKET_ID_HEX = 0x5F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('velocity_x', Short),
                Field('velocity_y', Short),
                Field('velocity_z', Short)
            ]

        class SCPlaySetEquipment(PacketPlay):
            """
                Set Equipment
            """
            PACKET_ID_HEX = 0x60
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()

                result['entity_id'] = VarInt.decode(bytes_io)

                equipments = []

                while True:
                    slot = Byte.decode(bytes_io)
                    item = Slot.decode(bytes_io)
                    equipments.append({'slot': slot - 64 if slot >= 64 else slot, 'item': item})
                    if slot < 64:
                        break

                result['equipments'] = equipments

                return result

        class SCPlaySetExperience(PacketPlay):
            """
                Sent by the server when the client should change experience levels.
            """
            PACKET_ID_HEX = 0x61
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # Between 0 and 1
                Field('experience_bar', Float),
                Field('level', VarInt),

                # See Experience#Leveling up on the Minecraft Wiki for Total Experience to Level conversion.
                # https://minecraft.wiki/w/Experience#Leveling_up
                Field('total_experience', VarInt),
            ]

        class SCPlaySetHealth(PacketPlay):
            """
                Sent by the server to set the health of the player it is sent to.
                Food saturation acts as a food “overcharge”.
                Food values will not decrease while the saturation is over zero.
                New players logging in or respawning automatically get a saturation of 5.0.
                Eating food increases the saturation as well as the food bar.
            """
            PACKET_ID_HEX = 0x62
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # 0 or less = dead, 20 = full HP.
                Field('health', Float),

                # 0 - 20
                Field('food', VarInt),

                # Seems to vary from 0.0 to 5.0 in integer increments.
                Field('food_saturation', Float),
            ]

        class SCPlaySetHeldItem(PacketPlay):
            """
                Sent to change the player's slot selection.
            """
            PACKET_ID_HEX = 0x63
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # The slot which the player has selected (0–8).
                Field('slot', VarInt),
            ]

        class SCPlayUpdateObjectives(PacketPlay):
            """
                This is sent to the client when it should create a new scoreboard objective or remove one.
            """
            PACKET_ID_HEX = 0x64
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['objective_name'] = String.decode(bytes_io)
                result['mode'] = Byte.decode(bytes_io)

                _cond = (
                    ProtocolEnum.UpdateScoreAction.CREATE.value,
                    ProtocolEnum.UpdateScoreAction.UPDATE.value,
                )

                if result['mode'] in _cond:
                    result['objective_value'] = TextComponent.decode(bytes_io)
                    result['_type'] = VarInt.decode(bytes_io)
                    result['has_number_format'] = Boolean.decode(bytes_io)
                    if result['has_number_format']:
                        result['number_format'] = VarInt.decode(bytes_io)
                        if result['number_format'] == 1:
                            result['styling'] = NBT.decode(bytes_io)
                        elif result['number_format'] == 2:
                            result['content'] = TextComponent.decode(bytes_io)

                return result

        class SCPlaySetPassengers(PacketPlay):
            """
                Set Passengers
            """
            PACKET_ID_HEX = 0x65
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('passenger_count', Int),
                FieldsArray(
                    'passengers',
                    [
                        Field('passenger', VarInt)
                    ],
                    'passenger_count',
                )
            ]

        class SCPlaySetPlayerInventorySlot(PacketPlay):
            """
                Set Player's inventory slot.
            """
            PACKET_ID_HEX = 0x66
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('slot', VarInt),
                Field('slot_data', Slot)
            ]

        class SCPlayerUpdateTeams(PacketPlay):
            """
                Creates and updates teams.
            """
            PACKET_ID_HEX = 0x67
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['team_name'] = String.decode(bytes_io)
                result['method'] = Byte.decode(bytes_io)

                if result['method'] in (
                    ProtocolEnum.UpdateTeamsMethod.CREATE_TEAM.value,
                    ProtocolEnum.UpdateTeamsMethod.UPDATE_TEAM_INFO.value,
                ):
                    result['team_display_name'] = TextComponent.decode(bytes_io)
                    result['friendly_flags'] = Byte.decode(bytes_io)
                    result['name_tag_visibility'] = String.decode(bytes_io)
                    result['collision_rule'] = String.decode(bytes_io)
                    result['team_color'] = VarInt.decode(bytes_io)
                    result['team_prefix'] = TextComponent.decode(bytes_io)
                    result['team_suffix'] = TextComponent.decode(bytes_io)

                    if result['method'] == ProtocolEnum.UpdateTeamsMethod.CREATE_TEAM.value:
                        result['entity_count'] = VarInt.decode(bytes_io)
                        result['entities'] = []
                        for _ in range(result['entity_count']):
                            result['entities'].append(String.decode(bytes_io))

                elif result['method'] in (
                        ProtocolEnum.UpdateTeamsMethod.ADD_ENTITIES_TO_TEAM.value,
                        ProtocolEnum.UpdateTeamsMethod.REMOVE_ENTITIES_FROM_TEAM.value,
                ):
                    result['entity_count'] = VarInt.decode(bytes_io)
                    result['entities'] = []
                    for _ in range(result['entity_count']):
                        result['entities'].append(String.decode(bytes_io))

                return result

        class SCPlayUpdateScore(PacketPlay):
            """
                This is sent to the client when it should update a scoreboard item.
            """
            PACKET_ID_HEX = 0x68
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['entity_name'] = String.decode(bytes_io)
                result['objective_name'] = String.decode(bytes_io)
                result['value'] = VarInt.decode(bytes_io)

                result['has_display_name'] = Boolean.decode(bytes_io)
                if result['has_display_name']:
                    result['display_name'] = TextComponent.decode(bytes_io)

                result['has_number_format'] = Boolean.decode(bytes_io)
                if result['has_number_format']:
                    result['number_format'] = VarInt.decode(bytes_io)
                    if result['number_format'] == 1:
                        result['styling'] = NBT.decode(bytes_io)
                    elif result['number_format'] == 2:
                        result['content'] = TextComponent.decode(bytes_io)

                return result

        class SCPlaySetSimulationDistance(PacketPlay):
            """
                Set simulation distance.
            """
            PACKET_ID_HEX = 0x69
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('simulation_distance', VarInt),
            ]

        class SCPlaySetSubtitleText(PacketPlay):
            """
                Set Subtitle Text
            """
            PACKET_ID_HEX = 0x6A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('subtitle_text', TextComponent)
            ]

        class SCPlayUpdateTime(PacketPlay):
            """
                Time is based on ticks, where 20 ticks happen every second.
                There are 24000 ticks in a day, making Minecraft days exactly 20 minutes long.
                The time of day is based on the timestamp modulo 24000.
                0 is sunrise, 6000 is noon, 12000 is sunset, and 18000 is midnight.
                The default SMP server increments the time by 20 every second.
            """
            PACKET_ID_HEX = 0x6B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                # In ticks; not changed by server commands.
                Field('world_age', Long),

                # The world (or region) time, in ticks.
                # If negative the sun will stop moving at the Math.abs of the time.
                Field('time_of_day', Long),

                # If true, the client should automatically advance the time of day according to its ticking rate.
                Field('time_of_day_increasing', Boolean)
            ]

        class SCPlaySetTitleText(PacketPlay):
            """
                Set Title Text
            """
            PACKET_ID_HEX = 0x6C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('title_text', TextComponent)
            ]

        class SCPlaySetTitleAnimationTimes(PacketPlay):
            """
                Set Title Animation Times
            """
            PACKET_ID_HEX = 0x6D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('fade_in', Int),
                Field('stay', Int),
                Field('fade_out', Int),
            ]

        class SCPlayEntitySoundEffect(PacketPlay):
            """
                Plays a sound effect from an entity, either by hardcoded ID or Identifier.
                Sound IDs and names can be found here.
                https://pokechu22.github.io/Burger/1.21.html#sounds
            """
            PACKET_ID_HEX = 0x6E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('sound_effect', Slot.IDOrSoundEvent),
                Field('sound_category', VarInt),
                Field('entity_id', VarInt),

                # 1.0 is 100%, capped between 0.0 and 1.0 by Notchian clients.
                Field('volume', Float),
                Field('pitch', Float),
                Field('seed', Long)
            ]

        class SCPlaySoundEffect(PacketPlay):
            """
                Plays a sound effect at the given location, either by hardcoded ID or Identifier.
                Sound IDs and names can be found here.
                https://pokechu22.github.io/Burger/1.21.html#sounds
            """
            PACKET_ID_HEX = 0x6F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('sound_event', Slot.IDOrSoundEvent),
                Field('sound_category', VarInt),
                Field('effect_position_x', Int),
                Field('effect_position_y', Int),
                Field('effect_position_z', Int),
                Field('volume', Float),
                Field('pitch', Float),
                Field('seed', Long)
            ]

        class SCPlayStartConfiguration(PacketPlay):
            """
                Sent during gameplay in order to redo the configuration process.
                The client must respond with Acknowledge Configuration for the process to start.
            """
            PACKET_ID_HEX = 0x70
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = []

        class SCPlayStopSound(PacketPlay):
            """
                Stop Sound.
            """
            PACKET_ID_HEX = 0x71
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('flags', Byte, enum=ProtocolEnum.SoundCategory),
                Field('source', VarInt, optional_field_name='flags', optional_condition=lambda x: x in (
                    ProtocolEnum.SoundCategory.MUSIC.value,
                    ProtocolEnum.SoundCategory.WEATHER.value,
                )),
                Field('sound', Identifier, optional_field_name='flags', optional_condition=lambda x: x in (
                    ProtocolEnum.SoundCategory.RECORD.value,
                    ProtocolEnum.SoundCategory.WEATHER.value,
                )),
            ]

        class SCPlayStoreCookie(PacketPlay):
            """
                Stores some arbitrary data on the client, which persists between server transfers.
                The Notchian client only accepts cookies of up to 5 kiB in size.
            """
            PACKET_ID_HEX = 0x72
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('key', Identifier),
                Field('payload_length', VarInt),
                FieldsArray(
                    'payload',
                    [
                        Field('payload_bytes', Byte)
                    ],
                    'payload_length',
                )
            ]

        class SCPlaySystemChatMessage(PacketPlay):
            """
                Sends the client a raw system message.
            """
            PACKET_ID_HEX = 0x73
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('content', TextComponent),
                Field('overlay', Boolean)
            ]

        class SCPlaySetTabListHeaderAndFooter(PacketPlay):
            """
                This packet may be used by custom servers to display additional information above/below the player list.
                 It is never sent by the Notchian server.
            """
            PACKET_ID_HEX = 0x74
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('header', TextComponent),
                Field('footer', TextComponent),
            ]

        class SCPlayTagQueryResponse(PacketPlay):
            """
                Sent in response to Query Block Entity Tag or Query Entity Tag.
            """
            PACKET_ID_HEX = 0x75
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('transaction_id', VarInt),
                Field('nbt', NBT)
            ]

        class SCPlayPickupItem(PacketPlay):
            """
                Sent by the server when someone picks up an item lying on the ground
                — its sole purpose appears to be the animation of the item flying towards you.
            """
            PACKET_ID_HEX = 0x76
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('collected_entity_id', VarInt),
                Field('collector_entity_id', VarInt),
                Field('pickup_item_count', VarInt),
            ]

        class SCPlaySynchronizeVehiclePosition(PacketPlay):
            """
                Teleports the entity on the client without changing the reference point of movement deltas
                in future Update Entity Position packets.
                Seems to be used to make relative adjustments to vehicle positions; more information needed.
            """
            PACKET_ID_HEX = 0x77
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('velocity_x', Double),
                Field('velocity_y', Double),
                Field('velocity_z', Double),
                Field('yaw', Float),
                Field('pitch', Float),
                Field('flags', TeleportFlags),
                Field('on_ground', Boolean),
            ]

        class SCPlaySetTickingState(PacketPlay):
            """
                Used to adjust the ticking rate of the client, and whether it's frozen.
            """
            PACKET_ID_HEX = 0x78
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('tick_rate', Float),
                Field('is_frozen', Boolean),
            ]

        class SCPlayStepTick(PacketPlay):
            """
                Advances the client processing by the specified number of ticks.
                Has no effect unless client ticking is frozen.
            """
            PACKET_ID_HEX = 0x79
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('tick_steps', VarInt),
            ]

        class SCPlayTransfer(PacketPlay):
            """
                Notifies the client that it should transfer to the given server.
                Cookies previously stored are preserved between server transfers.
            """
            PACKET_ID_HEX = 0x7A
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('host', String),
                Field('port', String),
            ]

        class SCPlayUpdateAdvancements(PacketPlay):
            """
                Update Advancements.
            """
            PACKET_ID_HEX = 0x7B
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('reset_or_clear', Boolean),
                Field('mapping_size', VarInt),
                FieldsArray(
                    'advancement_mapping',
                    [
                        Field('key', Identifier),
                        Field('value', Advancement)
                    ],
                    'mapping_size'
                ),
                Field('list_size', VarInt),
                FieldsArray(
                    'identifiers',
                    [
                        Field('identifier', Identifier),
                    ],
                    'list_size'
                ),
                Field('progress_size', VarInt),
                FieldsArray(
                    'progress_mapping',
                    [
                        Field('key', Identifier),
                        Field('value', AdvancementProcess)
                    ],
                    'progress_size'
                )
            ]

        class SCPlayUpdateAttributes(PacketPlay):
            """
                Sets attributes on the given entity.
                https://minecraft.wiki/w/Attribute
                # TODO some error
            """
            PACKET_ID_HEX = 0x7C
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('number_of_properties', VarInt),
                FieldsArray(
                    'property',
                    [
                        Field('p_id', VarInt),
                        Field('value', Double),
                        Field('number_of_modifiers', VarInt),
                        FieldsArray(
                            'modifiers',
                            [
                                Field('m_id', Identifier),
                                Field('amount', Double),
                                Field('operation', Byte),
                            ],
                            'number_of_modifiers'
                        )
                    ],
                    'number_of_properties'
                )
            ]

        class SCPlayEntityEffect(PacketPlay):
            """
                Entity Effect.
            """
            PACKET_ID_HEX = 0x7D
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('effect_id', VarInt),
                Field('amplifier', VarInt),
                Field('duration', VarInt),
                Field('flags', Byte)
            ]

        class SCPlayUpdateRecipes(PacketPlay):
            """
                Update Recipes
            """
            PACKET_ID_HEX = 0x7E
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('property_set_count', VarInt),
                FieldsArray(
                    'property_sets',
                    [
                        Field('property_set_id', Identifier),
                        Field('item_count', VarInt),
                        FieldsArray(
                            'items',
                            [
                                Field('item_id', VarInt),
                            ],
                            'item_count'
                        )
                    ],
                    'property_set_count'
                ),
                Field('stonecutter_recipe_count', VarInt),
                FieldsArray(
                    'stonecutter_recipes',
                    [
                        Field('ingredients', IDSet),
                        Field('slot_display', SlotDisplay),
                    ],
                    'stonecutter_recipe_count'
                )
            ]

        class SCPlayUpdateTags(PacketPlay):
            """
                Update Tags
            """
            PACKET_ID_HEX = 0x7F
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('length_of_the_array', VarInt),
                FieldsArray(
                    'array_of_tags',
                    [
                        Field('registry', Identifier),
                        Field('length', VarInt),
                        FieldsArray(
                            'tags',
                            [
                                Field('tag_name', Identifier),
                                Field('count', VarInt),
                                FieldsArray(
                                    'entries',
                                    [
                                        Field('entry', VarInt)
                                    ],
                                    'count'
                                )
                            ],
                            'length'
                        )
                    ],
                    'length_of_the_array'
                )
            ]

        class SCPlayProjectilePower(PacketPlay):
            """
                Projectile Power
            """
            PACKET_ID_HEX = 0x80
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('entity_id', VarInt),
                Field('power', Double),
            ]

        class SCPlayCustomReportDetails(PacketPlay):
            """
                Contains a list of key-value text entries that are included
                in any crash or disconnection report generated during connection to the server.
            """
            PACKET_ID_HEX = 0x81
            DIRECT = ProtocolEnum.Direction.SC
            FIELDS = [
                Field('details_count', VarInt),
                FieldsArray(
                    'details',
                    [
                        Field('title', String),
                        Field('description', String),
                    ],
                    'details_count'
                )
            ]

        class SCPlayServerLinks(PacketPlay):
            """
                This packet contains a list of links that the Notchian client will display
                in the menu available from the pause menu.
                Link labels can be built-in or custom (i.e., any text).
            """
            PACKET_ID_HEX = 0x82
            DIRECT = ProtocolEnum.Direction.SC

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['links_count'] = VarInt.decode(bytes_io)
                result['links'] = []
                for _ in range(result['links_count']):
                    is_built_in = Boolean.decode(bytes_io)
                    if is_built_in:
                        label = VarInt.decode(bytes_io)
                    else:
                        label = TextComponent.decode(bytes_io)
                    url = String.decode(bytes_io)
                    result['links'].append({
                        'is_built_in': is_built_in,
                        'label': label,
                        'url': url,
                    })
                return result

    class Client2Server:

        class CSPlayConfirmTeleportation(PacketPlay):
            """
                Sent by client as confirmation of Synchronize Player Position.
            """
            PACKET_ID_HEX = 0x00
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # The ID given by the Synchronize Player Position packet.
                Field('teleport_id', VarInt),
            ]

        class CSPlayQueryBlockEntityTag(PacketPlay):
            """
                Used when F3+I is pressed while looking at a block.
            """
            PACKET_ID_HEX = 0x01
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # An incremental ID so that the client can verify that the response matches.
                Field('transaction_id', VarInt),

                # The location of the block to check.
                Field('location', Position),
            ]

        class CSPlayBundleItemSelected(PacketPlay):
            """
                Bundle item selected.
            """
            PACKET_ID_HEX = 0x02
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('slot_of_bundle', VarInt),
                Field('slot_in_bundle', VarInt),
            ]

        class CSPlayChangeDifficulty(PacketPlay):
            """
                Must have at least op level 2 to use.
                Appears to only be used on singleplayer;
                the difficulty buttons are still disabled in multiplayer.
            """
            PACKET_ID_HEX = 0x03
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # 0: peaceful, 1: easy, 2: normal, 3: hard .
                Field('new_difficulty', Byte),
            ]

        class CSPlayAcknowledgeMessage(PacketPlay):
            """
                Acknowledge message.
            """
            PACKET_ID_HEX = 0x04
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('message_count', VarInt),
            ]

        class CSPlayChatCommand(PacketPlay):
            """
                Chat Command.
            """
            PACKET_ID_HEX = 0x05
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('command', String),
            ]

        class CSPlaySignedChatCommand(PacketPlay):
            """
                Signed Chat.
            """
            PACKET_ID_HEX = 0x06
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('command', String),
                Field('timestamp', Long),
                Field('salt', Long),
                Field('array_length', VarInt),
                FieldsArray(
                    'array_of_argument_signatures',
                    [
                        Field('argument_name', String),
                        FieldsArray(
                            'signature',
                            [Field('signature_bytes', Byte)],
                            256
                        )
                    ],
                    'array_length'
                ),
                Field('message_count', VarInt),
                Field('Acknowledge', FixedBitSet),
            ]

            @classmethod
            def encode(cls, **kwargs) -> DataPacket:
                bs = bytes()
                bs += String.encode(kwargs['command'])
                bs += Long.encode(kwargs.get('timestamp', round(datetime.datetime.now().timestamp() * 1000)))
                bs += Long.encode(kwargs.get('salt', 1000000000000000000 + random.randint(0, 899999999999999999)))
                bs += VarInt.encode(0)
                bs += VarInt.encode(0)
                bs += b'\x00\x00\x00'
                return DataPacket(len(bs), cls.PACKET_ID_HEX, bs)

        class CSPlayChatMessage(PacketPlay):
            """
                Used to send a chat message to the server.
                The message may not be longer than 256 characters or else the server will kick the client.
            """
            PACKET_ID_HEX = 0x07
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('message', String),
                Field('timestamp', Long),
                Field('salt', Long),
                Field('has_signature', Boolean),
                FieldsArray('signature', [
                    Field('signature_bytes', Byte),
                ], name_of_num_field=256, optional_field_name='has_signature'),
                Field('message_count', VarInt),
                Field('acknowledged', FixedBitSet),
            ]

            @classmethod
            def encode(cls, **kwargs) -> DataPacket:
                bs = bytes()
                bs += String.encode(kwargs['message'])
                bs += Long.encode(kwargs.get('timestamp', round(datetime.datetime.now().timestamp() * 1000)))
                bs += Long.encode(kwargs.get('salt', 1000000000000000000 + random.randint(0, 899999999999999999)))
                bs += Boolean.encode(kwargs.get('has_signature', False))
                bs += VarInt.encode(0)
                bs += b'\x00\x00\x00'
                return DataPacket(len(bs), cls.PACKET_ID_HEX, bs)

        class CSPlayPlayerSession(PacketPlay):
            """
                Player Session.
            """
            PACKET_ID_HEX = 0x08
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('session_id', UUID),
                Field('expires_at', Long),
                Field('public_key_length', VarInt),
                FieldsArray(
                    'public_key',
                    [Field('public_key_byte', Byte)],
                    'public_key_length'
                ),
                Field('key_signature_length', VarInt),
                FieldsArray(
                    'key_signature',
                    [Field('key_signature_byte', Byte)],
                    'key_signature_length'
                ),
            ]

        class CSPlayChunkBatchReceived(PacketPlay):
            """
                Notifies the server that the chunk batch has been received by the client.
                The server uses the value sent in this packet to adjust the number of chunks to be sent in a batch.
            """
            PACKET_ID_HEX = 0x09
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('chunks_per_tick', Float),
            ]

        class CSPlayClientStatus(PacketPlay):
            """
                Client Status.
                Action ID	Action	Notes
                0	Perform respawn	Sent when the client is ready to complete login
                and when the client is ready to respawn after death.
                1	Request stats	Sent when the client opens the Statistics menu.
            """
            PACKET_ID_HEX = 0x0A
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('action_id', VarInt),
            ]

        class CSPlayClientTickEnd(PacketPlay):
            """
                Client Tick End.
            """
            PACKET_ID_HEX = 0x0B
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = []

        class CSPlayClientInformation(PacketPlay):
            """
                Sent when the player connects, or when settings are changed.
            """
            PACKET_ID_HEX = 0x0C
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('locale', String),
                Field('view_distance', Byte),
                Field('chat_mode', VarInt),
                Field('chat_colors', Boolean),
                Field('displayed_skin_parts', UnsignedByte),
                Field('main_hand', VarInt),
                Field('enable_text_filtering', Boolean),
                Field('allow_server_listings', Boolean),
            ]

        class CSPlayCommandSuggestionsRequest(PacketPlay):
            """
                Sent when the client needs to tab-complete a minecraft:ask_server suggestion type.
            """
            PACKET_ID_HEX = 0x0D
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('transaction_id', VarInt),
                Field('text', String),
            ]

        class CSPlayAcknowledgeConfiguration(PacketPlay):
            """
                Sent by the client upon receiving a Start Configuration packet from the server.
                This packet switches the connection state to configuration.
            """
            PACKET_ID_HEX = 0x0E
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = []

        class CSPlayClickContainerButton(PacketPlay):
            """
                Used when clicking on window buttons. Until 1.14, this was only used by enchantment tables.
            """
            PACKET_ID_HEX = 0x0F
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # The ID of the window sent by Open Screen.
                Field('window_id', VarInt),
                Field('button_id', VarInt),
            ]

        class CSPlayClickContainer(PacketPlay):
            """
                This packet is sent by the client when the player clicks on a slot in a window.
            """
            PACKET_ID_HEX = 0x10
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # The ID of the window which was clicked.
                # 0 for player inventory.
                # The server ignores any packets targeting a Window ID other than the current one,
                # including ignoring 0 when any other window is open.
                Field('window_id', VarInt),

                # The last received State ID from either a Set Container Slot or a Set Container Content packet.
                Field('state_id', VarInt),

                Field('slot', Short),
                Field('button', Byte),
                Field('mode', VarInt),
                Field('length_of_the_array', VarInt),
                FieldsArray(
                    'array_of_changed_slots',
                    [
                        Field('slot_number', Short),
                        Field('slot_data', Slot)
                    ],
                    'length_of_the_array'
                ),

                # Item carried by the cursor. Has to be empty (item ID = -1) for drop mode,
                # otherwise nothing will happen.
                Field('carried_item', Slot)
            ]

        class CSPlayCloseContainer(PacketPlay):
            """
                This packet is sent by the client when closing a window.
                Notchian clients send a Close Window packet with Window ID 0 to close their inventory
                even though there is never an Open Screen packet for the inventory.
            """
            PACKET_ID_HEX = 0x11
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # This is the ID of the window that was closed. 0 for player inventory.
                Field('window_id', VarInt),
            ]

        class CSPlayChangeContainerSlotState(PacketPlay):
            """
                This packet is sent by the client when toggling the state of a Crafter.
            """
            PACKET_ID_HEX = 0x12
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('slot_id', VarInt),
                Field('window_id', VarInt),
                Field('state', Boolean),
            ]

        class CSPlayCookieResponse(PacketPlay):
            """
                Response to a Cookie Request (play) from the server.
                The Notchian server only accepts responses of up to 5 kiB in size.
            """
            PACKET_ID_HEX = 0x13
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('key', Identifier),
                Field('has_payload', Boolean),
                Field('payload_length', VarInt, optional_field_name='has_payload'),
                FieldsArray(
                    'payload',
                    [
                        Field('payload_bytes', Byte)
                    ],
                    'payload_length',
                    optional_field_name='has_payload',
                )
            ]

        class CSPlayServerboundPluginMessage(PacketPlay):
            """
                Mods and plugins can use this to send their data.
                Minecraft itself uses some plugin channels.
                These internal channels are in the minecraft namespace.
            """
            PACKET_ID_HEX = 0x14
            DIRECT = ProtocolEnum.Direction.CS

            @classmethod
            def decode(cls, bytes_io: IO) -> OrderedDict[str, Any]:
                result = OrderedDict()
                result['channel'] = Identifier.decode(bytes_io)
                result['data'] = bytes_io.read()
                return result

        class CSPlayDebugSampleSubscription(PacketPlay):
            """
                Subscribes to the specified type of debug sample data,
                which is then sent periodically to the client via Debug Sample.
            """
            PACKET_ID_HEX = 0x15
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # The type of debug sample to subscribe to. Can be one of the following:
                # 0 - Tick time
                Field('sample_type', VarInt),
            ]

        class CSPlayEditBook(PacketPlay):
            """
                Edit Book
            """
            PACKET_ID_HEX = 0x16
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('slot', VarInt),

                # Maximum array size is 100.
                Field('count', VarInt),
                FieldsArray(
                    'entries',
                    [
                        # Text from each page. Maximum string length is 1024 chars.
                        Field('entry', String),
                    ],
                    'count',
                ),

                # If true, the next field is present. true if book is being signed, false if book is being edited.
                Field('has_title', Boolean),
                Field('title', String, optional_field_name='has_title'),

            ]

        class CSPlayQueryEntityTag(PacketPlay):
            """
                Used when F3+I is pressed while looking at an entity.
            """
            PACKET_ID_HEX = 0x17
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # An incremental ID so that the client can verify that the response matches.
                Field('transaction_id', VarInt),

                # The ID of the entity to query.
                Field('entity_id', VarInt),
            ]

        class CSPlayInteract(PacketPlay):
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
            PACKET_ID_HEX = 0x18
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('entity_id', VarInt),
                Field('_type', VarInt),
                Field(
                    'target_x', Float,
                    optional_field_name='_type',
                    optional_condition=lambda x: x == ProtocolEnum.InteractType.INTERACT_AT.value
                ),
                Field(
                    'target_y', Float,
                    optional_field_name='_type',
                    optional_condition=lambda x: x == ProtocolEnum.InteractType.INTERACT_AT.value
                ),
                Field(
                    'target_y', Float,
                    optional_field_name='_type',
                    optional_condition=lambda x: x == ProtocolEnum.InteractType.INTERACT_AT.value
                ),
                Field(
                    'hand', VarInt, optional_field_name='_type',
                    optional_condition=lambda x: x in (
                        ProtocolEnum.InteractType.INTERACT.value,
                        ProtocolEnum.InteractType.INTERACT_AT.value,
                    )
                ),
                Field('sneaking', Boolean),
            ]

        class CSPlayJigsawGenerate(PacketPlay):
            """
                Sent when Generate is pressed on the Jigsaw Block interface.
            """
            PACKET_ID_HEX = 0x19
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('location', Position),
                Field('levels', VarInt),
                Field('keep_jigsaws', Boolean),
            ]

        class CSPlayServerboundKeepAlive(PacketPlay):
            """
                The server will frequently send out a keep-alive (see Clientbound Keep Alive),
                each containing a random ID. The client must respond with the same packet.
            """
            PACKET_ID_HEX = 0x1A
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('keep_alive_id', Long),
            ]

        class CSPlayLockDifficulty(PacketPlay):
            """
                Must have at least op level 2 to use.
                Appears to only be used on singleplayer;
                the difficulty buttons are still disabled in multiplayer.
            """
            PACKET_ID_HEX = 0x1B
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('locked', Boolean),
            ]

        class CSPlaySetPlayerPosition(PacketPlay):
            """
                Updates the player's XYZ position on the server.
            """
            PACKET_ID_HEX = 0x1C
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('x', Double),

                # Absolute feet position, normally Head Y - 1.62.
                Field('feet_y', Double),

                Field('z', Double),

                # Bit field: 0x01: on ground, 0x02: pushing against wall.
                Field('flags', Byte)
            ]

        class CSPlaySetPlayerPositionAndRotation(PacketPlay):
            """
                A combination of Move Player Rotation and Move Player Position.
            """
            PACKET_ID_HEX = 0x1D
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('x', Double),

                # Absolute feet position, normally Head Y - 1.62.
                Field('feet_y', Double),

                Field('z', Double),
                Field('yaw', Float),
                Field('pitch', Float),

                # Bit field: 0x01: on ground, 0x02: pushing against wall.
                Field('flags', Byte)
            ]

        class CSPlaySetPlayerRotation(PacketPlay):
            """
                Updates the direction the player is looking in.
            """
            PACKET_ID_HEX = 0x1E
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('yaw', Float),
                Field('pitch', Float),

                # Bit field: 0x01: on ground, 0x02: pushing against wall.
                Field('flags', Byte)
            ]

        class CSPlaySetPlayerMovementFlags(PacketPlay):
            """
                This packet as well as Set Player Position, Set Player Rotation,
                and Set Player Position and Rotation are called the “serverbound movement packets”.
                Vanilla clients will send Move Player Position once every 20 ticks even for a stationary player.
            """
            PACKET_ID_HEX = 0x1F
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # Bit field: 0x01: on ground, 0x02: pushing against wall.
                Field('flags', Byte),
            ]

        class CSPlayMoveVehicle(PacketPlay):
            """
                Sent when a player moves in a vehicle.
                Fields are the same as in Set Player Position and Rotation.
                Note that all fields use absolute positioning and do not allow for relative positioning.
            """
            PACKET_ID_HEX = 0x20
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('x', Double),
                Field('y', Double),
                Field('z', Double),
                Field('yaw', Float),
                Field('pitch', Float),
                Field('on_ground', Boolean),
            ]

        class CSPlayPaddleBoat(PacketPlay):
            """
                Used to visually update whether boat paddles are turning.
                The server will update the Boat entity metadata to match the values here.
            """
            PACKET_ID_HEX = 0x21
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('left_paddle_turning', Boolean),
                Field('right_paddle_turning', Boolean),
            ]

        class CSPlayPickItemFromBlock(PacketPlay):
            """
                Used to swap out an empty space on the hotbar with the item in the given inventory slot.
                The Notchian client uses this for pick block functionality (middle click)
                to retrieve items from the inventory.
            """
            PACKET_ID_HEX = 0x22
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('slot_to_use', VarInt),
            ]

        class CSPlayPickItemFromEntity(PacketPlay):
            """
                Pick Item From Entity.
            """
            PACKET_ID_HEX = 0x23
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('slot_to_use', VarInt),
            ]

        class CSPlayPingRequest(PacketPlay):
            """
                Ping Request.
            """
            PACKET_ID_HEX = 0x24
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # Maybe any number.
                # Notchian clients use a system-dependent time value which is counted in milliseconds.
                Field('payload', Long),
            ]

        class CSPlayPlaceRecipe(PacketPlay):
            """
                This packet is sent when a player clicks a recipe in the crafting book that is craftable (white border).
            """
            PACKET_ID_HEX = 0x25
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('window_id', Byte),

                # ID of recipe previously defined in Recipe Book Add.
                Field('recipe_id', VarInt),

                # Affects the amount of items processed; true if shift is down when clicked.
                Field('make_all', Boolean),
            ]

        class CSPlayPlayerAbilities(PacketPlay):
            """
                The vanilla client sends this packet when the player starts/stops flying
                with the Flags parameter changed accordingly.
            """
            PACKET_ID_HEX = 0x26
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # Bit mask. 0x02: is flying.
                Field('flags', Byte)
            ]

        class CSPlayPlayerAction(PacketPlay):
            """
                Sent when the player mines a block.
                A Notchian server only accepts digging packets with coordinates within a 6-unit radius
                between the center of the block and the player's eyes.
            """
            PACKET_ID_HEX = 0x27
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('status', VarInt),
                Field('location', Position),
                Field('face', Byte),
                Field('sequence', VarInt),
            ]

        class CSPlayPlayerCommand(PacketPlay):
            """
                Sent by the client to indicate that it has performed certain actions:
                sneaking (crouching), sprinting, exiting a bed, jumping with a horse,
                and opening a horse's inventory while riding it.
            """
            PACKET_ID_HEX = 0x28
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('entity_id', VarInt),
                Field('action_id', VarInt, enum=ProtocolEnum.EntityAction),

                # Only used by the “start jump with horse” action, in which case it ranges from 0 to 100.
                # In all other cases it is 0.
                Field('jump_boost', VarInt),
            ]

        class CSPlayPlayerInput(PacketPlay):
            """
                Player Input.
            """
            PACKET_ID_HEX = 0x29
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('flags', UnsignedByte, enum=ProtocolEnum.PlayerInput),
            ]

        class CSPlayPlayerLoaded(PacketPlay):
            """
                Sent by the client after the server starts sending chunks and the player's chunk has loaded.
            """
            PACKET_ID_HEX = 0x2A
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = []

        class CSPlayPong(PacketPlay):
            """
                Response to the clientbound packet (Ping) with the same id.
            """
            PACKET_ID_HEX = 0x2B
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # id is the same as the ping packet
                Field('_id', Int)
            ]

        class CSPlayChangeRecipeBookSettings(PacketPlay):
            """
                Replaces Recipe Book Data, type 1.
            """
            PACKET_ID_HEX = 0x2C
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # 0: crafting, 1: furnace, 2: blast furnace, 3: smoker.
                Field('book_id', VarInt, enum=ProtocolEnum.BookId),
                Field('book_open', Boolean),
                Field('filter_active', Boolean),
            ]

        class CSPlaySetSeenRecipe(PacketPlay):
            """
                Sent when recipe is first seen in recipe book. Replaces Recipe Book Data, type 0.
            """
            PACKET_ID_HEX = 0x2D
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # ID of recipe previously defined in Recipe Book Add.
                Field('recipe_id', VarInt)
            ]

        class CSPlayRenameItem(PacketPlay):
            """
                Sent as a player is renaming an item in an anvil
                (each keypress in the anvil UI sends a new Rename Item packet).
                If the new name is empty, then the item loses its custom name
                (this is different from setting the custom name to the normal name of the item).
                The item name may be no longer than 50 characters long, and if it is longer than that,
                then the rename is silently ignored.
            """
            PACKET_ID_HEX = 0x2E
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('item_name', String),
            ]

        class CSPlayResourcePackResponse(PacketPlay):
            """
                Resource Pack Response.
            """
            PACKET_ID_HEX = 0x2F
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # The unique identifier of the resource pack received in the Add Resource Pack (play) request.
                Field('uuid', UUID),
                Field('result', VarInt, enum=ProtocolEnum.ResourcePackStatus),
            ]

        class CSPlaySeenAdvancements(PacketPlay):
            """
                Seen Advancements.
            """
            PACKET_ID_HEX = 0x30
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # 0: Opened tab, 1: Closed screen.
                Field('action', VarInt, enum=ProtocolEnum.AdvancementTab),
                Field(
                    'tab_id', Identifier, optional_field_name='action',
                    optional_condition=lambda x: x == ProtocolEnum.AdvancementTab.OPEN_TAB.value
                )
            ]

        class CSPlaySelectTrade(PacketPlay):
            """
                When a player selects a specific trade offered by a villager NPC.
            """
            PACKET_ID_HEX = 0x31
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('selected_slot', VarInt),
            ]

        class CSPlaySetBeaconEffect(PacketPlay):
            """
                Changes the effect of the current beacon.
            """
            PACKET_ID_HEX = 0x32
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('has_primary_effect', Boolean),

                # A potion id
                Field('primary_effect', VarInt, optional_field_name='has_primary_effect'),

                Field('has_secondary_effect', Boolean),
                Field('secondary_effect', VarInt, optional_field_name='has_secondary_effect'),
            ]

        class CSPlaySetHeldItem(PacketPlay):
            """
                Sent when the player changes the slot selection.
            """
            PACKET_ID_HEX = 0x33
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # The slot which the player has selected (0–8).
                Field('slot', Short)
            ]

        class CSPlayProgramCommandBlock(PacketPlay):
            """
                Program command block.
            """
            PACKET_ID_HEX = 0x34
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('location', Position),
                Field('command', String),
                Field('mode', VarInt, enum=ProtocolEnum.CommandBlockMode),

                # 0x01: Track Output
                # (if false, the output of the previous command will not be stored within the command block);
                # 0x02: Is conditional; 0x04: Automatic.
                Field('flags', Byte)
            ]

        class CSPlayProgramCommandBlockMincart(PacketPlay):
            """
                Program command block mincart.
            """
            PACKET_ID_HEX = 0x35
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('entity_id', VarInt),
                Field('command', String),

                # If false, the output of the previous command will not be stored within the command block.
                Field('track_output', Boolean)
            ]

        class CSPlaySetCreativeModeSlot(PacketPlay):
            """
                While the user is in the standard inventory (i.e., not a crafting bench) in Creative mode,
                the player will send this packet.
            """
            PACKET_ID_HEX = 0x36
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # Inventory slot.
                Field('slot', Short),
                Field('clicked_item', Slot)
            ]

        class CSPlayProgramJigsawBlock(PacketPlay):
            """
                Sent when Done is pressed on the Jigsaw Block interface.
            """
            PACKET_ID_HEX = 0x37
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('location', Position),
                Field('name', Identifier),
                Field('target', Identifier),
                Field('pool', Identifier),
                Field('final_state', String),
                Field('joint_type', String),
                Field('selection_priority', VarInt),
                Field('placement_priority', VarInt),
            ]

        class CSPlayProgramStructureBlock(PacketPlay):
            """
                Program structure block.
            """
            PACKET_ID_HEX = 0x38
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('location', Position),
                Field('action', VarInt, enum=ProtocolEnum.StructureBlockAction),
                Field('mode', VarInt, enum=ProtocolEnum.StructureBlockMode),
                Field('name', String),

                # Between -48 and 48
                Field('offset_x', Byte),
                Field('offset_y', Byte),
                Field('offset_z', Byte),

                # Between 0 and 48
                Field('size_x', Byte),
                Field('size_y', Byte),
                Field('size_z', Byte),

                Field('mirror', VarInt, enum=ProtocolEnum.StructureBlockMirror),
                Field('rotation', VarInt, enum=ProtocolEnum.StructureBlockRotation),
                Field('metadata', String),

                # Between 0 and 1
                Field('integrity', Float),
                Field('seed', VarLong),
                Field('flags', Byte),
            ]

        class CSPlayUpdateSign(PacketPlay):
            """
                This message is sent from the client to the server when the “Done” button is pushed after placing a sign
                The server only accepts this packet after Open Sign Editor, otherwise this packet is silently ignored.
            """
            PACKET_ID_HEX = 0x39
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('location', Position),
                Field('is_front_text', Boolean),
                Field('line_1', String),
                Field('line_2', String),
                Field('line_3', String),
                Field('line_4', String),
            ]

        class CSPlaySwingArm(PacketPlay):
            """
                Sent when the player's arm swings.
            """
            PACKET_ID_HEX = 0x3A
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('hand', VarInt, enum=ProtocolEnum.Hand),
            ]

        class CSPlayTeleportToEntity(PacketPlay):
            """
                Teleports the player to the given entity. The player must be in spectator mode.
            """
            PACKET_ID_HEX = 0x3B
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                # UUID of the player to teleport to (can also be an entity UUID).
                Field('target_player', UUID)
            ]

        class CSPlayUseItemOn(PacketPlay):
            """
                Use Item On
            """
            PACKET_ID_HEX = 0x3C
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('hand', VarInt, enum=ProtocolEnum.Hand),
                Field('location', Position),

                # The face on which the block is placed (as documented at Player Action).
                Field('face', VarInt, enum=ProtocolEnum.Face),

                # The position of the crosshair on the block, from 0 to 1 increasing from west to east.
                Field('cursor_position_x', Float),
                # The position of the crosshair on the block, from 0 to 1 increasing from bottom to top.
                Field('cursor_position_y', Float),
                # The position of the crosshair on the block, from 0 to 1 increasing from north to south.
                Field('cursor_position_z', Float),

                # True when the player's head is inside of a block.
                Field('inside_block', Boolean),

                Field('world_border_hit', Boolean),
                Field('sequence', VarInt),
            ]

        class CSPlayUseItem(PacketPlay):
            """
                Sent when pressing the Use Item key (default: right click) with an item in hand.
            """
            PACKET_ID_HEX = 0x3D
            DIRECT = ProtocolEnum.Direction.CS
            FIELDS = [
                Field('hand', VarInt, enum=ProtocolEnum.Hand),
                Field('sequence', VarInt),

                # Player head rotation along the Y-Axis.
                Field('yaw', Float),
                # Player head rotation along the X-Axis.
                Field('pitch', Float),
            ]
