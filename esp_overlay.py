"""
CS2 ESP Overlay
?????????? ??????? ? ???????, ?????????, ???????? ? ??????? ?????????
"""

import pygame
import math
import time
from typing import List, Dict, Optional, Tuple
from esp_memory import CS2ESPMemory, ViewMatrix, Vector3, BoneIds

class ESPOverlay:
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        pygame.init()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # ??????? ?????????? ????
        self.screen = pygame.display.set_mode(
            (screen_width, screen_height),
            pygame.NOFRAME | pygame.HWSURFACE
        )
        pygame.display.set_caption("CS2 ESP")
        
        # ?????? ???? ?????? ?????? (??????? ?????????????? ????????? ? Windows)
        try:
            import win32gui
            import win32con
            hwnd = pygame.display.get_wm_info()['window']
            win32gui.SetWindowLong(
                hwnd, 
                win32con.GWL_EXSTYLE,
                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST
            )
            win32gui.SetLayeredWindowAttributes(hwnd, win32gui.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)
        except:
            print("[!] ?? ??????? ????????? ???????????? ???? (????? pywin32)")
        
        # ?????
        self.colors = {
            'enemy': (255, 0, 0),           # ??????? ??? ??????
            'teammate': (0, 255, 0),        # ??????? ??? ?????????
            'box': (255, 255, 255),         # ????? ??? ??????
            'skeleton': (200, 200, 200),    # ????? ??? ???????
            'health_bg': (50, 50, 50),      # ??? ????????
            'health_low': (255, 0, 0),      # ??????? (?????? ????????)
            'health_mid': (255, 165, 0),    # ????????? (???????)
            'health_high': (0, 255, 0),     # ??????? (???????)
            'text': (255, 255, 255),        # ????? ?????
            'snapline': (255, 255, 0),      # ?????? ?????
            'crosshair': (0, 255, 255),     # ??????? ??????
        }
        
        # ????????? ESP
        self.show_boxes = True
        self.show_health = True
        self.show_distance = True
        self.show_names = True
        self.show_skeleton = True
        self.show_snaplines = True
        self.show_head_circle = True
        self.show_teammates = False
        
        # ??????
        self.font_small = pygame.font.Font(None, 16)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 24)
        
        # FPS
        self.clock = pygame.time.Clock()
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
    def draw_box_esp(self, head_pos: Tuple[int, int], foot_pos: Tuple[int, int], 
                     color: Tuple[int, int, int], health: int = 100):
        """????????? 2D ????? ?????? ??????"""
        if not head_pos or not foot_pos:
            return
        
        # ????????? ??????? ?????
        height = abs(foot_pos[1] - head_pos[1])
        width = int(height * 0.4)  # ?????? = 40% ??????
        
        # ????? ?????
        center_x = head_pos[0]
        
        # ?????????? ?????
        x1 = center_x - width // 2
        y1 = head_pos[1]
        x2 = center_x + width // 2
        y2 = foot_pos[1]
        
        # ?????? ???????? ????
        pygame.draw.rect(self.screen, color, (x1, y1, x2 - x1, y2 - y1), 2)
        
        # ?????? ?????? ????????
        if self.show_health:
            self.draw_health_bar(x1 - 6, y1, health, y2 - y1)
    
    def draw_health_bar(self, x: int, y: int, health: int, height: int):
        """????????? ?????? ????????"""
        health = max(0, min(100, health))
        
        # ???
        pygame.draw.rect(self.screen, self.colors['health_bg'], (x - 2, y, 4, height))
        
        # ???? ? ??????????? ?? ????????
        if health > 75:
            color = self.colors['health_high']
        elif health > 35:
            color = self.colors['health_mid']
        else:
            color = self.colors['health_low']
        
        # ?????? ????????
        health_height = int((health / 100) * height)
        pygame.draw.rect(self.screen, color, (x - 1, y + (height - health_height), 2, health_height))
        
        # ????? ?? ????????? ????????
        if health < 100:
            health_text = self.font_small.render(str(health), True, self.colors['text'])
            self.screen.blit(health_text, (x - 15, y + height // 2))
    
    def draw_skeleton(self, pawn_address: int, memory: CS2ESPMemory, 
                     view_matrix: ViewMatrix, color: Tuple[int, int, int]):
        """????????? ??????? ??????"""
        if not self.show_skeleton:
            return
        
        # ?????????? ????? ??? ??????????
        bone_connections = [
            # ???????????
            (BoneIds.PELVIS, BoneIds.CHEST),
            (BoneIds.CHEST, BoneIds.NECK),
            (BoneIds.NECK, BoneIds.HEAD),
            
            # ????? ????
            (BoneIds.NECK, BoneIds.LEFT_SHOULDER),
            (BoneIds.LEFT_SHOULDER, BoneIds.LEFT_ELBOW),
            (BoneIds.LEFT_ELBOW, BoneIds.LEFT_HAND),
            
            # ?????? ????
            (BoneIds.NECK, BoneIds.RIGHT_SHOULDER),
            (BoneIds.RIGHT_SHOULDER, BoneIds.RIGHT_ELBOW),
            (BoneIds.RIGHT_ELBOW, BoneIds.RIGHT_HAND),
            
            # ????? ????
            (BoneIds.PELVIS, BoneIds.LEFT_HIP),
            (BoneIds.LEFT_HIP, BoneIds.LEFT_KNEE),
            (BoneIds.LEFT_KNEE, BoneIds.LEFT_FOOT),
            
            # ?????? ????
            (BoneIds.PELVIS, BoneIds.RIGHT_HIP),
            (BoneIds.RIGHT_HIP, BoneIds.RIGHT_KNEE),
            (BoneIds.RIGHT_KNEE, BoneIds.RIGHT_FOOT),
        ]
        
        # ???????? ??????? ?????? ? ???????????? ? ???????? ??????????
        bone_screen_positions = {}
        
        for bone_id in [BoneIds.HEAD, BoneIds.NECK, BoneIds.CHEST, BoneIds.PELVIS,
                       BoneIds.LEFT_SHOULDER, BoneIds.LEFT_ELBOW, BoneIds.LEFT_HAND,
                       BoneIds.RIGHT_SHOULDER, BoneIds.RIGHT_ELBOW, BoneIds.RIGHT_HAND,
                       BoneIds.LEFT_HIP, BoneIds.LEFT_KNEE, BoneIds.LEFT_FOOT,
                       BoneIds.RIGHT_HIP, BoneIds.RIGHT_KNEE, BoneIds.RIGHT_FOOT]:
            
            bone_pos = memory.get_bone_position(pawn_address, bone_id)
            if bone_pos:
                screen_pos = view_matrix.world_to_screen(
                    bone_pos, self.screen_width, self.screen_height
                )
                if screen_pos:
                    bone_screen_positions[bone_id] = screen_pos
        
        # ?????? ????? ????? ???????
        for bone1, bone2 in bone_connections:
            if bone1 in bone_screen_positions and bone2 in bone_screen_positions:
                pygame.draw.line(
                    self.screen, 
                    color,
                    bone_screen_positions[bone1],
                    bone_screen_positions[bone2],
                    2
                )
    
    def draw_head_circle(self, head_pos: Tuple[int, int], color: Tuple[int, int, int]):
        """????????? ????? ?????? ??????"""
        if not self.show_head_circle or not head_pos:
            return
        
        pygame.draw.circle(self.screen, color, head_pos, 8, 2)
    
    def draw_snapline(self, target_pos: Tuple[int, int]):
        """????????? ????? ?? ???? ?????? ? ??????"""
        if not self.show_snaplines or not target_pos:
            return
        
        start_pos = (self.screen_width // 2, self.screen_height)
        pygame.draw.line(self.screen, self.colors['snapline'], start_pos, target_pos, 1)
    
    def draw_player_info(self, pos: Tuple[int, int], name: str, distance: float, 
                        health: int, color: Tuple[int, int, int]):
        """????????? ?????????? ?? ??????"""
        if not pos:
            return
        
        x, y = pos
        offset_y = -15
        
        # ??? ??????
        if self.show_names:
            name_text = self.font_medium.render(name, True, color)
            name_rect = name_text.get_rect(center=(x, y + offset_y))
            
            # ?????? ??????? ??? ??????
            shadow_text = self.font_medium.render(name, True, (0, 0, 0))
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                shadow_rect = name_rect.copy()
                shadow_rect.x += dx
                shadow_rect.y += dy
                self.screen.blit(shadow_text, shadow_rect)
            
            self.screen.blit(name_text, name_rect)
            offset_y -= 20
        
        # ??????????
        if self.show_distance:
            dist_text = self.font_small.render(f"{int(distance)}m", True, self.colors['text'])
            dist_rect = dist_text.get_rect(center=(x, y + offset_y))
            self.screen.blit(dist_text, dist_rect)
    
    def draw_crosshair(self):
        """????????? ?????????? ? ?????? ??????"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        size = 10
        gap = 5
        thickness = 2
        
        color = self.colors['crosshair']
        
        # ???????????? ????? (????)
        pygame.draw.line(self.screen, color, 
                        (center_x, center_y - gap - size), 
                        (center_x, center_y - gap), thickness)
        
        # ???????????? ????? (???)
        pygame.draw.line(self.screen, color, 
                        (center_x, center_y + gap), 
                        (center_x, center_y + gap + size), thickness)
        
        # ?????????????? ????? (????)
        pygame.draw.line(self.screen, color, 
                        (center_x - gap - size, center_y), 
                        (center_x - gap, center_y), thickness)
        
        # ?????????????? ????? (?????)
        pygame.draw.line(self.screen, color, 
                        (center_x + gap, center_y), 
                        (center_x + gap + size, center_y), thickness)
        
        # ????? ? ??????
        pygame.draw.circle(self.screen, color, (center_x, center_y), 2)
    
    def draw_watermark(self):
        """????????? ???????? ?????"""
        watermark = f"CS2 ESP | FPS: {self.current_fps} | F1-F6: Toggle Features | END: Exit"
        text = self.font_small.render(watermark, True, self.colors['text'])
        
        # ?????? ??? ??? ??????
        text_rect = text.get_rect(topleft=(10, 10))
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
        
        self.screen.blit(text, (10, 10))
        
        # ?????????? ? ?????????? ????????
        features = []
        if self.show_boxes: features.append("Boxes")
        if self.show_skeleton: features.append("Skeleton")
        if self.show_snaplines: features.append("Lines")
        if self.show_health: features.append("Health")
        if self.show_names: features.append("Names")
        
        feature_text = f"Active: {', '.join(features)}"
        text2 = self.font_small.render(feature_text, True, self.colors['text'])
        self.screen.blit(text2, (10, 30))
    
    def calculate_distance(self, pos1: Vector3, pos2: Vector3) -> float:
        """?????????? ?????????? ????? ????? ??????? (? ??????)"""
        if not pos1 or not pos2:
            return 0
        
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        dz = pos1.z - pos2.z
        
        # ?????????? ? ?????? / 52.5 = ????? (????????)
        distance_units = math.sqrt(dx * dx + dy * dy + dz * dz)
        return distance_units / 52.5
    
    def render_frame(self, players: List[Dict], memory: CS2ESPMemory, view_matrix: ViewMatrix):
        """?????? ?????? ?????"""
        # ??????? ?????? (?????? ? ????? ??? ????????????)
        self.screen.fill((0, 0, 0))
        
        # ???????? ?????????? ??????
        local_controller = memory.get_local_player_controller()
        local_origin = None
        
        if local_controller:
            local_pawn = memory.get_player_pawn_from_controller(local_controller)
            if local_pawn:
                local_origin = memory.read_vec3(local_pawn + 0xD8)  # m_vecAbsOrigin
        
        # ?????? ??????? ??????
        for player in players:
            # ?????????? ????????? ???? ????? ?????????
            if not self.show_teammates and not player['is_enemy']:
                continue
            
            origin = player.get('origin')
            head_pos_3d = player.get('head_pos')
            
            if not origin or not head_pos_3d or not view_matrix:
                continue
            
            # ???????????? ??????? ? ???????? ??????????
            head_screen = view_matrix.world_to_screen(
                head_pos_3d, self.screen_width, self.screen_height
            )
            
            # ??????? ??? (??????? ???? origin)
            foot_pos_3d = Vector3(origin.x, origin.y, origin.z - 70)
            foot_screen = view_matrix.world_to_screen(
                foot_pos_3d, self.screen_width, self.screen_height
            )
            
            if not head_screen or not foot_screen:
                continue
            
            # ?????????? ????
            color = self.colors['enemy'] if player['is_enemy'] else self.colors['teammate']
            
            # ?????? ????? ?? ???? ??????
            self.draw_snapline(foot_screen)
            
            # ?????? ????
            if self.show_boxes:
                self.draw_box_esp(head_screen, foot_screen, color, player['health'])
            
            # ?????? ??????
            if self.show_skeleton:
                self.draw_skeleton(player['pawn_address'], memory, view_matrix, color)
            
            # ?????? ???? ?? ??????
            self.draw_head_circle(head_screen, color)
            
            # ????????? ??????????
            distance = 0
            if local_origin:
                distance = self.calculate_distance(local_origin, origin)
            
            # ?????? ??????????
            self.draw_player_info(head_screen, player['name'], distance, player['health'], color)
        
        # ?????? ?????????
        self.draw_crosshair()
        
        # ?????? ??????? ????
        self.draw_watermark()
        
        # ????????? ?????
        pygame.display.flip()
        self.update_fps()
    
    def update_fps(self):
        """?????????? ???????? FPS"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    def handle_events(self) -> bool:
        """????????? ???????, ?????????? False ???? ????? ?????"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_END:
                    return False
                elif event.key == pygame.K_F1:
                    self.show_boxes = not self.show_boxes
                    print(f"[*] Boxes ESP: {self.show_boxes}")
                elif event.key == pygame.K_F2:
                    self.show_skeleton = not self.show_skeleton
                    print(f"[*] Skeleton ESP: {self.show_skeleton}")
                elif event.key == pygame.K_F3:
                    self.show_snaplines = not self.show_snaplines
                    print(f"[*] Snaplines: {self.show_snaplines}")
                elif event.key == pygame.K_F4:
                    self.show_health = not self.show_health
                    print(f"[*] Health Bars: {self.show_health}")
                elif event.key == pygame.K_F5:
                    self.show_names = not self.show_names
                    print(f"[*] Player Names: {self.show_names}")
                elif event.key == pygame.K_F6:
                    self.show_teammates = not self.show_teammates
                    print(f"[*] Show Teammates: {self.show_teammates}")
        
        return True
    
    def run_frame(self, target_fps: int = 144):
        """?????? ?????? ????? ? ???????????? FPS"""
        self.clock.tick(target_fps)
    
    def cleanup(self):
        """??????? ????????"""
        pygame.quit()
