# Abstraction for Wayland/X11 clipboard reading
# Checks if the user is on Wayland ($WAYLAND_DISPLAY) or X11 ($XDG_SESSION_TYPE).
# It then calls the appropriate system tool (wl-paste or xclip) or uses a Python library to return clean, string-formatted text.

import os
import subprocess
import shutil
from time import sleep


class ClipboardError(Exception):
    """raised if the user is missing clipboard dependency"""

    pass


class TimeOutError(Exception):
    """raised if no user input is detected for a while"""


def get_text(exclusive_text: str = "") -> str:
    """
    gets text from clipboard, waiting for user input.
    can pass exclusive_text to omit input equal to the excluded text
    throws timeout and clipboard errors.
    """
    for _ in range(10):
        current_highlight = get_clipboard_content()
        if current_highlight and current_highlight != exclusive_text:
            return current_highlight
        sleep(1)
    raise TimeOutError


def get_clipboard_content() -> str:
    is_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))
    if is_wayland:
        # Ensure wl-clipboard is actually installed
        if not shutil.which("wl-paste"):
            raise ClipboardError(
                "Missing dependency: 'wl-clipboard' is not installed. (e.g., sudo pacman -S wl-clipboard)"
            )
        # Try highlighted text first, fall back to standard clipboard
        try:
            result = subprocess.run(
                ["wl-paste", "-p"], capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

        # Fallback to normal clipboard BLOCKED
        # try:
        #     result = subprocess.run(
        #         ["wl-paste"], capture_output=True, text=True, check=True
        #     )
        #     if result.stdout.strip():
        #         return result.stdout.strip()
        # except subprocess.CalledProcessError:
        #     pass  # Standard clipboard is also empty

    else:
        # X11 approach using xclip
        if not shutil.which("xclip"):
            raise ClipboardError(
                "Missing dependency: 'xclip' is not installed. (e.g., sudo pacman -S xclip)"
            )
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
        # # Fallback to standard clipboard BLOCKED
        # try:
        #     result = subprocess.run(
        #         ["xclip", "-o", "-selection", "clipboard"],
        #         capture_output=True,
        #         text=True,
        #         check=True
        #     )
        #     if result.stdout.strip():
        #         return result.stdout.strip()
        # except subprocess.CalledProcessError:
        #     pass
    # blank return otherwise
    return ""
    # raise ClipboardError("No text found in primary selection.")


def copy_to_clipboard(message: str):
    """sends a message to store in the clipboard"""
    if os.environ.get("WAYLAND_DISPLAY"):
        clipboard_cmd = ["wl-copy"]
    else:
        clipboard_cmd = ["xclip", "-selection", "clipboard"]
    # Push the translation to the clipboard
    subprocess.run(clipboard_cmd, input=message, text=True, check=True)
