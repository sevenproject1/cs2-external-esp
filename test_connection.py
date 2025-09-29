"""
CS2 Connection Test
Tests if the radar can connect to CS2 and read basic information
"""

import time
import sys
from memory_reader import CS2MemoryReader
from entity_parser import EntityParser

def test_connection():
    """Test connection to CS2"""
    print("CS2 Connection Test")
    print("="*50)
    
    # Create memory reader
    memory_reader = CS2MemoryReader()
    
    print("Attempting to connect to CS2...")
    
    # Try to connect
    if not memory_reader.connect_to_cs2():
        print("❌ Failed to connect to CS2")
        print("\nTroubleshooting:")
        print("1. Make sure Counter-Strike 2 is running")
        print("2. Run this script as administrator")
        print("3. Check if CS2 is fully loaded (not just in menu)")
        return False
    
    print("✅ Successfully connected to CS2!")
    
    # Test basic memory reading
    print("\nTesting memory reading...")
    
    try:
        # Test local player
        local_player = memory_reader.get_local_player()
        if local_player:
            print(f"✅ Local player found at address: 0x{local_player:X}")
        else:
            print("⚠️  Local player not found (might be in menu)")
        
        # Test entity list
        entities = memory_reader.get_entity_list()
        print(f"✅ Found {len(entities)} entities")
        
        # Test entity parser
        entity_parser = EntityParser(memory_reader)
        players = entity_parser.get_all_players()
        player_count = entity_parser.get_player_count()
        
        print(f"✅ Found {player_count['total']} players:")
        print(f"   - Enemies: {player_count['enemies']}")
        print(f"   - Teammates: {player_count['teammates']}")
        
        # Test local player info
        local_info = entity_parser.get_local_player_info()
        if local_info:
            print(f"✅ Local player info:")
            print(f"   - Position: ({local_info['x']:.1f}, {local_info['y']:.1f}, {local_info['z']:.1f})")
            print(f"   - Health: {local_info['health']}")
            print(f"   - Team: {local_info['team']}")
        
        print("\n✅ All tests passed! The radar should work correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    finally:
        memory_reader.disconnect()
        print("\nDisconnected from CS2")
    
    return True

def main():
    """Main test function"""
    print("This script will test if the CS2 radar can connect to the game.")
    print("Make sure Counter-Strike 2 is running before continuing.")
    print()
    
    input("Press Enter to start the test...")
    print()
    
    success = test_connection()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Connection test successful!")
        print("You can now run the full radar with: python main.py")
    else:
        print("❌ Connection test failed.")
        print("Please check the troubleshooting steps above.")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()