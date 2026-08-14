# Abstraction for Wayland/X11 clipboard reading
# Checks if the user is on Wayland ($WAYLAND_DISPLAY) or X11 ($XDG_SESSION_TYPE).
# It then calls the appropriate system tool (wl-paste or xclip) or uses a Python library to return clean, string-formatted text.

import os
import subprocess
import shutil

class ClipboardError(Exception):
    """raised if the user is missing clipboard dependency"""
    pass

def get_text() -> str:
    is_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))
    if is_wayland:
        # Ensure wl-clipboard is actually installed
        if not shutil.which("wl-paste"):
            raise ClipboardError("Missing dependency: 'wl-clipboard' is not installed. (e.g., sudo pacman -S wl-clipboard)")
        # Try highlighted text first, fall back to standard clipboard
        try:
            result = subprocess.run(
                ["wl-paste", "-p"], capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

        # Fallback to normal clipboard
        try:
            result = subprocess.run(
                ["wl-paste"], capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass  # Standard clipboard is also empty

    else:
        # X11 approach using xclip
        if not shutil.which("xclip"):
            raise ClipboardError("Missing dependency: 'xclip' is not installed. (e.g., sudo pacman -S xclip)")
        try:
            result = subprocess.run(
                ["xclip", "-o", "-selection", "primary"],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
        # Fallback to standard clipboard
        try:
            result = subprocess.run(
                ["xclip", "-o", "-selection", "clipboard"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

    raise ClipboardError("No text found in primary selection or standard clipboard.")
