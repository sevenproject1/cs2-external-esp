"""
CS2 Mini Radar - Main Application
Educational CS2 radar for school project

IMPORTANT DISCLAIMER:
This tool is created for educational purposes only. 
Use at your own risk. Using external tools with CS2 may violate 
the game's terms of service and could result in account penalties.
"""

import time
import sys
import traceback
from typing import Optional

from memory_reader import CS2MemoryReader
from entity_parser import EntityParser
from radar_gui import RadarGUI

class CS2MiniRadar:
    def __init__(self):
        self.memory_reader = CS2MemoryReader()
        self.entity_parser = None
        self.radar_gui = RadarGUI()
        self.running = False
        
        # Performance settings
        self.update_rate = 60  # FPS
        self.retry_connection_interval = 5.0  # seconds
        self.last_connection_attempt = 0
        
        print("="*60)
        print("CS2 Mini Radar - Educational Version")
        print("="*60)
        print("DISCLAIMER: This tool is for educational purposes only!")
        print("Use at your own risk. May violate game ToS.")
        print("="*60)
    
    def initialize(self) -> bool:
        """Initialize the radar system"""
        print("Initializing CS2 Mini Radar...")
        
        # Try to connect to CS2
        if not self.connect_to_game():
            print("Failed to connect to CS2. Make sure the game is running.")
            return False
        
        # Initialize entity parser
        self.entity_parser = EntityParser(self.memory_reader)
        
        print("Radar initialized successfully!")
        print("\nControls:")
        print("- ESC: Exit radar")
        print("- G: Toggle grid display")
        print("- T: Toggle teammate display")
        print("\nStarting radar loop...")
        
        return True
    
    def connect_to_game(self) -> bool:
        """Attempt to connect to CS2"""
        current_time = time.time()
        
        # Don't retry too frequently
        if current_time - self.last_connection_attempt < self.retry_connection_interval:
            return self.memory_reader.connected
        
        self.last_connection_attempt = current_time
        
        if not self.memory_reader.connected:
            print("Attempting to connect to CS2...")
            return self.memory_reader.connect_to_cs2()
        
        return True
    
    def update_radar_data(self) -> tuple:
        """Update radar data and return player information"""
        try:
            # Get all players
            players = self.entity_parser.get_all_players()
            
            # Get local player
            local_player = self.entity_parser.get_local_player_info()
            
            # Get player counts
            player_count = self.entity_parser.get_player_count()
            
            # Get current map (simplified)
            current_map = self.entity_parser.current_map
            
            return players, local_player, player_count, current_map
            
        except Exception as e:
            print(f"Error updating radar data: {e}")
            return [], None, {'enemies': 0, 'teammates': 0, 'total': 0}, "unknown"
    
    def run(self):
        """Main radar loop"""
        if not self.initialize():
            return False
        
        self.running = True
        last_update = time.time()
        
        try:
            while self.running:
                current_time = time.time()
                
                # Handle pygame events
                if not self.radar_gui.handle_events():
                    self.running = False
                    break
                
                # Check connection status
                if not self.memory_reader.connected:
                    if not self.connect_to_game():
                        # Show disconnected state
                        self.radar_gui.render_frame(
                            [], None, 
                            {'enemies': 0, 'teammates': 0, 'total': 0},
                            False, "disconnected"
                        )
                        self.radar_gui.run_frame(self.update_rate)
                        continue
                    else:
                        # Reconnected, reinitialize parser
                        self.entity_parser = EntityParser(self.memory_reader)
                
                # Update radar data
                players, local_player, player_count, current_map = self.update_radar_data()
                
                # Render frame
                self.radar_gui.render_frame(
                    players, local_player, player_count, 
                    self.memory_reader.connected, current_map
                )
                
                # Control frame rate
                self.radar_gui.run_frame(self.update_rate)
                
                # Print debug info occasionally
                if current_time - last_update >= 5.0:
                    print(f"Radar Update - Players: {player_count['total']}, "
                          f"Enemies: {player_count['enemies']}, "
                          f"Teammates: {player_count['teammates']}")
                    last_update = current_time
                    
        except KeyboardInterrupt:
            print("\nShutting down radar (Ctrl+C pressed)")
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            traceback.print_exc()
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        
        if self.memory_reader:
            self.memory_reader.disconnect()
        
        if self.radar_gui:
            self.radar_gui.cleanup()
        
        print("Cleanup complete. Goodbye!")

def main():
    """Entry point"""
    # Check if running on Windows (required for memory reading)
    if sys.platform != "win32":
        print("Warning: This radar is designed for Windows. "
              "Memory reading may not work on other platforms.")
    
    # Create and run radar
    radar = CS2MiniRadar()
    
    try:
        success = radar.run()
        if not success:
            print("Failed to start radar. Check if CS2 is running and try again.")
            return 1
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)