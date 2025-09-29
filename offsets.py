"""
CS2 Memory Offsets - Updated for latest version
These offsets are for educational purposes only
"""

# Client.dll offsets
class ClientOffsets:
    # Entity list
    dwEntityList = 0x19BBCC8
    
    # Local player
    dwLocalPlayerPawn = 0x1831D28
    
    # View matrix for world to screen conversion
    dwViewMatrix = 0x1A1E580
    
    # Game rules
    dwGameRules = 0x1A10B48
    
    # Plant bomb sites
    dwPlantedC4 = 0x1A18B38

# Server.dll offsets  
class ServerOffsets:
    pass

# Entity offsets
class EntityOffsets:
    # Player controller offsets
    m_hPlayerPawn = 0x7EC
    m_sSanitizedPlayerName = 0x770
    m_iPawnHealth = 0x334
    m_iPawnArmor = 0x2344
    m_bPawnIsAlive = 0x834
    
    # Pawn offsets
    m_vOldOrigin = 0x1324
    m_vecViewOffset = 0xCB0
    m_iTeamNum = 0x3E3
    m_lifeState = 0x348
    m_hOwnerEntity = 0x440
    m_MoveType = 0x32C
    m_vecOrigin = 0x1268
    m_modelState = 0x170
    
    # Bone matrix
    m_pGameSceneNode = 0x328
    m_boneArray = 0x1E0

# Netvars
class NetVars:
    m_iHealth = 0x334
    m_vecOrigin = 0x1268  
    m_iTeamNum = 0x3E3
    m_lifeState = 0x348
    m_fFlags = 0x3EC
    m_vecViewOffset = 0xCB0
    
# Map bounds for different CS2 maps
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
    'de_cache': {
        'x_min': -2000, 'x_max': 3250,
        'y_min': -2700, 'y_max': 1100
    }
}