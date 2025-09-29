#!/usr/bin/env python3
"""
CS2 Mini Radar Demo - Educational Project
=========================================

This is a demonstration version of the CS2 radar that doesn't require
external dependencies. It's perfect for educational purposes and school work.

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
from typing import List, Dict, Tuple, Optional

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
        self.weapon = random.choice(["AK-47", "AWP", "M4A4", "Glock-18", "USP-S"])

class CS2RadarDemo:
    """CS2 Radar Demo Application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS2 Mini Radar Demo - Educational Project")
        self.root.geometry("900x700")
        self.root.configure(bg='#0d1117')
        
        # Radar settings
        self.radar_size = 500
        self.scale = 0.1
        self.center_x = self.radar_size // 2
        self.center_y = self.radar_size // 2
        
        # Game state
        self.players: List[Player] = []
        self.local_player: Optional[Player] = None
        self.is_running = False
        self.update_thread = None
        
        # Statistics
        self.stats = {
            'total_players': 0,
            'enemies_detected': 0,
            'teammates_detected': 0,
            'uptime': 0
        }
        self.start_time = time.time()
        
        # CS2 process simulation
        self.cs2_running = False
        
        self.setup_ui()
        self.setup_radar()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#0d1117')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls
        left_panel = tk.Frame(main_container, bg='#161b22', width=350)
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
            text="CS2 Mini Radar Demo", 
            font=("Arial", 16, "bold"),
            fg="#58a6ff",
            bg="#161b22"
        )
        title_label.pack(pady=10)
        
        # Educational disclaimer
        disclaimer = tk.Label(
            parent,
            text="🎓 EDUCATIONAL PROJECT\n⚠️ Do not use in actual gameplay!",
            font=("Arial", 10),
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
        
        self.simulate_cs2_button = tk.Button(
            control_frame,
            text="🎮 Simulate CS2 Process",
            command=self.toggle_cs2_simulation,
            bg="#6f42c1",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        self.simulate_cs2_button.pack(fill=tk.X, pady=2)
        
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
        
        # CS2 Process Status
        tk.Label(status_frame, text="CS2 Process:", fg="white", bg="#161b22", font=("Arial", 10, "bold")).pack()
        self.cs2_status_label = tk.Label(
            status_frame,
            text="Not Running",
            font=("Arial", 10),
            fg="#f85149",
            bg="#161b22"
        )
        self.cs2_status_label.pack()
        
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
        self.refresh_rate = tk.IntVar(value=100)
        refresh_scale = tk.Scale(
            refresh_frame,
            from_=50,
            to=1000,
            resolution=50,
            orient=tk.HORIZONTAL,
            variable=self.refresh_rate,
            bg="#21262d",
            fg="white",
            highlightbackground="#161b22"
        )
        refresh_scale.pack(fill=tk.X, pady=2)
        
        # Educational info
        info_frame = tk.Frame(parent, bg="#161b22")
        info_frame.pack(pady=10, fill=tk.X)
        
        info_text = """
This demo teaches:
• Real-time visualization
• GUI development
• Memory concepts
• Game programming
• Threading basics
        """
        
        tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            fg="#8b949e",
            bg="#161b22",
            justify=tk.LEFT
        ).pack(padx=5, pady=5)
        
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
        info_frame = tk.Frame(parent, bg="#161b22", height=120)
        info_frame.pack(fill=tk.X, pady=5)
        info_frame.pack_propagate(False)
        
        # Player list
        tk.Label(info_frame, text="Players:", fg="white", bg="#161b22", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        self.player_listbox = tk.Listbox(
            info_frame,
            height=5,
            bg="#21262d",
            fg="white",
            selectbackground="#30363d",
            font=("Consolas", 9)
        )
        self.player_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
    def draw_radar_grid(self):
        """Draw the radar grid"""
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
            distance = i * 200
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
        
    def toggle_cs2_simulation(self):
        """Toggle CS2 process simulation"""
        self.cs2_running = not self.cs2_running
        
        if self.cs2_running:
            self.simulate_cs2_button.config(text="🛑 Stop CS2 Simulation", bg="#f85149")
            self.cs2_status_label.config(text="Running (Simulated)", fg="#3fb950")
        else:
            self.simulate_cs2_button.config(text="🎮 Simulate CS2 Process", bg="#6f42c1")
            self.cs2_status_label.config(text="Not Running", fg="#f85149")
            
    def toggle_radar(self):
        """Toggle radar on/off"""
        if not self.is_running:
            self.start_radar()
        else:
            self.stop_radar()
            
    def start_radar(self):
        """Start the radar"""
        if not self.cs2_running:
            messagebox.showwarning("Warning", "Please start CS2 simulation first!")
            return
            
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
                time.sleep(self.refresh_rate.get() / 1000.0)
            except Exception as e:
                print(f"Error in radar update: {e}")
                time.sleep(1)
                
    def update_game_data(self):
        """Update game data (simulated for educational purposes)"""
        if not self.is_running or not self.cs2_running:
            return
            
        # Clear old players
        self.players.clear()
        
        # Generate simulated enemy positions
        num_enemies = random.randint(1, 6)
        for i in range(num_enemies):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, 1000)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            z = random.uniform(-100, 100)
            
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
            
        # Generate teammates
        num_teammates = random.randint(0, 4)
        for i in range(num_teammates):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 500)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            z = random.uniform(-50, 50)
            
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
            
        # Clear previous markers
        self.radar_canvas.delete("players")
        
        # Draw players
        for player in self.players:
            self.draw_player(player)
            
        # Update player list
        self.update_player_list()
        
    def draw_player(self, player: Player):
        """Draw a player on the radar"""
        # Convert coordinates
        radar_x = self.center_x + (player.x * self.scale)
        radar_y = self.center_y - (player.y * self.scale)
        
        # Clamp to bounds
        radar_x = max(8, min(self.radar_size - 8, radar_x))
        radar_y = max(8, min(self.radar_size - 8, radar_y))
        
        # Choose colors
        if player.is_enemy:
            color = "#FF4444"
            size = 8
        else:
            color = "#4444FF"
            size = 6
            
        # Draw player dot
        self.radar_canvas.create_oval(
            radar_x - size, radar_y - size,
            radar_x + size, radar_y + size,
            fill=color, outline="white", width=2, tags="players"
        )
        
        # Draw health bar
        if player.health < 100:
            bar_width = 20
            bar_height = 4
            health_width = int((player.health / 100) * bar_width)
            
            # Background
            self.radar_canvas.create_rectangle(
                radar_x - bar_width//2, radar_y - size - 12,
                radar_x + bar_width//2, radar_y - size - 8,
                fill="#333333", outline="", tags="players"
            )
            
            # Health fill
            health_color = "#00ff00" if player.health > 50 else "#ffff00" if player.health > 25 else "#ff0000"
            self.radar_canvas.create_rectangle(
                radar_x - bar_width//2, radar_y - size - 12,
                radar_x - bar_width//2 + health_width, radar_y - size - 8,
                fill=health_color, outline="", tags="players"
            )
            
        # Draw distance
        distance = math.sqrt(player.x**2 + player.y**2)
        self.radar_canvas.create_text(
            radar_x, radar_y + size + 12,
            text=f"{int(distance)}m",
            fill="white", font=("Arial", 8), tags="players"
        )
        
        # Draw weapon info
        self.radar_canvas.create_text(
            radar_x, radar_y - size - 20,
            text=player.weapon,
            fill="white", font=("Arial", 7), tags="players"
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
            
    def run(self):
        """Run the radar application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_radar()
            self.root.quit()

def main():
    """Main function"""
    print("CS2 Mini Radar Demo - Educational Project")
    print("=========================================")
    print("This educational project demonstrates:")
    print("- Real-time data visualization")
    print("- GUI development with Python")
    print("- Memory reading concepts")
    print("- Game development principles")
    print()
    print("⚠️  IMPORTANT: Educational use only!")
    print("⚠️  Do not use in actual gameplay!")
    print()
    print("Instructions:")
    print("1. Click 'Simulate CS2 Process' to start simulation")
    print("2. Click 'Start Radar' to begin tracking")
    print("3. Adjust scale and refresh rate as needed")
    print()
    
    # Create and run radar
    radar = CS2RadarDemo()
    radar.run()

if __name__ == "__main__":
    main()