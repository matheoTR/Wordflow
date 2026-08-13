import subprocess
import shutil


def send_notification(title: str, message: str, urgency: str = "normal"):
    """
    Sends a Linux desktop notification using notify-send.
    """
    # Check if notify-send is installed on the user's system
    if not shutil.which("notify-send"):
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
                "5000",  # Timeout in milliseconds
                title,
                message,
            ],
            check=False,
        )
    except Exception:
        # Prevent notification failures from breaking the core Anki/Translation workflow
        pass
