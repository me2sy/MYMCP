# -*- coding: utf-8 -*-
"""
    player
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-02-10 0.1.2 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.1.2'

__all__ = [
    'Player',
]

from dataclasses import dataclass, field
from decimal import Decimal, getcontext
import math
import uuid
import threading
import time
from typing import Callable, ClassVar

from loguru import logger
import numpy as np
from twisted.internet.protocol import Protocol

from mymcp.protocols import *
from mymcp.protocols import ProtocolEnum as PE
from mymcp.data_type import Position, Chunk, block_ids

getcontext().prec = 12


@dataclass
class Vector:
    x: Decimal = Decimal(0)
    y: Decimal = Decimal(0)
    z: Decimal = Decimal(0)

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(
            Decimal(self.x + other.x),
            Decimal(self.y + other.y),
            Decimal(self.z + other.z)
        )

    def __sub__(self, other: 'Vector') -> 'Vector':
        return Vector(
            Decimal(self.x - other.x),
            Decimal(self.y - other.y),
            Decimal(self.z - other.z)
        )

    def main_block_pos(self) -> Position:
        """
            获取坐标 minecraft position
        :return:
        """
        return Position(
            math.floor(self.x),
            math.floor(self.y) - 1,
            math.floor(self.z),
        )

@dataclass
class EntityPosition:
    """
        实体位置
    """
    vector: Vector = field(default_factory=Vector)
    velocity_x: float = .0
    velocity_y: float = .0
    velocity_z: float = .0
    pitch: float = .0
    yaw: float = .0
    head_yaw: float = 0.0
    data: int = 0
    e_flags: int = 1


@dataclass
class Entity:
    """
        实体
    """

    entity_id: int
    entity_uuid: uuid.UUID
    e_type: PE.EntityType

    position: EntityPosition | None = None


class ChunkManager:
    """
        Chunk 管理器
    """

    def __init__(self, dimension_count: int = 16):
        self.chunks = {_: {} for _ in range(dimension_count)}

    def add(self, dimension: int, chunk: Chunk):
        self.chunks[dimension][f"{chunk.x}_{chunk.z}"] = chunk

    def delete(self, dimension: int, chunk_x: int, chunk_z: int):
        try:
            del self.chunks[dimension][f"{chunk_x}_{chunk_z}"]
        except KeyError:
            ...

    def get_chunk(self, dimension: int, chunk_x: int, chunk_z: int) -> Chunk | None:
        try:
            return self.chunks[dimension][f"{chunk_x}_{chunk_z}"]
        except KeyError:
            return None

    def get_chunk_by_pos(self, dimension: int, location: Position) -> Chunk | None:
        try:
            return self.chunks[dimension][f"{location.x // 16}_{location.z // 16}"]
        except KeyError:
            return None

    def get_block(self, dimension: int, location: Position) -> int | None:
        """
            获取 block ID
        :param dimension:
        :param location:
        :return:
        """
        try:
            return self.chunks[dimension][f"{location.x // 16}_{location.z // 16}"].get_block_id(location)
        except KeyError:
            return None

    def update_block(self, dimension: int, location: Position, block_id: int) -> bool:
        """
            更新 Block 数据
        :param dimension:
        :param location:
        :param block_id:
        :return:
        """
        _chunk = self.get_chunk_by_pos(dimension, location)
        if _chunk is None:
            return False
        else:
            _chunk.update_block(location, block_id)
            return True

    def get_block_cage(self, dimension: int, main_block_pos: Position) -> np.ndarray:
        """
            blocks around player
            # 4 * 3 * 3 ndarray with y,z,x order
            y * 3 * 3 ndarray with y,z,x order
        :param dimension:
        :param main_block_pos: player所属position
        :return:
        """
        blocks = []

        # y = main_block_pos.y + (64 if dimension == 0 else 0)

        for x in range(main_block_pos.x - 1, main_block_pos.x + 2):
            _x_line = []
            for z in range(main_block_pos.z - 1, main_block_pos.z + 2):
                _x_line.append(
                    self.get_chunk(dimension, x // 16, z // 16).blocks[
                        # y: y + 4, z % 16, x % 16
                        :, z % 16, x % 16
                    ]
                )
            blocks.append(_x_line)
        return np.array(blocks).T


@dataclass
class NextMoveAction:
    """
        判断下一个位置动作
    """

    ACTION_BLOCK_NULL: ClassVar[int] = -3
    ACTION_BLOCK_JUMP: ClassVar[int] = -2
    ACTION_BLOCK_HEAD: ClassVar[int] = -1

    ACTION_MOVE: ClassVar[int] = 0
    ACTION_JUMP: ClassVar[int] = 1
    ACTION_FALL: ClassVar[int] = 2

    is_moveable: bool
    action: int
    y: int
    block_id: int


class Player:

    MAX_MESSAGE_LENGTH = 256

    EMPTY_BLOCKS = (
        0,      # air
        2048,   # short_grass
    )

    def __init__(
            self,
            name: str,
            local_uuid: uuid.UUID
    ):
        self.name = name
        self.local_uuid = local_uuid
        self.server_uuid = None

        self.dimension = -1

        self.position = EntityPosition()
        self.entity: Entity | None = None

        # Health
        self.health: float
        self.food: int
        self.food_saturation: float

        # Experience
        self.experience_bar: float
        self.level: int
        self.total_experience: int

        self.client: Protocol

        self.reactions = {
            # Process
            PlayProtocols.Server2Client.SCPlayLogin: [self.rc_login],
            PlayProtocols.Server2Client.SCPlaySynchronizePlayerPosition: [self.rc_synchronize_player_position],
            PlayProtocols.Server2Client.SCPlaySetHealth: [self.rc_set_health_or_experience],
            PlayProtocols.Server2Client.SCPlaySetExperience: [self.rc_set_health_or_experience],
            PlayProtocols.Server2Client.SCPlayClientboundKeepAlive: [self.rc_keep_alive],
            PlayProtocols.Server2Client.SCPlayDisconnect: [self.rc_disconnect],

            # Chat
            PlayProtocols.Server2Client.SCPlayPlayerChatMessage: [self.rc_chat_message],
            PlayProtocols.Server2Client.SCPlaySystemChatMessage: [self.rc_system_chat_message],

            # Entity
            PlayProtocols.Server2Client.SCPlaySpawnEntity: [self.rc_spawn_entity],
            PlayProtocols.Server2Client.SCPlayRemoveEntities: [self.rc_remove_entities],
            PlayProtocols.Server2Client.SCPlayEntityAnimation: [self.rc_entity_animation],

            # PlayProtocols.Server2Client.SCPlayPlayerInfoUpdate: self.rc_player_info_update,

            # Chunk
            PlayProtocols.Server2Client.SCPlayChunkBatchStart: [self.rc_chunk_process],
            PlayProtocols.Server2Client.SCPlayChunkBatchFinished: [self.rc_chunk_process],
            PlayProtocols.Server2Client.SCPlayChunkDataAndUpdateLight: [self.rc_chunk_data],
            PlayProtocols.Server2Client.SCPlayUnloadChunk: [self.rc_unload_chunk],

            PlayProtocols.Server2Client.SCPlaySpawnExperienceOrb: [self.rc_spawn_experience_orb],

            # Block
            PlayProtocols.Server2Client.SCPlayAcknowledgeBlockChange: [self.rc_block_actions],
            PlayProtocols.Server2Client.SCPlayBlockUpdate: [self.rc_block_update],

            PlayProtocols.Server2Client.SCPlayRespawn: [self.rc_respawn],
            PlayProtocols.Server2Client.SCPlayCombatDeath: [self.rc_combat_death],
            PlayProtocols.Server2Client.SCPlayGameEvent: [self.rc_game_event],

            PlayProtocols.Server2Client.SCPlayUpdateEntityPosition: [self.rc_update_entity_pr],
            PlayProtocols.Server2Client.SCPlayUpdateEntityPositionAndRotation: [self.rc_update_entity_pr],
            PlayProtocols.Server2Client.SCPlayUpdateEntityRotation: [self.rc_update_entity_pr],

        }

        self.entities = {}
        self.other_players = {}

        self.chunk_manager = ChunkManager()
        self.start_recv = None

        self.wake_up = False

        self.sequence = 0

        self.cage: np.ndarray | None = None

    def f_talk(self, message: str):
        """
            Talk
        :param message:
        :return:
        """
        for i in range(0, len(message), self.MAX_MESSAGE_LENGTH):
            self.client.send_protocol(
                PlayProtocols.Client2Server.CSPlayChatMessage,
                message=message[i:i+self.MAX_MESSAGE_LENGTH]
            )

    def f_chat_command(self, command: str):
        """
            Send Command
        :param command:
        :return:
        """
        self.client.send_protocol(
            PlayProtocols.Client2Server.CSPlaySignedChatCommand,
            command=command
        )

    def f_stare_at(self, target_vector: Vector):
        """
            转动视角
        :param target_vector:
        :return:
        """
        dv = target_vector - self.position.vector
        r = Decimal(math.sqrt(dv.x ** 2 + dv.y ** 2 + dv.z ** 2))
        yaw = Decimal(-math.atan2(dv.x, dv.z) / math.pi * 180)
        if yaw < 0:
            yaw += 360
        pitch = Decimal(-math.asin(dv.y / r) / math.pi * 180)
        self.position.yaw = yaw
        self.position.pitch = pitch
        self.client.send_protocol(
            PlayProtocols.Client2Server.CSPlaySetPlayerRotation,
            yaw=yaw, pitch=pitch, flags=self.position.e_flags
        )

    def f_update_cage(self):
        """
            更新 player 周围blocks
        :return:
        """
        self.cage = self.chunk_manager.get_block_cage(
            self.dimension,
            self.position.vector.main_block_pos()
        )

    def f_next_block_action(
            self, abs_on_block_y: int, y_blocks: np.ndarray, can_jump: bool,
            y_fix: int = 64
    ) -> NextMoveAction:
        """
            判断前往的下一个block动作
            blocks 从底到顶
        :param abs_on_block_y:
        :param y_blocks:
        :param can_jump:
        :param y_fix:
        :return:
        """
        try:
            if y_blocks[abs_on_block_y + 2] not in self.EMPTY_BLOCKS:
                return NextMoveAction(False, NextMoveAction.ACTION_BLOCK_HEAD, abs_on_block_y - y_fix, -1)

            if y_blocks[abs_on_block_y + 1] not in self.EMPTY_BLOCKS:   # Jump or Block
                if y_blocks[abs_on_block_y + 3] in self.EMPTY_BLOCKS and can_jump:
                    return NextMoveAction(
                        True, NextMoveAction.ACTION_JUMP, abs_on_block_y + 1 - y_fix, int(y_blocks[abs_on_block_y + 1])
                    )
                else:
                    return NextMoveAction(False, NextMoveAction.ACTION_BLOCK_JUMP, abs_on_block_y - y_fix, -1)

            if y_blocks[abs_on_block_y] not in self.EMPTY_BLOCKS:
                return NextMoveAction(True, NextMoveAction.ACTION_MOVE, abs_on_block_y - y_fix, int(y_blocks[abs_on_block_y]))

            else:   # Fall
                for index, block in enumerate(reversed(y_blocks[:abs_on_block_y])):
                    if block not in self.EMPTY_BLOCKS:
                        return NextMoveAction(
                            True, NextMoveAction.ACTION_FALL, abs_on_block_y - index - 1 - y_fix, int(block)
                        )

                return NextMoveAction(False, NextMoveAction.ACTION_BLOCK_NULL, -1, -1)

        except IndexError:
            return NextMoveAction(False, NextMoveAction.ACTION_BLOCK_NULL, -1, -1)


    def get_player_entity(self, player_uuid: uuid.UUID) -> Entity | None:
        """
            获取玩家entity
        :param player_uuid:
        :return:
        """
        for eid, entity in self.entities.items():
            if entity.entity_uuid == player_uuid:
                return entity
        return None

    def reaction(self, data_packet: DataPacket, protocol):
        """
            反应
        :param data_packet:
        :param protocol:
        :return:
        """
        for func in self.reactions.get(protocol, [lambda _data_packet, _protocol, _player: None]):
            threading.Thread(target=func, args=(data_packet, protocol, self)).start()

    def register_protocol_reaction(self, protocol, reaction: Callable, append: bool=False):
        """
            注册反应函数
        :param protocol:
        :param reaction:
        :param append:
        :return:
        """
        if protocol in self.reactions:
            if append:
                self.reactions[protocol].append(reaction)
                return
        self.reactions[protocol] = [reaction]


    # 内置反应函数

    def rc_login(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            登录信息
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        player_instance.entity = Entity(
            _data['entity_id'],
            player_instance.server_uuid,
            PE.EntityType.PLAYER
        )
        player_instance.dimension = _data['dimension_type']
        logger.success(f"S>P Login {_data}")

    def rc_synchronize_player_position(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            初始化/同步 player 位置
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())

        for _ in ['x', 'y', 'z']:
            player_instance.position.vector.__setattr__(
                _,
                player_instance.position.vector.__getattribute__(_) + Decimal(_data[_])
                if _data['flags'] & PE.TeleportFlags[_].value else Decimal(_data[_])
            )

        for key, value in _data.items():
            if hasattr(player_instance.position, key):
                # 注意是否为相对位置
                setattr(
                    player_instance.position,
                    key,
                    player_instance.position.__getattribute__(key) + Decimal(value)
                    if _data['flags'] & PE.TeleportFlags[key].value else Decimal(value)
                )

        # 确认位置
        player_instance.client.send_protocol(
            PlayProtocols.Client2Server.CSPlayConfirmTeleportation,
            teleport_id=_data['teleport_id'],
        )
        logger.success(f"S>P Play synchronize player position {_data} | {player_instance.position}")

    def rc_set_health_or_experience(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            设置 player 生命及经验
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        for k, v in _data.items():
            setattr(player_instance, k, v)

    def rc_keep_alive(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            Keep Alive
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        player_instance.client.send_protocol(
            PlayProtocols.Client2Server.CSPlayServerboundKeepAlive,
            **protocol.decode(data_packet.bytes_io())
        )

    def rc_disconnect(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            player disconnect
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        logger.error(f"S>P Play disconnect {_data} | {data_packet}")
        self.client.disconnect()

    def rc_chat_message(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            聊天信息
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())

        logger.info(f"S>P Chat Message {_data}")

        if _data['sender'] == player_instance.server_uuid:
            return

        msg = _data['message']

        if msg == 'b':
            cage = player_instance.chunk_manager.get_block_cage(
                    player_instance.dimension,
                    player_instance.position.vector.main_block_pos(),
                )

            y, z, x = cage.shape
            for _y in range(y):
                print('\ny', _y)
                for _z in range(z):
                    for _x in range(x):
                        bid = cage[_y, _z, _x]
                        block = block_ids[bid]['name'].split(':')[1]
                        print(f"{bid:>5}:{block:<20}", end=' ')
                    print('\n')

        elif msg == 'c':
            mbp = player_instance.position.vector.main_block_pos()

            cage = player_instance.chunk_manager.get_block_cage(
                player_instance.dimension,
                mbp,
            )
            y = mbp.y + (64 if player_instance.dimension == 0 else 0)
            for z in range(3):
                for x in range(3):
                    if x == 1 and z == 1:
                        continue

                    nba = player_instance.f_next_block_action(
                        y,
                        cage[:, z, x],
                        cage[y + 3, 1, 1] in self.EMPTY_BLOCKS,
                        y_fix=(64 if player_instance.dimension == 0 else 0),
                    )
                    print(f"{x}:{z} | {nba} | {block_ids[nba.block_id] if nba.is_moveable else ''}")

        elif msg == 'hi':
            entity = player_instance.get_player_entity(_data['sender'])
            if entity:
                player_instance.f_stare_at(entity.position.vector)

            player_instance.f_talk('Hi There!')

    def rc_system_chat_message(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            System Chat Message
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        logger.success(f"S>P Play System Chat {_data}")

    def rc_spawn_entity(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            Spawn entity
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        try:
            _data = protocol.decode(data_packet.bytes_io())
            entity = Entity(
                entity_id=_data['entity_id'],
                entity_uuid=_data['entity_uuid'],
                e_type=PE.EntityType(_data['_type']),
                position=EntityPosition(
                    vector=Vector(Decimal(_data['x']), Decimal(_data['y']), Decimal(_data['z'])),
                    velocity_x=_data['velocity_x'], velocity_y=_data['velocity_y'], velocity_z=_data['velocity_z'],
                    pitch=_data['pitch'], yaw=_data['yaw'], head_yaw=_data['head_yaw'],
                    data=_data['data']
                )
            )
            self.entities[entity.entity_id] = entity
        except Exception as e:
            logger.exception(f"S>P Play Spawn Entity Error {data_packet.data}")
            ...

    def rc_remove_entities(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        _data = protocol.decode(data_packet.bytes_io())
        for _ in _data['entities']:
            if _['entity_id'] in self.entities:
                self.entities.pop(_['entity_id'])

    def rc_entity_animation(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        _data = protocol.decode(data_packet.bytes_io())
        logger.success(f"S>P Play Entity Animation {_data}")

    def rc_player_info_update(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        _data = protocol.decode(data_packet.bytes_io())
        logger.success(f"S>P Play Player Info Update {_data}")

    def rc_chunk_process(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        if protocol == PlayProtocols.Server2Client.SCPlayChunkBatchStart:
            self.start_recv = time.time_ns()
        else:
            _data = protocol.decode(data_packet.bytes_io())
            self.client.send_protocol(
                PlayProtocols.Client2Server.CSPlayChunkBatchReceived,
                chunks_per_tick=25 / ((time.time_ns() - self.start_recv) / 1000000 / _data['batch_size'])
            )

    def rc_chunk_data(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            加载 Chunk 数据
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        chunk_block_size = {0: 24}.get(self.dimension, 16)
        chunk = Chunk.decode_result(
            dimension=self.dimension,
            **protocol.decode(data_packet.bytes_io(), chunk_block_size),
        )
        self.chunk_manager.add(self.dimension, chunk)

    def rc_unload_chunk(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        self.chunk_manager.delete(self.dimension, **protocol.decode(data_packet.bytes_io()))

    def rc_block_update(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        self.chunk_manager.update_block(self.dimension, **protocol.decode(data_packet.bytes_io()))

    def rc_spawn_experience_orb(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        _data = protocol.decode(data_packet.bytes_io())
        logger.success(f"S>P Spawn Experience Orb {_data}")

    def rc_block_actions(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        _data = protocol.decode(data_packet.bytes_io())
        logger.success(f"S>P block_actions: {protocol.__name__} > {_data}")

    def rc_respawn(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            重生
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        self.dimension = _data['dimension_type']
        logger.success(f"S>P respawn: {_data}")

    def rc_combat_death(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            狗带事件
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        msg = _data['message']['translate'].value
        logger.error(f"S>P combat_death: {msg}")

        # auto respawn
        self.client.send_protocol(
            PlayProtocols.Client2Server.CSPlayClientStatus,
            action_id=PE.ClientStatusAction.PERFORM_RESPAWN.value
        )

    def rc_game_event(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            Game Event
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        logger.info(f"S>P Game Event {_data}")

    def rc_update_entity_pr(self, data_packet: DataPacket, protocol, player_instance: 'Player'):
        """
            Update Entity Pr
        :param data_packet:
        :param protocol:
        :param player_instance:
        :return:
        """
        _data = protocol.decode(data_packet.bytes_io())
        entity = player_instance.entities.get(_data['entity_id'], None)
        if entity is None:
            return

        if 'delta_x' in _data:
            entity.position.vector.x += Decimal(_data['delta_x']) / Decimal(4096.0)
            entity.position.vector.y += Decimal(_data['delta_y']) / Decimal(4096.0)
            entity.position.vector.z += Decimal(_data['delta_z']) / Decimal(4096.0)

        if 'yaw' in _data:
            entity.position.yaw = Decimal(_data['yaw'])
            entity.position.pitch = Decimal(_data['pitch'])
