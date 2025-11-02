"""
CS2 ESP Memory Reader
??????????? reader ??? ?????? ?????? ? ?????????? ?????? ? view matrix
"""

import pymem
import pymem.process
import psutil
import struct
import ctypes
from typing import Optional, List, Tuple, Dict
from offsets_updated import ClientOffsets, EntityOffsets, NetVars, BoneIds

class Vector3:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z
    
    def __repr__(self):
        return f"Vector3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

class ViewMatrix:
    def __init__(self, matrix: List[List[float]]):
        self.matrix = matrix
    
    def world_to_screen(self, pos: Vector3, screen_width: int, screen_height: int) -> Optional[Tuple[int, int]]:
        """??????????? 3D ????????? ? 2D ???????? ??????????"""
        try:
            # View matrix transformation
            clip_x = pos.x * self.matrix[0][0] + pos.y * self.matrix[0][1] + pos.z * self.matrix[0][2] + self.matrix[0][3]
            clip_y = pos.x * self.matrix[1][0] + pos.y * self.matrix[1][1] + pos.z * self.matrix[1][2] + self.matrix[1][3]
            clip_w = pos.x * self.matrix[3][0] + pos.y * self.matrix[3][1] + pos.z * self.matrix[3][2] + self.matrix[3][3]
            
            if clip_w < 0.1:
                return None
            
            # Normalize device coordinates
            ndc_x = clip_x / clip_w
            ndc_y = clip_y / clip_w
            
            # Screen coordinates
            screen_x = (screen_width / 2) + (ndc_x * screen_width / 2)
            screen_y = (screen_height / 2) - (ndc_y * screen_height / 2)
            
            # Check if on screen
            if screen_x < 0 or screen_x > screen_width or screen_y < 0 or screen_y > screen_height:
                return None
            
            return (int(screen_x), int(screen_y))
        except:
            return None

class CS2ESPMemory:
    def __init__(self):
        self.process = None
        self.client_dll = None
        self.connected = False
        self.screen_width = 1920
        self.screen_height = 1080
        
    def connect_to_cs2(self) -> bool:
        """??????????? ? ???????? CS2"""
        try:
            # ????? ???????? CS2
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in ['cs2.exe', 'cs2']:
                    try:
                        self.process = pymem.Pymem(proc.info['pid'])
                        print(f"[+] ?????????? ? CS2 (PID: {proc.info['pid']})")
                        break
                    except Exception as e:
                        print(f"[-] ?? ??????? ???????????? ? ???????? {proc.info['pid']}: {e}")
                        continue
            
            if not self.process:
                print("[-] ??????? CS2 ?? ??????!")
                return False
            
            # ????????? ???????? ?????? client.dll
            try:
                self.client_dll = pymem.process.module_from_name(
                    self.process.process_handle, 
                    "client.dll"
                ).lpBaseOfDll
                print(f"[+] client.dll base: 0x{self.client_dll:X}")
            except Exception as e:
                print(f"[-] ?? ??????? ???????? client.dll: {e}")
                return False
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"[-] ?????? ??????????? ? CS2: {e}")
            return False
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """?????? ?????? ?? ????????"""
        if not self.connected or not self.process:
            return None
        try:
            return self.process.read_bytes(address, size)
        except:
            return None
    
    def read_int(self, address: int) -> Optional[int]:
        """?????? 4-????????? integer"""
        data = self.read_memory(address, 4)
        if data:
            return struct.unpack('<I', data)[0]
        return None
    
    def read_uint64(self, address: int) -> Optional[int]:
        """?????? 8-????????? integer"""
        data = self.read_memory(address, 8)
        if data:
            return struct.unpack('<Q', data)[0]
        return None
    
    def read_float(self, address: int) -> Optional[float]:
        """?????? 4-????????? float"""
        data = self.read_memory(address, 4)
        if data:
            return struct.unpack('<f', data)[0]
        return None
    
    def read_vec3(self, address: int) -> Optional[Vector3]:
        """?????? 3D ???????"""
        data = self.read_memory(address, 12)
        if data:
            x, y, z = struct.unpack('<fff', data)
            return Vector3(x, y, z)
        return None
    
    def read_string(self, address: int, length: int = 64) -> Optional[str]:
        """?????? ?????? ?? ??????"""
        data = self.read_memory(address, length)
        if data:
            try:
                return data.decode('utf-8').rstrip('\x00')
            except:
                return data.decode('utf-8', errors='ignore').rstrip('\x00')
        return None
    
    def get_view_matrix(self) -> Optional[ViewMatrix]:
        """????????? view matrix ??? world-to-screen"""
        if not self.connected:
            return None
        
        try:
            matrix_data = self.read_memory(self.client_dll + ClientOffsets.dwViewMatrix, 64)
            if matrix_data:
                matrix = []
                for i in range(4):
                    row = struct.unpack('<ffff', matrix_data[i*16:(i+1)*16])
                    matrix.append(list(row))
                return ViewMatrix(matrix)
        except Exception as e:
            pass
        return None
    
    def get_local_player_controller(self) -> Optional[int]:
        """????????? ?????? ?????????? ??????????? ??????"""
        if not self.connected:
            return None
        return self.read_uint64(self.client_dll + ClientOffsets.dwLocalPlayerController)
    
    def get_local_player_pawn(self) -> Optional[int]:
        """????????? ?????? ?????????? pawn ??????"""
        if not self.connected:
            return None
        return self.read_uint64(self.client_dll + ClientOffsets.dwLocalPlayerPawn)
    
    def get_entity_list_entry(self, index: int) -> Optional[int]:
        """????????? ?????? entity ?? ??????"""
        if not self.connected:
            return None
        
        try:
            entity_list = self.client_dll + ClientOffsets.dwEntityList
            
            # ?????? entity list entry
            list_entry = self.read_uint64(entity_list + (8 * (index & 0x7FFF) >> 9) + 16)
            if not list_entry:
                return None
            
            controller = self.read_uint64(list_entry + 120 * (index & 0x1FF))
            return controller
        except:
            return None
    
    def get_player_pawn_from_controller(self, controller_address: int) -> Optional[int]:
        """????????? pawn ?????? ?? controller"""
        if not controller_address:
            return None
        
        try:
            # ?????? m_hPlayerPawn
            pawn_handle = self.read_int(controller_address + EntityOffsets.m_hPlayerPawn)
            if not pawn_handle:
                return None
            
            # ???????? index ?? handle
            list_entry_index = pawn_handle & 0x7FFF
            
            # ???????? pawn ?? entity list
            entity_list = self.client_dll + ClientOffsets.dwEntityList
            list_entry = self.read_uint64(entity_list + 8 * (list_entry_index >> 9) + 16)
            
            if not list_entry:
                return None
            
            pawn_address = self.read_uint64(list_entry + 120 * (list_entry_index & 0x1FF))
            return pawn_address
        except:
            return None
    
    def get_bone_position(self, pawn_address: int, bone_id: int) -> Optional[Vector3]:
        """????????? ??????? ????? ??????"""
        if not pawn_address:
            return None
        
        try:
            # ???????? game scene node
            game_scene_node = self.read_uint64(pawn_address + EntityOffsets.m_pGameSceneNode)
            if not game_scene_node:
                return None
            
            # ???????? bone array
            bone_array = self.read_uint64(game_scene_node + EntityOffsets.m_boneArray)
            if not bone_array:
                return None
            
            # ?????? ??????? ????? (?????? ????? = 32 ?????)
            bone_pos = self.read_vec3(bone_array + bone_id * 32)
            return bone_pos
        except:
            return None
    
    def get_player_info(self, controller_address: int) -> Optional[Dict]:
        """????????? ?????? ?????????? ?? ??????"""
        if not controller_address:
            return None
        
        try:
            # ???????? pawn address
            pawn_address = self.get_player_pawn_from_controller(controller_address)
            if not pawn_address:
                return None
            
            # ?????? ??????? ??????????
            health = self.read_int(pawn_address + NetVars.m_iHealth)
            team = self.read_int(pawn_address + NetVars.m_iTeamNum)
            life_state = self.read_int(pawn_address + NetVars.m_lifeState)
            
            if health is None or team is None:
                return None
            
            # ???????? ?? ???????
            is_alive = life_state == 256 and health > 0
            
            if not is_alive:
                return None
            
            # ???????? ??? ??????
            name_address = controller_address + EntityOffsets.m_sSanitizedPlayerName
            player_name = self.read_string(name_address, 32)
            
            # ???????? ??????? ??????
            origin = self.read_vec3(pawn_address + NetVars.m_vecAbsOrigin)
            
            # ???????? ??????? ?????? ??? ???????
            head_pos = self.get_bone_position(pawn_address, BoneIds.HEAD)
            
            return {
                'controller_address': controller_address,
                'pawn_address': pawn_address,
                'health': health,
                'team': team,
                'alive': is_alive,
                'name': player_name or "Unknown",
                'origin': origin,
                'head_pos': head_pos
            }
            
        except Exception as e:
            return None
    
    def get_all_players(self) -> List[Dict]:
        """????????? ?????? ???? ???????"""
        players = []
        
        if not self.connected:
            return players
        
        # ???????? ????????? ???????
        local_controller = self.get_local_player_controller()
        local_team = None
        
        if local_controller:
            local_pawn = self.get_player_pawn_from_controller(local_controller)
            if local_pawn:
                local_team = self.read_int(local_pawn + NetVars.m_iTeamNum)
        
        # ?????????? ???? ??????? (???????? 64)
        for i in range(1, 65):
            try:
                controller = self.get_entity_list_entry(i)
                if not controller:
                    continue
                
                player_info = self.get_player_info(controller)
                if not player_info:
                    continue
                
                # ?????????? ?????
                player_info['is_enemy'] = (local_team is not None and 
                                          player_info['team'] != local_team and 
                                          player_info['team'] != 0)
                
                players.append(player_info)
            except:
                continue
        
        return players
    
    def disconnect(self):
        """?????????? ?? ????????"""
        if self.process:
            try:
                self.process.close_handle()
            except:
                pass
        self.process = None
        self.client_dll = None
        self.connected = False
        print("[+] ????????? ?? CS2")
