# -*- coding: utf-8 -*-
"""
    enums
    ~~~~~~~~~~~~~~~~~~
    
    Log:
        2025-05-30 0.2.0 Me2sY  重构，用于未来区分版本

        2025-05-23 0.1.0 Me2sY 创建
"""

__author__ = 'Me2sY'
__version__ = '0.2.0'

__all__ = [
    'Enums',
    'V769'
]

from enum import Enum, IntEnum


class Enums:
    class Transport(IntEnum):
        CS = 0
        SC = 1
        CP = 0
        SP = 1

    class BoundTo(IntEnum):
        CLIENT = 0
        SERVER = 1

    class Status(IntEnum):
        """
            当前状态
        """
        HANDSHAKING = 0
        STATUS = 1
        LOGIN = 2
        CONFIGURATION = 3
        PLAY = 4

    class Dimension(IntEnum):
        """
            维度
        """
        OVERWORLD = 0
        THE_END = 1
        THE_NETHER = 3

    class DimensionChunkHeight(Enum):
        """
            维度高度
        """
        OVERWORLD = 24
        THE_NETHER = 16
        THE_END = 16

    class HandShaking(Enum):
        """
            HandShaking Next Status
        """
        STATUS = 1
        LOGIN = 2
        TRANSFER = 3

    class Hand(Enum):
        """
            Hand Type
        """
        MAIN = 0
        OFF = 1

    class Difficulty(Enum):
        """
            difficulty level
        """
        PEACEFUL = 0
        EASY = 1
        NORMAL = 2
        HARD = 3

    class TeleportFlags(Enum):
        """
           A bit field represented as an Int, specifying how a teleportation is to be applied on each axis.
           In the lower 8 bits of the bit field,
           a set bit means the teleportation on the corresponding axis is relative,
           and an unset bit that it is absolute.
        """
        x = 0x0001
        y = 0x0002
        z = 0x0004
        yaw = 0x0008
        pitch = 0x0010
        velocity_x = 0x0020
        velocity_y = 0x0040
        velocity_z = 0x0080

    class ClientStatusAction(Enum):
        """
            0x04 play CS
        """
        PERFORM_RESPAWN = 0
        REQUEST_STATS = 1

    class ClientSettingsChatMode(Enum):
        """
            0x05 play CS
        """
        ENABLED = 0
        COMMANDS_ONLY = 1
        HIDDEN = 2

    class InteractEntityType(Enum):
        """
            0x0d play CS
        """
        INTERACT = 0
        ATTACK = 1
        INTERACT_AT = 2

    class PlayerAction(Enum):
        """
            Digging
        """
        START_DIGGING = 0
        CANCELLED_DIGGING = 1
        FINISHED_DIGGING = 2
        DROP_ITEM_STACK = 3
        DROP_ITEM = 4
        SHOOT_ARROW__FINISH_EATING = 5
        SWAP_ITEM_IN_HAND = 6

    class EntityAction(Enum):
        """
            Sent by the client to indicate that it has performed certain actions:
            sneaking (crouching), sprinting, exiting a bed,
            jumping with a horse, and opening a horse's inventory while riding it.
        """
        START_SNEAKING = 0
        STOP_SNEAKING = 1
        LEAVE_BED = 2
        START_SPRINTING = 3
        STOP_SPRINTING = 4
        START_JUMP_WITH_HORSE = 5
        STOP_JUMP_WITH_HORSE = 6
        OPEN_HORSE_INVENTORY = 7
        START_FLYING_WITH_ELYTRA = 8

    class BookId(Enum):
        CRAFTING = 0
        FURNACE = 1
        BLAST_FURNACE = 2
        SMOKER = 3

    class ResourcePackStatus(Enum):
        SUCCESSFULLY_LOADED = 0
        DECLINED = 1
        FAILED_DOWNLOAD = 2
        ACCEPTED = 3
        DOWNLOADED = 4
        INVALID_URL = 5
        FAILED_TO_RELOAD = 6
        DISCARDED = 7

    class AdvancementTab(IntEnum):
        OPEN_TAB = 0
        CLOSED_SCREEN = 1

    class CommandBlockMode(Enum):
        SEQUENCE = 0
        AUTO = 1
        REDSTONE = 2

    class StructureBlockAction(Enum):
        UPDATE_DATA = 0
        SAVE_THE_STRUCTURE = 1
        LOAD_THE_STRUCTURE = 2
        DETECT_SIZE = 3

    class StructureBlockMode(Enum):
        SAVE = 0
        LOAD = 1
        CORNER = 2
        DATA = 3

    class StructureBlockMirror(Enum):
        NONE = 0
        LEFT_RIGHT = 1
        FRONT_BACK = 2

    class StructureBlockRotation(Enum):
        NONE = 0
        CLOCKWISE_90 = 1
        CLOCKWISE_180 = 2
        COUNTERCLOCKWISE_90 = 3

    class Face(Enum):
        """
            Face direction
        """
        BOTTOM = 0
        TOP = 1
        NORTH = 2
        SOUTH = 3
        WEST = 4
        EAST = 5

    class Color(Enum):
        """
            Color
        """
        PINK = 0
        BLUE = 1
        RED = 2
        GREEN = 3
        YELLOW = 4
        PURPLE = 5
        WHITE = 6

    class Division(Enum):
        NO_DIVISION = 0
        NOTCHES_6 = 1
        NOTCHES_10 = 2
        NOTCHES_12 = 3
        NOTCHES_20 = 4

    class SpawnPaintingDirection(Enum):
        SOUTH = 0
        WEST = 1
        NORTH = 2
        EAST = 3

    class SculkVibrationSignalIdentifier(Enum):
        BLOCK = 'block'
        ENTITY = 'entity'

    class EntityAnimation(Enum):
        SWING_MAIN_ARM = 0
        TAKE_DAMAGE = 1
        LEAVE_BED = 2
        SWING_OFFHAND = 3
        CRITICAL_EFFECT = 4
        MAGIC_CRITICAL_EFFECT = 5

    class DiggingStatusServer(Enum):
        """
            Digging for Server
        """
        START_DIGGING = 0
        CANCELLED_DIGGING = 1
        FINISHED_DIGGING = 2

    class BlockEntityDataAction(Enum):
        SET_DATA_OF_A_MOB_SPAWNER = 1
        SET_COMMAND_BLOCK_TEXT = 2
        SET_THE_LEVEL = 3
        SET_ROTATION_AND_SKIN_OF_MOB_HEAD = 4
        DECLARE_A_CONDUIT = 5
        SET_BASE_COLOR = 6
        SET_THE_DATA_FOR_A_STRUCTURE_TILE_ENTITY = 7
        SET_THE_DESTINATION_FOR_A_END_GATEWAY = 8
        SET_THE_TEXT_ON_A_SIGN = 9
        DECLARE_A_BED = 11
        SET_DATA_OF_A_JIGSAW_BLOCK = 12
        SET_ITEMS_IN_A_CAMPFIRE = 13
        BEEHIVE_INFORMATION = 14

    class ChatMessagePosition(Enum):
        CHAT_BOX = 0
        SYSTEM_MESSAGE = 1
        GAME_INFO = 2

    class BossBarAction(Enum):
        ADD = 0
        REMOVE = 1
        UPDATE_HEALTH = 2
        UPDATE_TITLE = 3
        UPDATE_STYLE = 4
        UPDATE_FLAGS = 5

    class UpdateScoreAction(IntEnum):
        CREATE = 0
        REMOVE = 1
        UPDATE = 2

    class UpdateTeamsMethod(IntEnum):
        CREATE_TEAM = 0
        REMOVE_TEAM = 1
        UPDATE_TEAM_INFO = 2
        ADD_ENTITIES_TO_TEAM = 3
        REMOVE_ENTITIES_FROM_TEAM = 4

    class SoundCategory(IntEnum):
        MASTER = 0
        MUSIC = 1
        RECORD = 2
        WEATHER = 3
        BLOCK = 4
        HOSTILE = 5
        NEUTRAL = 6
        PLAYER = 7
        AMBIENT = 8
        VOICE = 9

    class GameMode(Enum):
        SURVIVAL = 0
        CREATIVE = 1
        ADVENTURE = 2
        SPECTATOR = 3

    class UnlockRecipesAction(Enum):
        INIT = 0
        ADD = 1
        REMOVE = 2

    class PlayerInfo(Enum):
        ADD_PLAYER = 0
        UPDATE_GAMEMODE = 1
        UPDATE_LATENCY = 2
        UPDATE_DISPLAY_NAME = 3
        REMOVE_PLAYER = 4

    class FacePlayer(Enum):
        FEET = 0
        EYES = 1

    class InteractType(Enum):
        INTERACT = 0
        ATTACH = 1
        INTERACT_AT = 2

    class PlayerInput(Enum):
        FORWARD = 0x01
        BACKWARD = 0x02
        LEFT = 0x04
        RIGHT = 0x08
        JUMP = 0x10
        SNEAK = 0x20
        SPRINT = 0x40

    class EntityType(IntEnum):
        """
            All Entity in protocol 769
        """
        # Acacia Boat
        AcaciaBoat = 0

        # Acacia Boat with Chest
        AcaciaChestBoat = 1

        # Allay
        Allay = 2

        # Area Effect Cloud
        AreaEffectCloud = 3

        # Armadillo
        Armadillo = 4

        # Armor Stand
        ArmorStand = 5

        # Arrow
        Arrow = 6

        # Axolotl
        Axolotl = 7

        # Bamboo Raft with Chest
        BambooChestRaft = 8

        # Bamboo Raft
        BambooRaft = 9

        # Bat
        Bat = 10

        # Bee
        Bee = 11

        # Birch Boat
        BirchBoat = 12

        # Birch Boat with Chest
        BirchChestBoat = 13

        # Blaze
        Blaze = 14

        # Block Display
        BlockDisplay = 15

        # Bogged
        Bogged = 16

        # Breeze
        Breeze = 17

        # Wind Charge
        BreezeWindCharge = 18

        # Camel
        Camel = 19

        # Cat
        Cat = 20

        # Cave Spider
        CaveSpider = 21

        # Cherry Boat
        CherryBoat = 22

        # Cherry Boat with Chest
        CherryChestBoat = 23

        # Minecart with Chest
        ChestMinecart = 24

        # Chicken
        Chicken = 25

        # Cod
        Cod = 26

        # Minecart with Command Block
        CommandBlockMinecart = 27

        # Cow
        Cow = 28

        # Creaking
        Creaking = 29

        # Creeper
        Creeper = 30

        # Dark Oak Boat
        DarkOakBoat = 31

        # Dark Oak Boat with Chest
        DarkOakChestBoat = 32

        # Dolphin
        Dolphin = 33

        # Donkey
        Donkey = 34

        # Dragon Fireball
        DragonFireball = 35

        # Drowned
        Drowned = 36

        # Thrown Egg
        Egg = 37

        # Elder Guardian
        ElderGuardian = 38

        # Enderman
        Enderman = 39

        # Endermite
        Endermite = 40

        # Ender Dragon
        EnderDragon = 41

        # Thrown Ender Pearl
        EnderPearl = 42

        # End Crystal
        EndCrystal = 43

        # Evoker
        Evoker = 44

        # Evoker Fangs
        EvokerFangs = 45

        # Thrown Bottle o' Enchanting
        ExperienceBottle = 46

        # Experience Orb
        ExperienceOrb = 47

        # Eye of Ender
        EyeOfEnder = 48

        # Falling Block
        FallingBlock = 49

        # Fireball
        Fireball = 50

        # Firework Rocket
        FireworkRocket = 51

        # Fox
        Fox = 52

        # Frog
        Frog = 53

        # Minecart with Furnace
        FurnaceMinecart = 54

        # Ghast
        Ghast = 55

        # Giant
        Giant = 56

        # Glow Item Frame
        GlowItemFrame = 57

        # Glow Squid
        GlowSquid = 58

        # Goat
        Goat = 59

        # Guardian
        Guardian = 60

        # Hoglin
        Hoglin = 61

        # Minecart with Hopper
        HopperMinecart = 62

        # Horse
        Horse = 63

        # Husk
        Husk = 64

        # Illusioner
        Illusioner = 65

        # Interaction
        Interaction = 66

        # Iron Golem
        IronGolem = 67

        # Item
        Item = 68

        # Item Display
        ItemDisplay = 69

        # Item Frame
        ItemFrame = 70

        # Jungle Boat
        JungleBoat = 71

        # Jungle Boat with Chest
        JungleChestBoat = 72

        # Leash Knot
        LeashKnot = 73

        # Lightning Bolt
        LightningBolt = 74

        # Llama
        Llama = 75

        # Llama Spit
        LlamaSpit = 76

        # Magma Cube
        MagmaCube = 77

        # Mangrove Boat
        MangroveBoat = 78

        # Mangrove Boat with Chest
        MangroveChestBoat = 79

        # Marker
        Marker = 80

        # Minecart
        Minecart = 81

        # Mooshroom
        Mooshroom = 82

        # Mule
        Mule = 83

        # Oak Boat
        OakBoat = 84

        # Oak Boat with Chest
        OakChestBoat = 85

        # Ocelot
        Ocelot = 86

        # Ominous Item Spawner
        OminousItemSpawner = 87

        # Painting
        Painting = 88

        # Pale Oak Boat
        PaleOakBoat = 89

        # Pale Oak Boat with Chest
        PaleOakChestBoat = 90

        # Panda
        Panda = 91

        # Parrot
        Parrot = 92

        # Phantom
        Phantom = 93

        # Pig
        Pig = 94

        # Piglin
        Piglin = 95

        # Piglin Brute
        PiglinBrute = 96

        # Pillager
        Pillager = 97

        # Polar Bear
        PolarBear = 98

        # Potion
        Potion = 99

        # Pufferfish
        Pufferfish = 100

        # Rabbit
        Rabbit = 101

        # Ravager
        Ravager = 102

        # Salmon
        Salmon = 103

        # Sheep
        Sheep = 104

        # Shulker
        Shulker = 105

        # Shulker Bullet
        ShulkerBullet = 106

        # Silverfish
        Silverfish = 107

        # Skeleton
        Skeleton = 108

        # Skeleton Horse
        SkeletonHorse = 109

        # Slime
        Slime = 110

        # Small Fireball
        SmallFireball = 111

        # Sniffer
        Sniffer = 112

        # Snowball
        Snowball = 113

        # Snow Golem
        SnowGolem = 114

        # Minecart with Monster Spawner
        SpawnerMinecart = 115

        # Spectral Arrow
        SpectralArrow = 116

        # Spider
        Spider = 117

        # Spruce Boat
        SpruceBoat = 118

        # Spruce Boat with Chest
        SpruceChestBoat = 119

        # Squid
        Squid = 120

        # Stray
        Stray = 121

        # Strider
        Strider = 122

        # Tadpole
        Tadpole = 123

        # Text Display
        TextDisplay = 124

        # Primed TNT
        Tnt = 125

        # Minecart with TNT
        TntMinecart = 126

        # Trader Llama
        TraderLlama = 127

        # Trident
        Trident = 128

        # Tropical Fish
        TropicalFish = 129

        # Turtle
        Turtle = 130

        # Vex
        Vex = 131

        # Villager
        Villager = 132

        # Vindicator
        Vindicator = 133

        # Wandering Trader
        WanderingTrader = 134

        # Warden
        Warden = 135

        # Wind Charge
        WindCharge = 136

        # Witch
        Witch = 137

        # Wither
        Wither = 138

        # Wither Skeleton
        WitherSkeleton = 139

        # Wither Skull
        WitherSkull = 140

        # Wolf
        Wolf = 141

        # Zoglin
        Zoglin = 142

        # Zombie
        Zombie = 143

        # Zombie Horse
        ZombieHorse = 144

        # Zombie Villager
        ZombieVillager = 145

        # Zombified Piglin
        ZombifiedPiglin = 146

        # Player
        Player = 147

        # Fishing Bobber
        FishingBobber = 148


    EntityTypeMap = {
        item.value: item.name for item in EntityType
    }


    class VillagerTypes(IntEnum):
        DESERT = 0
        JUNGLE = 1
        PLAINS = 2
        SAVANNA = 3
        SNOW = 4
        SWAMP = 5
        TAIGA = 6


    class VillagerProfessions(IntEnum):
        NONE = 0
        ARMORER = 1
        BUTCHER = 2
        CARTOGRAPHER = 3
        CLIERIC = 4
        FARMER = 5
        FISHERMAN = 6
        FLETCHER = 7
        LEATHERWORKER = 8
        LIBRARIAN = 9
        MASON = 10
        NITWIT = 11
        SHEPHERD = 12
        TOOLSMITH = 13
        WEAPONSMITH = 14


    class ParticleEnum(IntEnum):
        """
            https://minecraft.wiki/w/Java_Edition_protocol/Particles
            Particles Enum
        """
        ANGRY_VILLAGER = 0
        BLOCK = 1
        BLOCK_MARKER = 2
        BUBBLE = 3
        CLOUD = 4
        CRIT = 5
        DAMAGE_INDICATOR = 6
        DRAGON_BREATH = 7
        DRIPPING_LAVA = 8
        FALLING_LAVA = 9
        LANDING_LAVA = 10
        DRIPPING_WATER = 11
        FALLING_WATER = 12
        DUST = 13
        DUST_COLOR_TRANSITION = 14
        EFFECT = 15
        ELDER_GUARDIAN = 16
        ENCHANTED_HIT = 17
        ENCHANT = 18
        END_ROD = 19
        ENTITY_EFFECT = 20
        EXPLOSION_EMITTER = 21
        EXPLOSION = 22
        GUST = 23
        SMALL_GUST = 24
        GUST_EMITTER_LARGE = 25
        GUST_EMITTER_SMALL = 26
        SONIC_BOOM = 27
        FALLING_DUST = 28
        FIREWORK = 29
        FISHING = 30
        FLAME = 31
        INFESTED = 32
        CHERRY_LEAVES = 33
        PALE_OAK_LEAVES = 34
        SCULK_SOUL = 35
        SCULK_CHARGE = 36
        SCULK_CHARGE_POP = 37
        SOUL_FIRE_FLAME = 38
        SOUL = 39
        FLASH = 40
        HAPPY_VILLAGER = 41
        COMPOSTER = 42
        HEART = 43
        INSTANT_EFFECT = 44
        ITEM = 45
        VIBRATION = 46
        TRAIL = 47
        ITEM_SLIME = 48
        ITEM_COBWEB = 49
        ITEM_SNOWBALL = 50
        LARGE_SMOKE = 51
        LAVA = 52
        MYCELIUM = 53
        NOTE = 54
        POOF = 55
        PORTAL = 56
        RAIN = 57
        SMOKE = 58
        WHITE_SMOKE = 59
        SNEEZE = 60
        SPIT = 61
        SQUID_INK = 62
        SWEEP_ATTACK = 63
        TOTEM_OF_UNDYING = 64
        UNDERWATER = 65
        SPLASH = 66
        WITCH = 67
        BUBBLE_POP = 68
        CURRENT_DOWN = 69
        BUBBLE_COLUMN_UP = 70
        NAUTILUS = 71
        DOLPHIN = 72
        CAMPFIRE_COSY_SMOKE = 73
        CAMPFIRE_SIGNAL_SMOKE = 74
        DRIPPING_HONEY = 75
        FALLING_HONEY = 76
        LANDING_HONEY = 77
        FALLING_NECTAR = 78
        FALLING_SPORE_BLOSSOM = 79
        ASH = 80
        CRIMSON_SPORE = 81
        WARPED_SPORE = 82
        SPORE_BLOSSOM_AIR = 83
        DRIPPING_OBSIDIAN_TEAR = 84
        FALLING_OBSIDIAN_TEAR = 85
        LANDING_OBSIDIAN_TEAR = 86
        REVERSE_PORTAL = 87
        WHITE_ASH = 88
        SMALL_FLAME = 89
        SNOWFLAKE = 90
        DRIPPING_DRIPSTONE_LAVA = 91
        FALLING_DRIPSTONE_LAVA = 92
        DRIPPING_DRIPSTONE_WATER = 93
        FALLING_DRIPSTONE_WATER = 94
        GLOW_SQUID_INK = 95
        GLOW = 96
        WAX_ON = 97
        WAX_OFF = 98
        ELECTRIC_SPARK = 99
        SCRAPE = 100
        SHRIEK = 101
        EGG_CRACK = 102
        DUST_PLUME = 103
        TRIAL_SPAWNER_DETECTION = 104
        TRIAL_SPAWNER_DETECTION_OMINOUS = 105
        VAULT_CONNECTION = 106
        DUST_PILLAR = 107
        OMINOUS_SPAWNING = 108
        RAID_OMEN = 109
        TRIAL_OMEN = 110
        BLOCK_CRUMBLE = 111

        @property
        def minecraft_name(self):
            return 'minecraft:' + self.name.lower()

    class ParticleStatus(IntEnum):
        ALL = 0
        DECREASED = 1
        MINIMAL = 2


class V769(Enums): ...