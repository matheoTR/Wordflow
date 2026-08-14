import subprocess
import shutil
import sys

def send_notification(title: str, message: str, urgency: str = "normal", timeout: int = 5000):
    """
    Sends a Linux desktop notification using notify-send.
    """
    # Check if notify-send is installed on the user's system
    if not shutil.which("notify-send"):
        print(f"[Warning] 'notify-send' is not installed. Missing notification: {title}", file=sys.stderr)
        return

    try:
        subprocess.run(
            [
                "notify-send",
                "-a",
                "foo",  # App name shown in notification center
                "-u",
                urgency,  # Urgency: low, normal, critical
                "-t",
                str(timeout),  # Timeout in milliseconds
                title,
                message,
            ],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[Warning] Notification daemon error: {e.stderr.strip()}", file=sys.stderr)
    except Exception as e:
        print(f"[Warning] Failed to send notification '{title}': {e}", file=sys.stderr)
