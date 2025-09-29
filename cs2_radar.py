#!/usr/bin/env python3
"""
CS2 Mini Radar - Educational Project
====================================

This is an educational radar application for Counter-Strike 2.
It demonstrates concepts of memory reading, real-time data processing,
and GUI development for educational purposes.

IMPORTANT DISCLAIMERS:
- This is for educational purposes only
- Do not use in actual gameplay as it may violate game terms of service
- This project is designed for learning about game development and memory management
- Use only in controlled educational environments

Author: Educational Project
Purpose: School Work - Learning about game memory and real-time visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import threading
import time
import struct
import psutil
from typing import List, Dict, Tuple, Optional
import json
import os

class Player:
    """Represents a player in the game"""
    def __init__(self, name: str, x: float, y: float, z: float, health: int, team: int, is_enemy: bool = True):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.health = health
        self.team = team
        self.is_enemy = is_enemy
        self.last_seen = time.time()
        self.is_visible = True

class CS2Radar:
    """Main radar application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS2 Mini Radar - Educational Project")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Radar settings
        self.radar_size = 400
        self.scale = 0.1  # Scale factor for coordinates
        self.center_x = self.radar_size // 2
        self.center_y = self.radar_size // 2
        
        # Game state
        self.players: List[Player] = []
        self.local_player: Optional[Player] = None
        self.is_running = False
        self.update_thread = None
        
        # CS2 process detection
        self.cs2_process = None
        self.process_id = None
        
        # Memory offsets (simulated for educational purposes)
        self.offsets = {
            'local_player': 0x1E8F2C8,
            'entity_list': 0x1E8F2D0,
            'player_health': 0x334,
            'player_position': 0x128,
            'player_team': 0x3C5,
            'player_name': 0x6C0
        }
        
        self.setup_ui()
        self.setup_radar()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="CS2 Mini Radar - Educational Project", 
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#1a1a1a"
        )
        title_label.pack(pady=10)
        
        # Disclaimer
        disclaimer = tk.Label(
            self.root,
            text="⚠️ EDUCATIONAL USE ONLY - Do not use in actual gameplay ⚠️",
            font=("Arial", 10),
            fg="orange",
            bg="#1a1a1a"
        )
        disclaimer.pack(pady=5)
        
        # Control frame
        control_frame = tk.Frame(self.root, bg="#1a1a1a")
        control_frame.pack(pady=10)
        
        # Start/Stop button
        self.start_button = tk.Button(
            control_frame,
            text="Start Radar",
            command=self.toggle_radar,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Status: Stopped",
            font=("Arial", 12),
            fg="white",
            bg="#1a1a1a"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Settings frame
        settings_frame = tk.Frame(self.root, bg="#1a1a1a")
        settings_frame.pack(pady=10)
        
        # Scale control
        tk.Label(settings_frame, text="Scale:", fg="white", bg="#1a1a1a").pack(side=tk.LEFT)
        self.scale_var = tk.DoubleVar(value=self.scale)
        scale_scale = tk.Scale(
            settings_frame,
            from_=0.01,
            to=0.5,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.scale_var,
            command=self.update_scale,
            bg="#2a2a2a",
            fg="white"
        )
        scale_scale.pack(side=tk.LEFT, padx=5)
        
        # Refresh rate control
        tk.Label(settings_frame, text="Refresh Rate (ms):", fg="white", bg="#1a1a1a").pack(side=tk.LEFT, padx=(20, 5))
        self.refresh_rate = tk.IntVar(value=100)
        refresh_scale = tk.Scale(
            settings_frame,
            from_=50,
            to=1000,
            resolution=50,
            orient=tk.HORIZONTAL,
            variable=self.refresh_rate,
            bg="#2a2a2a",
            fg="white"
        )
        refresh_scale.pack(side=tk.LEFT, padx=5)
        
    def setup_radar(self):
        """Setup the radar display"""
        # Radar frame
        radar_frame = tk.Frame(self.root, bg="#1a1a1a")
        radar_frame.pack(pady=20)
        
        # Radar canvas
        self.radar_canvas = tk.Canvas(
            radar_frame,
            width=self.radar_size,
            height=self.radar_size,
            bg="#0a0a0a",
            highlightthickness=2,
            highlightbackground="#333333"
        )
        self.radar_canvas.pack()
        
        # Draw radar grid
        self.draw_radar_grid()
        
        # Info frame
        info_frame = tk.Frame(self.root, bg="#1a1a1a")
        info_frame.pack(pady=10)
        
        # Player count
        self.player_count_label = tk.Label(
            info_frame,
            text="Players: 0",
            font=("Arial", 12),
            fg="white",
            bg="#1a1a1a"
        )
        self.player_count_label.pack(side=tk.LEFT, padx=10)
        
        # Enemy count
        self.enemy_count_label = tk.Label(
            info_frame,
            text="Enemies: 0",
            font=("Arial", 12),
            fg="red",
            bg="#1a1a1a"
        )
        self.enemy_count_label.pack(side=tk.LEFT, padx=10)
        
    def draw_radar_grid(self):
        """Draw the radar grid"""
        self.radar_canvas.delete("grid")
        
        # Center cross
        self.radar_canvas.create_line(
            self.center_x, 0, self.center_x, self.radar_size,
            fill="#333333", width=1, tags="grid"
        )
        self.radar_canvas.create_line(
            0, self.center_y, self.radar_size, self.center_y,
            fill="#333333", width=1, tags="grid"
        )
        
        # Circles for distance reference
        for i in range(1, 6):
            radius = i * self.radar_size // 10
            self.radar_canvas.create_oval(
                self.center_x - radius, self.center_y - radius,
                self.center_x + radius, self.center_y + radius,
                outline="#333333", width=1, tags="grid"
            )
            
        # Center dot (local player)
        self.radar_canvas.create_oval(
            self.center_x - 3, self.center_y - 3,
            self.center_x + 3, self.center_y + 3,
            fill="#00FF00", outline="white", width=2, tags="local_player"
        )
        
    def update_scale(self, value):
        """Update radar scale"""
        self.scale = float(value)
        self.update_radar()
        
    def toggle_radar(self):
        """Toggle radar on/off"""
        if not self.is_running:
            self.start_radar()
        else:
            self.stop_radar()
            
    def start_radar(self):
        """Start the radar"""
        self.is_running = True
        self.start_button.config(text="Stop Radar", bg="#f44336")
        self.status_label.config(text="Status: Running")
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.radar_update_loop, daemon=True)
        self.update_thread.start()
        
    def stop_radar(self):
        """Stop the radar"""
        self.is_running = False
        self.start_button.config(text="Start Radar", bg="#4CAF50")
        self.status_label.config(text="Status: Stopped")
        
    def radar_update_loop(self):
        """Main radar update loop"""
        while self.is_running:
            try:
                self.update_game_data()
                self.update_radar()
                time.sleep(self.refresh_rate.get() / 1000.0)
            except Exception as e:
                print(f"Error in radar update: {e}")
                time.sleep(1)
                
    def update_game_data(self):
        """Update game data (simulated for educational purposes)"""
        # In a real implementation, this would read from CS2 memory
        # For educational purposes, we'll simulate player data
        
        if not self.is_running:
            return
            
        # Simulate finding CS2 process
        if not self.cs2_process:
            self.find_cs2_process()
            
        # Generate simulated player data
        self.generate_simulated_players()
        
    def find_cs2_process(self):
        """Find CS2 process (simulated)"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'cs2' in proc.info['name'].lower():
                    self.cs2_process = proc
                    self.process_id = proc.info['pid']
                    print(f"Found CS2 process: PID {self.process_id}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    def generate_simulated_players(self):
        """Generate simulated player data for demonstration"""
        if not self.is_running:
            return
            
        # Clear old players
        self.players.clear()
        
        # Generate random enemy positions
        num_enemies = random.randint(1, 5)
        for i in range(num_enemies):
            # Generate random position around the map
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 200)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            z = random.uniform(-50, 50)
            
            player = Player(
                name=f"Enemy_{i+1}",
                x=x,
                y=y,
                z=z,
                health=random.randint(1, 100),
                team=2,  # Terrorist team
                is_enemy=True
            )
            self.players.append(player)
            
        # Add some teammates (non-enemies)
        num_teammates = random.randint(0, 2)
        for i in range(num_teammates):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(30, 100)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            z = random.uniform(-30, 30)
            
            player = Player(
                name=f"Teammate_{i+1}",
                x=x,
                y=y,
                z=z,
                health=random.randint(50, 100),
                team=3,  # Counter-Terrorist team
                is_enemy=False
            )
            self.players.append(player)
            
    def update_radar(self):
        """Update radar display"""
        if not self.is_running:
            return
            
        # Clear previous player markers
        self.radar_canvas.delete("players")
        
        # Draw players
        for player in self.players:
            self.draw_player(player)
            
        # Update info labels
        enemy_count = sum(1 for p in self.players if p.is_enemy)
        self.player_count_label.config(text=f"Players: {len(self.players)}")
        self.enemy_count_label.config(text=f"Enemies: {enemy_count}")
        
    def draw_player(self, player: Player):
        """Draw a player on the radar"""
        # Convert world coordinates to radar coordinates
        radar_x = self.center_x + (player.x * self.scale)
        radar_y = self.center_y - (player.y * self.scale)  # Invert Y for proper orientation
        
        # Clamp to radar bounds
        radar_x = max(5, min(self.radar_size - 5, radar_x))
        radar_y = max(5, min(self.radar_size - 5, radar_y))
        
        # Choose color based on team
        if player.is_enemy:
            color = "#FF0000"  # Red for enemies
            outline = "#FFFFFF"
        else:
            color = "#0000FF"  # Blue for teammates
            outline = "#FFFFFF"
            
        # Draw player dot
        size = 6 if player.is_enemy else 4
        self.radar_canvas.create_oval(
            radar_x - size, radar_y - size,
            radar_x + size, radar_y + size,
            fill=color, outline=outline, width=2, tags="players"
        )
        
        # Draw health bar
        if player.health < 100:
            bar_width = 20
            bar_height = 3
            health_width = int((player.health / 100) * bar_width)
            
            # Health bar background
            self.radar_canvas.create_rectangle(
                radar_x - bar_width//2, radar_y - size - 8,
                radar_x + bar_width//2, radar_y - size - 5,
                fill="#333333", outline="", tags="players"
            )
            
            # Health bar fill
            health_color = "#00FF00" if player.health > 50 else "#FFFF00" if player.health > 25 else "#FF0000"
            self.radar_canvas.create_rectangle(
                radar_x - bar_width//2, radar_y - size - 8,
                radar_x - bar_width//2 + health_width, radar_y - size - 5,
                fill=health_color, outline="", tags="players"
            )
            
        # Draw distance indicator
        distance = math.sqrt(player.x**2 + player.y**2)
        if distance > 0:
            self.radar_canvas.create_text(
                radar_x, radar_y + size + 10,
                text=f"{int(distance)}m",
                fill="white", font=("Arial", 8), tags="players"
            )
            
    def run(self):
        """Run the radar application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_radar()
            self.root.quit()

def main():
    """Main function"""
    print("CS2 Mini Radar - Educational Project")
    print("====================================")
    print("This is an educational project for learning about:")
    print("- Game memory reading concepts")
    print("- Real-time data visualization")
    print("- GUI development with Python")
    print("- Threading and concurrent programming")
    print()
    print("⚠️  IMPORTANT: This is for educational purposes only!")
    print("⚠️  Do not use in actual gameplay!")
    print()
    
    # Create and run radar
    radar = CS2Radar()
    radar.run()

if __name__ == "__main__":
    main()