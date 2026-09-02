import subprocess
import shutil
import sys

from wordflow.clipboard import copy_to_clipboard


def notify(
    title: str,
    message: str,
    urgency: str = "normal",
    timeout: int = 5000,
    enable_notifications=True,
    copy_output_to_clipboard=False,
):
    """
    Sends a Linux desktop notification using notify-send, or simply prints message to terminal
    """
    if not enable_notifications:
        print(title, "\n", message)
        return

    # Check if notify-send is installed on the user's system
    if not shutil.which("notify-send"):
        print(
            f"[Warning] 'notify-send' is not installed. Missing notification: {title}",
            file=sys.stderr,
        )
        return

    try:
        if not copy_output_to_clipboard:
            subprocess.run(
                [
                    "notify-send",
                    "-a",
                    "Wordflow",  # App name shown in notification center
                    "-u",
                    urgency,  # Urgency: low, normal, critical
                    "-t",
                    str(timeout),  # Timeout in milliseconds
                    title,
                    message,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            process = subprocess.run(
                [
                    "notify-send",
                    "-a",
                    "Wordflow",
                    "--action=default=Copy",
                    "--wait",
                    "-u",
                    urgency,
                    "-t",
                    str(timeout),
                    title,
                    message,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            if process.stdout.strip() == "default":
                # Push the translation to the Wayland clipboard
                copy_to_clipboard(message)

    except subprocess.CalledProcessError as e:
        print(
            f"[Warning] Notification daemon error: {e.stderr.strip()}", file=sys.stderr
        )
    except Exception as e:
        print(f"[Warning] Failed to send notification '{title}': {e}", file=sys.stderr)
