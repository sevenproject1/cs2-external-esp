"""
CS2 Entity Parser
Processes game entities and extracts relevant player data
"""

import math
from typing import List, Dict, Optional, Tuple
from memory_reader import CS2MemoryReader
from offsets import MAP_BOUNDS

class EntityParser:
    def __init__(self, memory_reader: CS2MemoryReader):
        self.memory_reader = memory_reader
        self.local_player_team = 0
        self.current_map = "de_dust2"  # Default map
        
    def update_local_player_info(self):
        """Update local player information"""
        local_player = self.memory_reader.get_local_player()
        if local_player:
            player_info = self.memory_reader.get_player_info(local_player)
            if player_info:
                self.local_player_team = player_info.get('team', 0)
    
    def get_all_players(self) -> List[Dict]:
        """Get information for all players in the game"""
        players = []
        entities = self.memory_reader.get_entity_list()
        
        self.update_local_player_info()
        
        for entity in entities:
            player_info = self.memory_reader.get_player_info(entity)
            if player_info and player_info['alive'] and player_info['health'] > 0:
                # Add additional processed data
                player_info['is_enemy'] = self.is_enemy(player_info['team'])
                player_info['radar_pos'] = self.world_to_radar(
                    player_info['x'], player_info['y']
                )
                players.append(player_info)
        
        return players
    
    def is_enemy(self, player_team: int) -> bool:
        """Check if player is an enemy"""
        if self.local_player_team == 0:
            return True  # Unknown team, assume enemy
        return player_team != self.local_player_team and player_team != 0
    
    def world_to_radar(self, world_x: float, world_y: float, 
                      radar_size: int = 400) -> Tuple[int, int]:
        """Convert world coordinates to radar coordinates"""
        bounds = MAP_BOUNDS.get(self.current_map, MAP_BOUNDS['de_dust2'])
        
        # Normalize world coordinates to 0-1 range
        norm_x = (world_x - bounds['x_min']) / (bounds['x_max'] - bounds['x_min'])
        norm_y = (world_y - bounds['y_min']) / (bounds['y_max'] - bounds['y_min'])
        
        # Convert to radar coordinates
        radar_x = int(norm_x * radar_size)
        radar_y = int((1 - norm_y) * radar_size)  # Flip Y axis
        
        # Clamp to radar bounds
        radar_x = max(0, min(radar_size - 1, radar_x))
        radar_y = max(0, min(radar_size - 1, radar_y))
        
        return radar_x, radar_y
    
    def get_distance_2d(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate 2D distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def get_enemies_only(self) -> List[Dict]:
        """Get only enemy players"""
        all_players = self.get_all_players()
        return [player for player in all_players if player['is_enemy']]
    
    def get_teammates_only(self) -> List[Dict]:
        """Get only teammate players"""
        all_players = self.get_all_players()
        return [player for player in all_players if not player['is_enemy']]
    
    def get_local_player_info(self) -> Optional[Dict]:
        """Get local player information"""
        local_player = self.memory_reader.get_local_player()
        if local_player:
            return self.memory_reader.get_player_info(local_player)
        return None
    
    def detect_current_map(self) -> str:
        """Attempt to detect current map (simplified)"""
        # This is a simplified implementation
        # In a real implementation, you'd read the map name from game memory
        return self.current_map
    
    def set_current_map(self, map_name: str):
        """Manually set the current map"""
        if map_name in MAP_BOUNDS:
            self.current_map = map_name
            print(f"Map set to: {map_name}")
        else:
            print(f"Unknown map: {map_name}, using default bounds")
    
    def get_player_count(self) -> Dict[str, int]:
        """Get count of players by team"""
        players = self.get_all_players()
        
        enemies = len([p for p in players if p['is_enemy']])
        teammates = len([p for p in players if not p['is_enemy']])
        
        return {
            'enemies': enemies,
            'teammates': teammates,
            'total': len(players)
        }
    
    def get_closest_enemy(self, reference_pos: Tuple[float, float]) -> Optional[Dict]:
        """Get the closest enemy to a reference position"""
        enemies = self.get_enemies_only()
        if not enemies:
            return None
        
        closest_enemy = None
        closest_distance = float('inf')
        
        for enemy in enemies:
            enemy_pos = (enemy['x'], enemy['y'])
            distance = self.get_distance_2d(reference_pos, enemy_pos)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy
        
        if closest_enemy:
            closest_enemy['distance'] = closest_distance
        
        return closest_enemy