"""
CS2 Mini Radar Installation Script
Installs dependencies and checks system requirements
"""

import sys
import subprocess
import platform
import os

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_operating_system():
    """Check if running on Windows"""
    system = platform.system()
    if system != "Windows":
        print(f"⚠️  Warning: This radar is designed for Windows. Current OS: {system}")
        print("Memory reading functionality may not work on other platforms.")
        return False
    
    print(f"✅ Running on {system} - compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("✅ Running with administrator privileges")
        else:
            print("⚠️  Warning: Not running as administrator")
            print("Memory reading may fail. Consider running as administrator.")
        return is_admin
    except:
        print("⚠️  Could not check administrator privileges")
        return False

def create_launcher_script():
    """Create a convenient launcher script"""
    launcher_content = '''@echo off
echo Starting CS2 Mini Radar...
echo Make sure CS2 is running first!
echo.
python main.py
pause
'''
    
    try:
        with open("start_radar.bat", "w") as f:
            f.write(launcher_content)
        print("✅ Created start_radar.bat launcher script")
        return True
    except Exception as e:
        print(f"⚠️  Could not create launcher script: {e}")
        return False

def main():
    """Main installation function"""
    print("="*60)
    print("CS2 Mini Radar - Installation & Setup")
    print("="*60)
    print("This will check system requirements and install dependencies.")
    print()
    
    # Check system requirements
    python_ok = check_python_version()
    windows_ok = check_operating_system()
    
    if not python_ok:
        print("\n❌ System requirements not met. Please upgrade Python.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check your internet connection.")
        return False
    
    # Check admin privileges
    check_admin_privileges()
    
    # Create launcher
    create_launcher_script()
    
    print("\n" + "="*60)
    print("✅ Installation completed successfully!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Start Counter-Strike 2")
    print("2. Run: python main.py (or double-click start_radar.bat)")
    print("3. Use ESC to exit, G to toggle grid, T to toggle teammates")
    print()
    print("⚠️  IMPORTANT DISCLAIMER:")
    print("This tool is for educational purposes only!")
    print("Using external tools may violate CS2's Terms of Service.")
    print("Use at your own risk!")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Installation failed. Please check the errors above.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    input("Press Enter to exit...")