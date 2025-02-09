# MYMCP V0.1.1

## MY Minecraft Protocols/Proxy

Encode and decode the protocols of Minecraft (Java Edition) version 1.21.4 in Python. (>90%)

A demo proxy server has been provided.

More Details see [wiki.vg](https://minecraft.wiki/w/Java_Edition_protocol)


## Install
`pip install mymcp`

[twisted](https://twisted.org) is need when use proxy server.

`pip install twisted`

## HowTo
1. Set up a [**minecraft server**](https://www.minecraft.net/en-us/download/server) (java edition) with version 1.21.4 
2. Set **online-mode=false** in **server.propertie** then start the server
3. Install `twisted` before run proxy server
4. Create your own probe and run
```python
from mymcp.protocols import *
from mymcp.protocols import ProtocolEnum as PE
from mymcp.proxy import Probe, Proxy


class MyProbe(Probe):
    """
        Probe Demo
    """
    def play_protocol(self, direct, protocol_cls, data_packet: DataPacket):
        # Create a protocol filter
        if protocol_cls not in (
                PlayProtocols.Client2Server.CSPlayChatMessage,
                PlayProtocols.Server2Client.SCPlayPlayerChatMessage
        ):
            return

        # Do what you want
        print(f"{protocol_cls.__name__:<30} > {protocol_cls.decode(data_packet.bytes_io())}")

# Start A Proxy Server
Proxy(server_host='minecraft_server_host', server_port=25565, proxy_port=25566, probe_cls=MyProbe).run()

```
5. Open a minecraft client, connect to 127.0.0.1:25566 (_proxy_port_ your set before)
6. Say something, and you will see the data in console (ChatMessage Protocol)


## DECLARE

This project is intended for educational purposes (graphics, sound, AI training, etc.) or just for fun.

**ATTENTION PLEASE:**

**NEVER** use this project for illegal or criminal activities.

The author and this project are not responsible for any related consequences resulting from the above usage, and you should use it at your own discretion.
