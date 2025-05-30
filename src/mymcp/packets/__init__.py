# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-05-26 0.2.0 Me2sY  重构

        2025-05-23 0.1.0 Me2sY  创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'Codec', 'Packet'
]

import os
import zlib
from dataclasses import dataclass
from io import BytesIO
from typing import Iterable, ClassVar, Self

from mymcp.data_types import VarInt, DataPacket, Combined
from mymcp.packets.enums import Enums


class Codec:
    """
        编解码器
    """

    SUCCESS = 0
    UNFINISHED = 1
    END = 2

    def __init__(self, bound_to: Enums.BoundTo):
        self.bytes_io = BytesIO()
        self.last_pos = 0
        self.compression_threshold = -1
        self.bound_to = bound_to

    def decode_a_packet(self) -> tuple[int, DataPacket | None]:
        """
            解析Packet
        :return:
        """

        loc = self.bytes_io.tell()

        try:
            packet_length = VarInt.decode(self.bytes_io)
        except EOFError:
            return self.END, None
        except ValueError:
            return self.UNFINISHED, None

        try:
            if self.compression_threshold < 0:
                # 未压缩
                packet_id = VarInt.decode(self.bytes_io)
                data_length = packet_length.value - 1  # Packet_id Max Size is 1 for protocol 769
                data = self.bytes_io.read(data_length)

                # 传输未完成
                if len(data) != data_length:
                    return self.UNFINISHED, None

            else:
                # 压缩
                data_length = VarInt.decode(self.bytes_io)

                if data_length.value == 0:
                    # 未压缩，Size < threshold
                    packet_id = VarInt.decode(self.bytes_io)
                    _data_length = packet_length.value - 2  # (1 data_length of (0) + 1 packet_id < 127)
                    data = self.bytes_io.read(_data_length)

                    # 传输未完成
                    if len(data) != _data_length:
                        return self.UNFINISHED, None
                else:
                    # 压缩 Size >= threshold

                    compressed_data_length = packet_length.value - VarInt.size(data_length)

                    compressed_data = self.bytes_io.read(compressed_data_length)

                    # 传输未完成
                    if len(compressed_data) != compressed_data_length:
                        return self.UNFINISHED, None

                    _data_io = BytesIO(zlib.decompress(compressed_data))
                    packet_id = VarInt.decode(_data_io)
                    data = _data_io.read()

            move = self.bytes_io.tell() - loc
            self.bytes_io.seek(-move, os.SEEK_CUR)

            return self.SUCCESS, DataPacket(
            packet_length.value, self.bound_to, packet_id.value, data, self.bytes_io.read(move)
            )

        except (EOFError, zlib.error):
            # 解析 Packet 错误 bytes未传输完成
            return self.UNFINISHED, None

    def decode(self, raw_bytes: bytes) -> Iterable[DataPacket] | None:
        """
            解析数据流
        :param raw_bytes:
        :return:
        """
        # 写入bytes_io
        self.bytes_io.write(raw_bytes)

        # 指针返回初始位置
        self.bytes_io.seek(self.last_pos, os.SEEK_SET)

        # 循环读取至流尾端
        while True:
            flag, data_packet = self.decode_a_packet()
            if flag == self.END:
                # 指针归零 新BytesIO
                self.last_pos = 0
                self.bytes_io = BytesIO()
                break

            elif flag == self.UNFINISHED:
                # 当前流未完成，等待继续写入
                break

            elif flag == self.SUCCESS:
                # 更新指针位置
                self.last_pos = self.bytes_io.tell()
                yield data_packet

        return None

    def encode(self, data_packet: DataPacket) -> bytes:
        """
            编码
        :param data_packet:
        :return:
        """
        bs = data_packet.to_raw_bytes()
        if self.compression_threshold >= 0:
            if len(bs) < self.compression_threshold:
                bs = b'\x00' + bs
            else:
                bs = VarInt.encode(len(bs)) + zlib.compress(bs)
        return VarInt.encode(len(bs)) + bs

    @classmethod
    def encode_by_threshold(cls, compression_threshold: int, data_packet: DataPacket) -> bytes:
        """
            通过 threshold 编码
        :param compression_threshold:
        :param data_packet:
        :return:
        """
        bs = data_packet.to_raw_bytes()
        if compression_threshold >= 0:
            if len(bs) < compression_threshold:
                bs = b'\x00' + bs
            else:
                bs = VarInt.encode(len(bs)) + zlib.compress(bs)
        return VarInt.encode(len(bs)) + bs


@dataclass(slots=True)
class Packet(Combined):
    """
        Protocol Packet
    """
    RESOURCE: ClassVar[str]
    PACKET_ID_HEX: ClassVar[int] = -1
    STATUS: ClassVar[Enums.Status]
    BOUND_TO: ClassVar[Enums.BoundTo]

    def __hash__(self):
        return self.PACKET_ID_HEX

    def __repr__(self):
        return f"<0x{self.PACKET_ID_HEX:>02x} {self.__class__.__name__}?>"

    @property
    def data_packet(self) -> DataPacket:
        """
            Packet -> DataPacket
        :return:
        """
        data = self.__bytes__()
        return DataPacket(len(data), self.BOUND_TO, self.PACKET_ID_HEX, data)

    @classmethod
    def one(cls, *args, **kwargs) -> Self:
        """
            糖函数，快速生成一个随机Packet，需重写以定义
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()
