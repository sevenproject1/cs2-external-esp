"""
CS2 Radar GUI
Real-time radar display using pygame
"""

import pygame
import math
import time
from typing import List, Dict, Tuple, Optional
from entity_parser import EntityParser
from memory_reader import CS2MemoryReader

class RadarGUI:
    def __init__(self, size: int = 500):
        pygame.init()
        
        # Window settings
        self.size = size
        self.radar_size = size - 100  # Leave space for UI elements
        self.screen = pygame.display.set_mode((size, size + 100))
        pygame.display.set_caption("CS2 Mini Radar - Educational Purpose")
        
        # Colors
        self.colors = {
            'background': (20, 20, 30),
            'radar_bg': (40, 40, 50),
            'enemy': (255, 50, 50),
            'teammate': (50, 150, 255),
            'local_player': (50, 255, 50),
            'text': (255, 255, 255),
            'grid': (60, 60, 70),
            'border': (100, 100, 120)
        }
        
        # Fonts
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        
        # Radar settings
        self.radar_center = (50, 50)
        self.zoom_level = 1.0
        self.show_teammates = True
        self.show_grid = True
        
        # Statistics
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        
    def draw_radar_background(self):
        """Draw the radar background and grid"""
        radar_rect = pygame.Rect(50, 50, self.radar_size, self.radar_size)
        
        # Draw radar background
        pygame.draw.rect(self.screen, self.colors['radar_bg'], radar_rect)
        pygame.draw.rect(self.screen, self.colors['border'], radar_rect, 2)
        
        if self.show_grid:
            # Draw grid lines
            grid_spacing = self.radar_size // 8
            for i in range(1, 8):
                x = 50 + i * grid_spacing
                y = 50 + i * grid_spacing
                
                # Vertical lines
                pygame.draw.line(self.screen, self.colors['grid'], 
                               (x, 50), (x, 50 + self.radar_size), 1)
                # Horizontal lines
                pygame.draw.line(self.screen, self.colors['grid'], 
                               (50, y), (50 + self.radar_size, y), 1)
            
            # Draw center cross
            center_x = 50 + self.radar_size // 2
            center_y = 50 + self.radar_size // 2
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (center_x - 10, center_y), (center_x + 10, center_y), 2)
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (center_x, center_y - 10), (center_x, center_y + 10), 2)
    
    def draw_player(self, x: int, y: int, player_type: str, health: int = 100):
        """Draw a player dot on the radar"""
        # Adjust coordinates to radar space
        radar_x = 50 + x
        radar_y = 50 + y
        
        # Skip if outside radar bounds
        if (radar_x < 50 or radar_x > 50 + self.radar_size or 
            radar_y < 50 or radar_y > 50 + self.radar_size):
            return
        
        color = self.colors.get(player_type, self.colors['enemy'])
        
        # Draw player dot
        if player_type == 'local_player':
            # Draw local player as a triangle pointing up
            points = [
                (radar_x, radar_y - 8),
                (radar_x - 6, radar_y + 6),
                (radar_x + 6, radar_y + 6)
            ]
            pygame.draw.polygon(self.screen, color, points)
        else:
            # Draw other players as circles
            radius = 6 if player_type == 'enemy' else 4
            pygame.draw.circle(self.screen, color, (radar_x, radar_y), radius)
            
            # Draw health indicator for enemies
            if player_type == 'enemy' and health < 100:
                health_color = (255, int(255 * health / 100), 0)
                pygame.draw.circle(self.screen, health_color, (radar_x, radar_y), radius - 2)
    
    def draw_ui_elements(self, player_count: Dict[str, int], 
                        connection_status: bool, current_map: str):
        """Draw UI elements like status, player count, etc."""
        y_offset = self.size - 90
        
        # Connection status
        status_text = "Connected" if connection_status else "Disconnected"
        status_color = self.colors['teammate'] if connection_status else self.colors['enemy']
        text = self.font_medium.render(f"Status: {status_text}", True, status_color)
        self.screen.blit(text, (10, y_offset))
        
        # Player counts
        enemy_text = self.font_small.render(f"Enemies: {player_count.get('enemies', 0)}", 
                                          True, self.colors['enemy'])
        teammate_text = self.font_small.render(f"Teammates: {player_count.get('teammates', 0)}", 
                                             True, self.colors['teammate'])
        
        self.screen.blit(enemy_text, (10, y_offset + 25))
        self.screen.blit(teammate_text, (10, y_offset + 45))
        
        # Map name
        map_text = self.font_small.render(f"Map: {current_map}", True, self.colors['text'])
        self.screen.blit(map_text, (150, y_offset))
        
        # FPS counter
        fps_text = self.font_small.render(f"FPS: {self.current_fps}", True, self.colors['text'])
        self.screen.blit(fps_text, (150, y_offset + 20))
        
        # Instructions
        instructions = [
            "ESC - Exit",
            "G - Toggle Grid",
            "T - Toggle Teammates"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, self.colors['text'])
            self.screen.blit(text, (300, y_offset + i * 15))
    
    def draw_legend(self):
        """Draw color legend"""
        legend_x = self.size - 120
        legend_y = 60
        
        # Title
        title = self.font_small.render("Legend:", True, self.colors['text'])
        self.screen.blit(title, (legend_x, legend_y))
        
        # Legend items
        items = [
            ("Enemy", self.colors['enemy']),
            ("Teammate", self.colors['teammate']),
            ("You", self.colors['local_player'])
        ]
        
        for i, (label, color) in enumerate(items):
            y = legend_y + 20 + i * 20
            pygame.draw.circle(self.screen, color, (legend_x + 10, y + 8), 4)
            text = self.font_small.render(label, True, self.colors['text'])
            self.screen.blit(text, (legend_x + 25, y))
    
    def update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    def handle_events(self) -> bool:
        """Handle pygame events, return False if should quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_t:
                    self.show_teammates = not self.show_teammates
        
        return True
    
    def render_frame(self, players: List[Dict], local_player: Optional[Dict],
                    player_count: Dict[str, int], connection_status: bool, 
                    current_map: str):
        """Render a complete frame"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Draw radar background
        self.draw_radar_background()
        
        # Draw local player
        if local_player and local_player.get('radar_pos'):
            radar_pos = local_player['radar_pos']
            self.draw_player(radar_pos[0], radar_pos[1], 'local_player')
        
        # Draw other players
        for player in players:
            if not player.get('radar_pos'):
                continue
                
            radar_pos = player['radar_pos']
            
            if player['is_enemy']:
                self.draw_player(radar_pos[0], radar_pos[1], 'enemy', player['health'])
            elif self.show_teammates:
                self.draw_player(radar_pos[0], radar_pos[1], 'teammate', player['health'])
        
        # Draw UI elements
        self.draw_ui_elements(player_count, connection_status, current_map)
        self.draw_legend()
        
        # Update display
        pygame.display.flip()
        self.update_fps()
    
    def run_frame(self, target_fps: int = 60):
        """Run one frame with FPS limiting"""
        self.clock.tick(target_fps)
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()