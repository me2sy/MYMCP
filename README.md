# MYMCP V0.1.2

## MY Minecraft Protocols/Proxy

Encode and decode the protocols of Minecraft (Java Edition) version 1.21.4 in Python. (>90%)

With a demo proxy server and a demo client/player.

More Protocol Details see [wiki.vg](https://minecraft.wiki/w/Java_Edition_protocol)


## Install
`pip install mymcp`

and enjoy.

## How To Set Up a Proxy Server
1. Set up a [**minecraft server**](https://www.minecraft.net/en-us/download/server) (java edition) with version 1.21.4 
2. Set **online-mode=false** in **server.propertie** then start the server
3. Create your own probe and run
```python
from mymcp.protocols import *
from mymcp.protocols import ProtocolEnum as PE
from mymcp.proxy import Probe, Proxy


class MyProbe(Probe):
    """
        Probe Demo
    """
    def play_protocol(self, direct: PE.Direction, protocol_cls, data_packet: DataPacket):
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

## How To Use Client / Player To make a Robot/AI
1. Just Create a Player and a Client
```python
import uuid
from mymcp.client import Player, Client
Client.run(
    Player('robot', uuid.uuid4()), 
    'minecraft_server_host'
)
```
2. A player named `robot` will join the server
3. say `hi` to him and he will stare at you maybe ;)


## DECLARE

This project is intended for educational purposes (graphics, sound, AI training, etc.) or just for fun.

**ATTENTION PLEASE:**

**NEVER** use this project for illegal or criminal activities.

The author and this project are not responsible for any related consequences resulting from the above usage, and you should use it at your own discretion.
