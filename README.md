# CS2 Mini Radar - Educational Project

A real-time radar overlay for Counter-Strike 2 created for educational purposes.

## ⚠️ IMPORTANT DISCLAIMER

**This tool is created for educational and research purposes only.** 

- Using external tools with Counter-Strike 2 may violate the game's Terms of Service
- This could result in VAC bans or other account penalties
- Use at your own risk
- The author is not responsible for any consequences

## Features

- Real-time enemy position tracking
- Team member display (toggleable)
- Multiple CS2 map support
- Clean, modern radar interface
- FPS counter and connection status
- Grid overlay for better positioning

## Requirements

- Windows OS (for memory access)
- Python 3.7+
- Counter-Strike 2 installed and running
- Administrator privileges (for memory reading)

## Installation

1. Clone or download this project
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start Counter-Strike 2
2. Run the radar as administrator:
   ```bash
   python main.py
   ```

## Controls

- **ESC** - Exit radar
- **G** - Toggle grid display
- **T** - Toggle teammate display

## How It Works

The radar works by:

1. **Memory Reading**: Connects to the CS2 process and reads game memory
2. **Entity Parsing**: Extracts player positions, health, and team information
3. **Coordinate Conversion**: Converts 3D world coordinates to 2D radar positions
4. **Real-time Display**: Updates the radar display at 60 FPS

## Technical Details

### Memory Offsets

The application uses current CS2 memory offsets to access:
- Player entity list
- Local player information
- World coordinates
- Health and team data

### Supported Maps

- de_dust2
- de_mirage  
- de_inferno
- de_cache

Additional maps can be added by updating the `MAP_BOUNDS` in `offsets.py`.

## Project Structure

```
cs2-mini-radar/
├── main.py              # Main application entry point
├── memory_reader.py     # CS2 memory access functionality
├── entity_parser.py     # Game entity processing
├── radar_gui.py         # Pygame-based radar display
├── offsets.py           # CS2 memory offsets and constants
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Educational Value

This project demonstrates:

- **Memory Management**: Reading external process memory
- **Game Development**: Understanding game engine data structures
- **Real-time Systems**: Processing and displaying data at high frame rates
- **Coordinate Systems**: Converting between 3D world and 2D screen coordinates
- **GUI Programming**: Creating responsive user interfaces

## Troubleshooting

### "CS2 process not found"
- Make sure Counter-Strike 2 is running
- Run the radar as administrator
- Check that the process name matches your CS2 installation

### "Failed to get client.dll"
- Ensure CS2 is fully loaded (not just in menu)
- Try running as administrator
- Check if antivirus is blocking memory access

### Radar shows no players
- Verify you're in an active game (not menu/lobby)
- Check that the memory offsets are current
- Ensure the map is supported

## Updating Offsets

CS2 updates frequently change memory offsets. To update:

1. Find current offsets using tools like cs2-dumper
2. Update values in `offsets.py`
3. Test with the new game version

## Legal and Ethical Considerations

- This tool is for educational purposes only
- Do not use in competitive matches
- Respect other players and fair play
- Consider the impact on game integrity
- Always follow your local laws and game ToS

## Contributing

This is an educational project. Contributions should focus on:
- Code quality improvements
- Educational documentation
- Bug fixes
- Performance optimizations

## License

This project is provided as-is for educational purposes. Use responsibly.

---

**Remember**: The goal of this project is learning, not gaining unfair advantages in games. Use it to understand game development, memory management, and real-time systems programming.