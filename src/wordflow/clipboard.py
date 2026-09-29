# Abstraction for Wayland/X11 clipboard reading
# Checks if the user is on Wayland ($WAYLAND_DISPLAY) or X11 ($XDG_SESSION_TYPE).
# It then calls the appropriate system tool (wl-paste or xclip) or uses a Python library to return clean, string-formatted text.

import os
import sys
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
    # transfer highlighted text to clipboard
    simulate_copy()

    for _ in range(10):
        current_highlight = get_clipboard_content()
        if current_highlight and current_highlight != exclusive_text:
            return current_highlight
        sleep(1)
    raise TimeOutError


def get_clipboard_content() -> str:
    """Reads from the OS-specific clipboard."""

    # macOS
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["pbpaste"], capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

    # Windows
    elif sys.platform == "win32":
        try:
            # -NoProfile prevents loading powershell profile scripts, making it much faster
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
    else:
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


def copy_to_clipboard(message: str):
    """sends a message to store in the clipboard"""
    # MacOS
    if sys.platform == "darwin":
        clipboard_cmd = ["pbcopy"]
    # Windows
    elif sys.platform == "win32":
        clipboard_cmd = ["clip"]
    else:
        # Linux
        if os.environ.get("WAYLAND_DISPLAY"):
            clipboard_cmd = ["wl-copy"]
        else:
            clipboard_cmd = ["xclip", "-selection", "clipboard"]

    subprocess.run(clipboard_cmd, input=message, text=True, check=True)


def simulate_copy():
    """
    Simulates the native copy keystroke (Cmd+C / Ctrl+C) on macOS and Windows
    to mimic Linux's primary selection behavior.
    """
    if sys.platform == "darwin":
        # macOS: Use built-in AppleScript to send Cmd+C
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to keystroke "c" using command down',
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            pass

    elif sys.platform == "win32":
        # Windows: Use ctypes to call the native Windows API for keystrokes
        import ctypes

        VK_CONTROL = 0x11
        VK_C = 0x43
        KEYEVENTF_KEYUP = 0x0002

        user32 = ctypes.windll.user32

        # Press Ctrl
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        # Press C
        user32.keybd_event(VK_C, 0, 0, 0)
        # Release C
        user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
        # Release Ctrl
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    if sys.platform in ["darwin", "win32"]:
        sleep(0.1)
