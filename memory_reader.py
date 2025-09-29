"""
CS2 Memory Reader
Handles reading game memory for radar functionality
"""

import pymem
import pymem.process
import psutil
import struct
import time
from typing import Optional, List, Tuple
from offsets import ClientOffsets, EntityOffsets, NetVars

class CS2MemoryReader:
    def __init__(self):
        self.process = None
        self.client_dll = None
        self.server_dll = None
        self.connected = False
        
    def connect_to_cs2(self) -> bool:
        """Connect to CS2 process"""
        try:
            # Find CS2 process
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in ['cs2.exe', 'cs2']:
                    try:
                        self.process = pymem.Pymem(proc.info['pid'])
                        print(f"Connected to CS2 process (PID: {proc.info['pid']})")
                        break
                    except Exception as e:
                        print(f"Failed to connect to process {proc.info['pid']}: {e}")
                        continue
            
            if not self.process:
                print("CS2 process not found!")
                return False
            
            # Get module addresses
            try:
                self.client_dll = pymem.process.module_from_name(self.process.process_handle, "client.dll").lpBaseOfDll
                print(f"client.dll base address: 0x{self.client_dll:X}")
            except Exception as e:
                print(f"Failed to get client.dll: {e}")
                return False
                
            try:
                self.server_dll = pymem.process.module_from_name(self.process.process_handle, "server.dll").lpBaseOfDll
                print(f"server.dll base address: 0x{self.server_dll:X}")
            except Exception as e:
                print(f"Failed to get server.dll: {e}")
                # server.dll might not be needed for basic radar
                pass
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Error connecting to CS2: {e}")
            return False
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from process"""
        if not self.connected or not self.process:
            return None
            
        try:
            return self.process.read_bytes(address, size)
        except Exception as e:
            print(f"Memory read error at 0x{address:X}: {e}")
            return None
    
    def read_int(self, address: int) -> Optional[int]:
        """Read 4-byte integer from memory"""
        data = self.read_memory(address, 4)
        if data:
            return struct.unpack('<I', data)[0]
        return None
    
    def read_float(self, address: int) -> Optional[float]:
        """Read 4-byte float from memory"""
        data = self.read_memory(address, 4)
        if data:
            return struct.unpack('<f', data)[0]
        return None
    
    def read_vec3(self, address: int) -> Optional[Tuple[float, float, float]]:
        """Read 3D vector (12 bytes) from memory"""
        data = self.read_memory(address, 12)
        if data:
            return struct.unpack('<fff', data)
        return None
    
    def read_string(self, address: int, length: int = 64) -> Optional[str]:
        """Read string from memory"""
        data = self.read_memory(address, length)
        if data:
            try:
                return data.decode('utf-8').rstrip('\x00')
            except:
                return data.decode('utf-8', errors='ignore').rstrip('\x00')
        return None
    
    def get_local_player(self) -> Optional[int]:
        """Get local player pawn address"""
        if not self.connected:
            return None
            
        local_player_pawn = self.read_int(self.client_dll + ClientOffsets.dwLocalPlayerPawn)
        if local_player_pawn:
            return local_player_pawn
        return None
    
    def get_entity_list(self) -> List[int]:
        """Get list of entity addresses"""
        if not self.connected:
            return []
            
        entities = []
        entity_list_base = self.client_dll + ClientOffsets.dwEntityList
        
        # Read entity list (up to 64 entities)
        for i in range(64):
            try:
                entity_address = self.read_int(entity_list_base + (i * 0x78))
                if entity_address and entity_address != 0:
                    entities.append(entity_address)
            except:
                continue
                
        return entities
    
    def get_player_info(self, entity_address: int) -> Optional[dict]:
        """Get player information from entity"""
        if not entity_address:
            return None
            
        try:
            # Read basic player data
            origin = self.read_vec3(entity_address + NetVars.m_vecOrigin)
            health = self.read_int(entity_address + NetVars.m_iHealth)
            team = self.read_int(entity_address + NetVars.m_iTeamNum)
            life_state = self.read_int(entity_address + NetVars.m_lifeState)
            
            if not origin or health is None or team is None:
                return None
            
            # Check if player is alive
            is_alive = life_state == 0 and health > 0
            
            return {
                'address': entity_address,
                'origin': origin,
                'health': health,
                'team': team,
                'alive': is_alive,
                'x': origin[0],
                'y': origin[1],
                'z': origin[2]
            }
            
        except Exception as e:
            print(f"Error reading player info: {e}")
            return None
    
    def get_view_matrix(self) -> Optional[List[List[float]]]:
        """Get view matrix for world-to-screen conversion"""
        if not self.connected:
            return None
            
        try:
            matrix_data = self.read_memory(self.client_dll + ClientOffsets.dwViewMatrix, 64)
            if matrix_data:
                matrix = []
                for i in range(4):
                    row = struct.unpack('<ffff', matrix_data[i*16:(i+1)*16])
                    matrix.append(list(row))
                return matrix
        except Exception as e:
            print(f"Error reading view matrix: {e}")
            
        return None
    
    def disconnect(self):
        """Disconnect from CS2 process"""
        if self.process:
            try:
                self.process.close_handle()
            except:
                pass
        self.process = None
        self.client_dll = None
        self.server_dll = None
        self.connected = False
        print("Disconnected from CS2")