#!/usr/bin/env python3
"""
Enhanced CS2 Radar - Educational Project
========================================

This is an enhanced version of the CS2 radar with advanced visualization features.
It demonstrates concepts of real-time data processing, GUI development, and game memory reading.

IMPORTANT DISCLAIMERS:
- This is for educational purposes only
- Do not use in actual gameplay as it may violate game terms of service
- This project is designed for learning about game development and memory management
- Use only in controlled educational environments

Features:
- Real-time enemy tracking
- Health indicators
- Distance calculations
- Team color coding
- Configurable settings
- Educational memory reading simulation

Author: Educational Project
Purpose: School Work - Learning about game memory and real-time visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import random
import threading
import time
import struct
import psutil
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class Team(Enum):
    SPECTATOR = 0
    TERRORIST = 2
    COUNTER_TERRORIST = 3

@dataclass
class Player:
    """Represents a player in the game"""
    name: str
    x: float
    y: float
    z: float
    health: int
    armor: int
    team: Team
    is_enemy: bool
    is_visible: bool = True
    last_seen: float = 0.0
    weapon: str = "Unknown"
    angle: float = 0.0

class EnhancedRadar:
    """Enhanced radar application with advanced features"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced CS2 Radar - Educational Project")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0d1117')
        
        # Radar settings
        self.radar_size = 500
        self.scale = 0.08
        self.center_x = self.radar_size // 2
        self.center_y = self.radar_size // 2
        
        # Game state
        self.players: List[Player] = []
        self.local_player: Optional[Player] = None
        self.is_running = False
        self.update_thread = None
        
        # Settings
        self.settings = {
            'show_health_bars': True,
            'show_distance': True,
            'show_weapon_info': True,
            'show_angles': False,
            'enemy_color': '#FF4444',
            'teammate_color': '#4444FF',
            'spectator_color': '#888888',
            'refresh_rate': 50,
            'max_distance': 2000
        }
        
        # Statistics
        self.stats = {
            'total_players': 0,
            'enemies_detected': 0,
            'teammates_detected': 0,
            'uptime': 0
        }
        
        self.start_time = time.time()
        
        self.setup_ui()
        self.setup_radar()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the enhanced user interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#0d1117')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls
        left_panel = tk.Frame(main_container, bg='#161b22', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Right panel for radar
        right_panel = tk.Frame(main_container, bg='#0d1117')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_control_panel(left_panel)
        self.setup_radar_panel(right_panel)
        
    def setup_control_panel(self, parent):
        """Setup the control panel"""
        # Title
        title_label = tk.Label(
            parent, 
            text="CS2 Enhanced Radar", 
            font=("Arial", 16, "bold"),
            fg="#58a6ff",
            bg="#161b22"
        )
        title_label.pack(pady=10)
        
        # Educational disclaimer
        disclaimer = tk.Label(
            parent,
            text="🎓 EDUCATIONAL PROJECT\n⚠️ Do not use in actual gameplay",
            font=("Arial", 9),
            fg="#f85149",
            bg="#161b22",
            justify=tk.CENTER
        )
        disclaimer.pack(pady=5)
        
        # Control buttons
        control_frame = tk.Frame(parent, bg="#161b22")
        control_frame.pack(pady=10, fill=tk.X)
        
        self.start_button = tk.Button(
            control_frame,
            text="🚀 Start Radar",
            command=self.toggle_radar,
            bg="#238636",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8
        )
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.settings_button = tk.Button(
            control_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            bg="#6f42c1",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        self.settings_button.pack(fill=tk.X, pady=2)
        
        # Status display
        status_frame = tk.Frame(parent, bg="#161b22")
        status_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(status_frame, text="Status:", fg="white", bg="#161b22", font=("Arial", 10, "bold")).pack()
        self.status_label = tk.Label(
            status_frame,
            text="Stopped",
            font=("Arial", 10),
            fg="#f85149",
            bg="#161b22"
        )
        self.status_label.pack()
        
        # Statistics
        stats_frame = tk.Frame(parent, bg="#161b22")
        stats_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(stats_frame, text="Statistics:", fg="white", bg="#161b22", font=("Arial", 10, "bold")).pack()
        
        self.stats_labels = {}
        for key in ['total_players', 'enemies_detected', 'teammates_detected', 'uptime']:
            self.stats_labels[key] = tk.Label(
                stats_frame,
                text=f"{key.replace('_', ' ').title()}: 0",
                font=("Arial", 9),
                fg="#8b949e",
                bg="#161b22"
            )
            self.stats_labels[key].pack(anchor=tk.W)
            
        # Scale control
        scale_frame = tk.Frame(parent, bg="#161b22")
        scale_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(scale_frame, text="Radar Scale:", fg="white", bg="#161b22", font=("Arial", 10, "bold")).pack()
        self.scale_var = tk.DoubleVar(value=self.scale)
        scale_scale = tk.Scale(
            scale_frame,
            from_=0.01,
            to=0.3,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.scale_var,
            command=self.update_scale,
            bg="#21262d",
            fg="white",
            highlightbackground="#161b22"
        )
        scale_scale.pack(fill=tk.X, pady=2)
        
        # Refresh rate control
        refresh_frame = tk.Frame(parent, bg="#161b22")
        refresh_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(refresh_frame, text="Refresh Rate (ms):", fg="white", bg="#161b22", font=("Arial", 10, "bold")).pack()
        self.refresh_rate_var = tk.IntVar(value=self.settings['refresh_rate'])
        refresh_scale = tk.Scale(
            refresh_frame,
            from_=16,
            to=500,
            resolution=16,
            orient=tk.HORIZONTAL,
            variable=self.refresh_rate_var,
            command=self.update_refresh_rate,
            bg="#21262d",
            fg="white",
            highlightbackground="#161b22"
        )
        refresh_scale.pack(fill=tk.X, pady=2)
        
    def setup_radar_panel(self, parent):
        """Setup the radar display panel"""
        # Radar container
        radar_container = tk.Frame(parent, bg="#0d1117")
        radar_container.pack(fill=tk.BOTH, expand=True)
        
        # Radar canvas
        self.radar_canvas = tk.Canvas(
            radar_container,
            width=self.radar_size,
            height=self.radar_size,
            bg="#0d1117",
            highlightthickness=3,
            highlightbackground="#30363d"
        )
        self.radar_canvas.pack(expand=True)
        
        # Draw initial radar
        self.draw_radar_grid()
        
        # Info panel below radar
        info_frame = tk.Frame(parent, bg="#161b22", height=100)
        info_frame.pack(fill=tk.X, pady=5)
        info_frame.pack_propagate(False)
        
        # Player list
        tk.Label(info_frame, text="Players:", fg="white", bg="#161b22", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        self.player_listbox = tk.Listbox(
            info_frame,
            height=4,
            bg="#21262d",
            fg="white",
            selectbackground="#30363d",
            font=("Consolas", 9)
        )
        self.player_listbox.pack(fill=tk.X, padx=5, pady=2)
        
    def draw_radar_grid(self):
        """Draw the enhanced radar grid"""
        self.radar_canvas.delete("grid")
        
        # Center cross
        self.radar_canvas.create_line(
            self.center_x, 0, self.center_x, self.radar_size,
            fill="#30363d", width=2, tags="grid"
        )
        self.radar_canvas.create_line(
            0, self.center_y, self.radar_size, self.center_y,
            fill="#30363d", width=2, tags="grid"
        )
        
        # Distance circles
        for i in range(1, 6):
            radius = i * self.radar_size // 10
            self.radar_canvas.create_oval(
                self.center_x - radius, self.center_y - radius,
                self.center_x + radius, self.center_y + radius,
                outline="#30363d", width=1, tags="grid"
            )
            
        # Distance labels
        for i in range(1, 6):
            distance = i * 200  # 200 units per circle
            self.radar_canvas.create_text(
                self.center_x + i * self.radar_size // 10, self.center_y - 5,
                text=f"{distance}m",
                fill="#8b949e", font=("Arial", 8), tags="grid"
            )
            
        # Center dot (local player)
        self.radar_canvas.create_oval(
            self.center_x - 4, self.center_y - 4,
            self.center_x + 4, self.center_y + 4,
            fill="#00ff00", outline="white", width=2, tags="local_player"
        )
        
        # Direction indicators
        directions = ['N', 'E', 'S', 'W']
        positions = [(self.center_x, 15), (self.radar_size - 15, self.center_y), 
                    (self.center_x, self.radar_size - 15), (15, self.center_y)]
        
        for direction, pos in zip(directions, positions):
            self.radar_canvas.create_text(
                pos[0], pos[1],
                text=direction,
                fill="#58a6ff", font=("Arial", 12, "bold"), tags="grid"
            )
            
    def update_scale(self, value):
        """Update radar scale"""
        self.scale = float(value)
        self.update_radar()
        
    def update_refresh_rate(self, value):
        """Update refresh rate"""
        self.settings['refresh_rate'] = int(value)
        
    def toggle_radar(self):
        """Toggle radar on/off"""
        if not self.is_running:
            self.start_radar()
        else:
            self.stop_radar()
            
    def start_radar(self):
        """Start the radar"""
        self.is_running = True
        self.start_button.config(text="🛑 Stop Radar", bg="#f85149")
        self.status_label.config(text="Running", fg="#3fb950")
        self.start_time = time.time()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.radar_update_loop, daemon=True)
        self.update_thread.start()
        
    def stop_radar(self):
        """Stop the radar"""
        self.is_running = False
        self.start_button.config(text="🚀 Start Radar", bg="#238636")
        self.status_label.config(text="Stopped", fg="#f85149")
        
    def radar_update_loop(self):
        """Main radar update loop"""
        while self.is_running:
            try:
                self.update_game_data()
                self.update_radar()
                self.update_statistics()
                time.sleep(self.settings['refresh_rate'] / 1000.0)
            except Exception as e:
                print(f"Error in radar update: {e}")
                time.sleep(1)
                
    def update_game_data(self):
        """Update game data (simulated for educational purposes)"""
        if not self.is_running:
            return
            
        # Clear old players
        self.players.clear()
        
        # Generate simulated enemy positions
        num_enemies = random.randint(1, 5)
        for i in range(num_enemies):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, 800)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            z = random.uniform(-100, 100)
            
            player = Player(
                name=f"Enemy_{i+1}",
                x=x,
                y=y,
                z=z,
                health=random.randint(1, 100),
                armor=random.randint(0, 100),
                team=Team.TERRORIST,
                is_enemy=True,
                weapon=random.choice(["AK-47", "AWP", "M4A4", "Glock-18"]),
                angle=random.uniform(0, 360)
            )
            self.players.append(player)
            
        # Generate teammates
        num_teammates = random.randint(0, 3)
        for i in range(num_teammates):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 400)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            z = random.uniform(-50, 50)
            
            player = Player(
                name=f"Teammate_{i+1}",
                x=x,
                y=y,
                z=z,
                health=random.randint(50, 100),
                armor=random.randint(0, 100),
                team=Team.COUNTER_TERRORIST,
                is_enemy=False,
                weapon=random.choice(["M4A4", "AWP", "USP-S", "Desert Eagle"]),
                angle=random.uniform(0, 360)
            )
            self.players.append(player)
            
    def update_radar(self):
        """Update radar display"""
        if not self.is_running:
            return
            
        # Clear previous markers
        self.radar_canvas.delete("players")
        
        # Draw players
        for player in self.players:
            self.draw_enhanced_player(player)
            
        # Update player list
        self.update_player_list()
        
    def draw_enhanced_player(self, player: Player):
        """Draw an enhanced player marker"""
        # Convert coordinates
        radar_x = self.center_x + (player.x * self.scale)
        radar_y = self.center_y - (player.y * self.scale)
        
        # Clamp to bounds
        radar_x = max(8, min(self.radar_size - 8, radar_x))
        radar_y = max(8, min(self.radar_size - 8, radar_y))
        
        # Choose colors
        if player.is_enemy:
            color = self.settings['enemy_color']
            size = 8
        else:
            color = self.settings['teammate_color']
            size = 6
            
        # Draw player dot
        self.radar_canvas.create_oval(
            radar_x - size, radar_y - size,
            radar_x + size, radar_y + size,
            fill=color, outline="white", width=2, tags="players"
        )
        
        # Draw health bar
        if self.settings['show_health_bars'] and player.health < 100:
            self.draw_health_bar(radar_x, radar_y, player.health, size)
            
        # Draw distance
        if self.settings['show_distance']:
            distance = math.sqrt(player.x**2 + player.y**2)
            self.radar_canvas.create_text(
                radar_x, radar_y + size + 12,
                text=f"{int(distance)}m",
                fill="white", font=("Arial", 8), tags="players"
            )
            
        # Draw weapon info
        if self.settings['show_weapon_info']:
            self.radar_canvas.create_text(
                radar_x, radar_y - size - 12,
                text=player.weapon,
                fill="white", font=("Arial", 7), tags="players"
            )
            
        # Draw direction indicator
        if self.settings['show_angles']:
            end_x = radar_x + math.cos(math.radians(player.angle)) * 15
            end_y = radar_y - math.sin(math.radians(player.angle)) * 15
            self.radar_canvas.create_line(
                radar_x, radar_y, end_x, end_y,
                fill="yellow", width=2, tags="players"
            )
            
    def draw_health_bar(self, x, y, health, size):
        """Draw health bar above player"""
        bar_width = 20
        bar_height = 4
        health_width = int((health / 100) * bar_width)
        
        # Background
        self.radar_canvas.create_rectangle(
            x - bar_width//2, y - size - 15,
            x + bar_width//2, y - size - 11,
            fill="#333333", outline="", tags="players"
        )
        
        # Health fill
        health_color = "#00ff00" if health > 50 else "#ffff00" if health > 25 else "#ff0000"
        self.radar_canvas.create_rectangle(
            x - bar_width//2, y - size - 15,
            x - bar_width//2 + health_width, y - size - 11,
            fill=health_color, outline="", tags="players"
        )
        
    def update_player_list(self):
        """Update the player list display"""
        self.player_listbox.delete(0, tk.END)
        
        for player in self.players:
            team_icon = "🔴" if player.is_enemy else "🔵"
            health_icon = "❤️" if player.health > 50 else "💛" if player.health > 25 else "💔"
            
            info = f"{team_icon} {player.name} {health_icon}{player.health}HP {player.weapon}"
            self.player_listbox.insert(tk.END, info)
            
    def update_statistics(self):
        """Update statistics display"""
        self.stats['total_players'] = len(self.players)
        self.stats['enemies_detected'] = sum(1 for p in self.players if p.is_enemy)
        self.stats['teammates_detected'] = sum(1 for p in self.players if not p.is_enemy)
        self.stats['uptime'] = int(time.time() - self.start_time)
        
        for key, label in self.stats_labels.items():
            label.config(text=f"{key.replace('_', ' ').title()}: {self.stats[key]}")
            
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Radar Settings")
        settings_window.geometry("400x500")
        settings_window.configure(bg="#161b22")
        settings_window.resizable(False, False)
        
        # Settings content
        tk.Label(settings_window, text="Radar Settings", font=("Arial", 16, "bold"), 
                fg="white", bg="#161b22").pack(pady=10)
        
        # Visual settings
        visual_frame = tk.LabelFrame(settings_window, text="Visual Settings", 
                                   fg="white", bg="#161b22", font=("Arial", 12, "bold"))
        visual_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Checkboxes
        self.show_health_var = tk.BooleanVar(value=self.settings['show_health_bars'])
        tk.Checkbutton(visual_frame, text="Show Health Bars", variable=self.show_health_var,
                      fg="white", bg="#161b22", selectcolor="#21262d").pack(anchor=tk.W, padx=5)
        
        self.show_distance_var = tk.BooleanVar(value=self.settings['show_distance'])
        tk.Checkbutton(visual_frame, text="Show Distance", variable=self.show_distance_var,
                      fg="white", bg="#161b22", selectcolor="#21262d").pack(anchor=tk.W, padx=5)
        
        self.show_weapon_var = tk.BooleanVar(value=self.settings['show_weapon_info'])
        tk.Checkbutton(visual_frame, text="Show Weapon Info", variable=self.show_weapon_var,
                      fg="white", bg="#161b22", selectcolor="#21262d").pack(anchor=tk.W, padx=5)
        
        self.show_angles_var = tk.BooleanVar(value=self.settings['show_angles'])
        tk.Checkbutton(visual_frame, text="Show Direction Arrows", variable=self.show_angles_var,
                      fg="white", bg="#161b22", selectcolor="#21262d").pack(anchor=tk.W, padx=5)
        
        # Color settings
        color_frame = tk.LabelFrame(settings_window, text="Color Settings", 
                                  fg="white", bg="#161b22", font=("Arial", 12, "bold"))
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Enemy color
        tk.Label(color_frame, text="Enemy Color:", fg="white", bg="#161b22").pack(anchor=tk.W, padx=5)
        self.enemy_color_var = tk.StringVar(value=self.settings['enemy_color'])
        enemy_color_entry = tk.Entry(color_frame, textvariable=self.enemy_color_var, 
                                   bg="#21262d", fg="white", insertbackground="white")
        enemy_color_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # Teammate color
        tk.Label(color_frame, text="Teammate Color:", fg="white", bg="#161b22").pack(anchor=tk.W, padx=5)
        self.teammate_color_var = tk.StringVar(value=self.settings['teammate_color'])
        teammate_color_entry = tk.Entry(color_frame, textvariable=self.teammate_color_var,
                                      bg="#21262d", fg="white", insertbackground="white")
        teammate_color_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # Save button
        save_button = tk.Button(settings_window, text="Save Settings", 
                               command=lambda: self.save_settings(settings_window),
                               bg="#238636", fg="white", font=("Arial", 12, "bold"),
                               padx=20, pady=5)
        save_button.pack(pady=20)
        
    def save_settings(self, window):
        """Save settings and close window"""
        self.settings['show_health_bars'] = self.show_health_var.get()
        self.settings['show_distance'] = self.show_distance_var.get()
        self.settings['show_weapon_info'] = self.show_weapon_var.get()
        self.settings['show_angles'] = self.show_angles_var.get()
        self.settings['enemy_color'] = self.enemy_color_var.get()
        self.settings['teammate_color'] = self.teammate_color_var.get()
        
        self.save_settings_to_file()
        window.destroy()
        
    def save_settings_to_file(self):
        """Save settings to file"""
        try:
            with open('radar_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('radar_settings.json'):
                with open('radar_settings.json', 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def run(self):
        """Run the enhanced radar application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_radar()
            self.root.quit()

def main():
    """Main function"""
    print("Enhanced CS2 Radar - Educational Project")
    print("=======================================")
    print("This educational project demonstrates:")
    print("- Real-time data visualization")
    print("- GUI development with Python")
    print("- Memory reading concepts")
    print("- Game development principles")
    print()
    print("⚠️  IMPORTANT: Educational use only!")
    print("⚠️  Do not use in actual gameplay!")
    print()
    
    # Create and run enhanced radar
    radar = EnhancedRadar()
    radar.run()

if __name__ == "__main__":
    main()