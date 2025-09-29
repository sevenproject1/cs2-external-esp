#!/usr/bin/env python3
"""
CS2 Radar Launcher - Educational Project
========================================

This launcher script provides an easy way to run different versions
of the CS2 radar application for educational purposes.

IMPORTANT: This is for educational purposes only!
Do not use in actual gameplay.
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def show_launcher():
    """Show the radar launcher interface"""
    root = tk.Tk()
    root.title("CS2 Radar Launcher - Educational Project")
    root.geometry("500x400")
    root.configure(bg='#0d1117')
    root.resizable(False, False)
    
    # Title
    title_label = tk.Label(
        root,
        text="CS2 Radar Launcher",
        font=("Arial", 20, "bold"),
        fg="#58a6ff",
        bg="#0d1117"
    )
    title_label.pack(pady=20)
    
    # Educational disclaimer
    disclaimer = tk.Label(
        root,
        text="🎓 EDUCATIONAL PROJECT\n⚠️ Do not use in actual gameplay!",
        font=("Arial", 12),
        fg="#f85149",
        bg="#0d1117",
        justify=tk.CENTER
    )
    disclaimer.pack(pady=10)
    
    # Description
    desc_label = tk.Label(
        root,
        text="Choose a radar version to run:",
        font=("Arial", 12),
        fg="white",
        bg="#0d1117"
    )
    desc_label.pack(pady=10)
    
    # Button frame
    button_frame = tk.Frame(root, bg="#0d1117")
    button_frame.pack(pady=20)
    
    # Basic radar button
    basic_button = tk.Button(
        button_frame,
        text="🚀 Basic Radar\n(Simple version)",
        command=lambda: run_radar("basic"),
        bg="#238636",
        fg="white",
        font=("Arial", 12, "bold"),
        padx=20,
        pady=10,
        width=15
    )
    basic_button.pack(pady=10)
    
    # Enhanced radar button
    enhanced_button = tk.Button(
        button_frame,
        text="⭐ Enhanced Radar\n(Advanced features)",
        command=lambda: run_radar("enhanced"),
        bg="#6f42c1",
        fg="white",
        font=("Arial", 12, "bold"),
        padx=20,
        pady=10,
        width=15
    )
    enhanced_button.pack(pady=10)
    
    # Memory reader button
    memory_button = tk.Button(
        button_frame,
        text="🔍 Memory Reader\n(Educational module)",
        command=lambda: run_radar("memory"),
        bg="#f85149",
        fg="white",
        font=("Arial", 12, "bold"),
        padx=20,
        pady=10,
        width=15
    )
    memory_button.pack(pady=10)
    
    # Info frame
    info_frame = tk.Frame(root, bg="#161b22")
    info_frame.pack(fill=tk.X, padx=20, pady=20)
    
    info_text = """
This educational project demonstrates:
• Real-time data visualization
• GUI development with Python
• Memory reading concepts
• Game development principles
• Threading and concurrency

Choose a version above to start learning!
    """
    
    info_label = tk.Label(
        info_frame,
        text=info_text,
        font=("Arial", 10),
        fg="#8b949e",
        bg="#161b22",
        justify=tk.LEFT
    )
    info_label.pack(padx=10, pady=10)
    
    # Exit button
    exit_button = tk.Button(
        root,
        text="Exit",
        command=root.quit,
        bg="#6e7681",
        fg="white",
        font=("Arial", 10),
        padx=20,
        pady=5
    )
    exit_button.pack(pady=10)
    
    root.mainloop()

def run_radar(version):
    """Run the specified radar version"""
    try:
        if version == "basic":
            subprocess.run([sys.executable, "cs2_radar.py"])
        elif version == "enhanced":
            subprocess.run([sys.executable, "enhanced_radar.py"])
        elif version == "memory":
            subprocess.run([sys.executable, "memory_reader.py"])
        else:
            messagebox.showerror("Error", "Invalid radar version selected!")
    except FileNotFoundError:
        messagebox.showerror("Error", f"Could not find {version}_radar.py file!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run radar: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import psutil
        return True
    except ImportError:
        return False

def main():
    """Main function"""
    print("CS2 Radar Launcher - Educational Project")
    print("=======================================")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Missing dependencies!")
        print("Please install required packages:")
        print("pip install psutil")
        print()
        return
    
    print("✅ Dependencies OK")
    print("🚀 Starting radar launcher...")
    print()
    
    # Show launcher interface
    show_launcher()

if __name__ == "__main__":
    main()