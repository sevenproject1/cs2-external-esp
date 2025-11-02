"""
CS2 Memory Offsets - ????????? ?? ?????? 20230584
?????????? ??????? ?? a2x/cs2-dumper
"""

# Client.dll offsets (?????????? ?? 2025-11-02)
class ClientOffsets:
    # Entity list
    dwEntityList = 0x1D0C978  # 30460408
    
    # Local player
    dwLocalPlayerPawn = 0x1BE3C20  # 29261216
    dwLocalPlayerController = 0x1E10070  # 31549552
    
    # View matrix for world to screen conversion
    dwViewMatrix = 0x1E2A740  # 31633088
    
    # Game rules
    dwGameRules = 0x1E1EE00  # 31629440
    
    # Plant bomb sites
    dwPlantedC4 = 0x1E2A960  # 31654752
    
    # Input
    dwCSGOInput = 0x1E35010  # 31673744
    
    # View angles
    dwViewAngles = 0x1E356C0  # 31675456

# Server.dll offsets  
class ServerOffsets:
    pass

# Entity offsets (?????????? ??? C_BaseEntity ? ???????????)
class EntityOffsets:
    # Player controller offsets
    m_hPlayerPawn = 0x80C  # 2060
    m_sSanitizedPlayerName = 0x778  # 1912
    m_iPawnHealth = 0x344  # 836
    m_iPawnArmor = 0x2348  # 9032
    m_bPawnIsAlive = 0x838  # 2104
    
    # Pawn offsets
    m_vOldOrigin = 0x1324  # 4900
    m_vecViewOffset = 0xCB8  # 3256
    m_iTeamNum = 0x3E3  # 995
    m_lifeState = 0x350  # 848
    m_hOwnerEntity = 0x448  # 1096
    m_MoveType = 0x334  # 820
    
    # Scene node and bone
    m_pGameSceneNode = 0x328  # 808
    m_modelState = 0x170  # 368
    m_boneArray = 0x1E0  # 480

# Netvars (?????????? ??????? ??? ????????? ?????)
class NetVars:
    # Health and team
    m_iHealth = 0x344  # 836
    m_iTeamNum = 0x3E3  # 995
    m_lifeState = 0x350  # 848
    
    # Position and view
    m_vecAbsOrigin = 0xD8  # 216 - absolute origin
    m_vecOrigin = 0x1324  # 4900 - old origin
    m_vecViewOffset = 0xCB8  # 3256
    
    # Flags and state
    m_fFlags = 0x3EC  # 1004
    m_bSpottedByMask = 0x1800  # 6144
    
    # Weapon and inventory
    m_hActiveWeapon = 0x1400  # 5120
    m_iItemDefinitionIndex = 0x1F4  # 500
    
    # Armor
    m_ArmorValue = 0x2418  # 9240

# Map bounds ??? ?????? ???? CS2
MAP_BOUNDS = {
    'de_dust2': {
        'x_min': -2476, 'x_max': 1800,
        'y_min': -2032, 'y_max': 3239
    },
    'de_mirage': {
        'x_min': -3217, 'x_max': 1912,
        'y_min': -3401, 'y_max': 1682
    },
    'de_inferno': {
        'x_min': -2087, 'x_max': 3870,
        'y_min': -3870, 'y_max': 1344
    },
    'de_nuke': {
        'x_min': -3584, 'x_max': 3840,
        'y_min': -3840, 'y_max': 4096
    },
    'de_overpass': {
        'x_min': -4831, 'x_max': 1663,
        'y_min': -3500, 'y_max': 2064
    },
    'de_ancient': {
        'x_min': -2953, 'x_max': 2655,
        'y_min': -2633, 'y_max': 2624
    },
    'de_anubis': {
        'x_min': -2796, 'x_max': 3260,
        'y_min': -3542, 'y_max': 2214
    }
}

# Bone IDs ??? ???????
class BoneIds:
    HEAD = 6
    NECK = 5
    CHEST = 4
    PELVIS = 0
    LEFT_SHOULDER = 8
    LEFT_ELBOW = 9
    LEFT_HAND = 10
    RIGHT_SHOULDER = 13
    RIGHT_ELBOW = 14
    RIGHT_HAND = 15
    LEFT_HIP = 22
    LEFT_KNEE = 23
    LEFT_FOOT = 24
    RIGHT_HIP = 25
    RIGHT_KNEE = 26
    RIGHT_FOOT = 27
