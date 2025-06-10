import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)


def _find_vlc_path() -> str:
    vlc_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ]
    for path in vlc_paths:
        if os.path.exists(path):
            return path
    return "vlc"  # Default to PATH


def play_song(file_path):
    """Play a song file using VLC or the system default player."""
    try:
        if sys.platform.startswith("win"):
            vlc_cmd = _find_vlc_path()
            try:
                subprocess.Popen([vlc_cmd, "--play-and-exit", file_path], shell=True)
                logger.info(f"Playing song with VLC: {file_path}")
            except (OSError, FileNotFoundError, subprocess.SubprocessError) as e:
                logger.error(f"Failed to play song with VLC: {e}")
                try:
                    os.startfile(file_path)
                    logger.info(f"Playing song with default app: {file_path}")
                except OSError as e2:
                    logger.error(f"Failed to play song with default app: {e2}")
        else:
            try:
                subprocess.Popen(["vlc", "--play-and-exit", file_path])
                logger.info(f"Playing song with VLC: {file_path}")
            except (OSError, FileNotFoundError, subprocess.SubprocessError) as e:
                logger.error(f"Failed to play song with VLC: {e}")
                try:
                    subprocess.Popen(["xdg-open", file_path])
                    logger.info(f"Playing song with xdg-open: {file_path}")
                except OSError as e2:
                    logger.error(f"Failed to play song with xdg-open: {e2}")
    except (OSError, FileNotFoundError) as e:
        logger.error(f"Failed to play song: {e}")


def stop_song():
    """Stop the currently playing song."""
    try:
        if sys.platform.startswith("win"):
            subprocess.call(["taskkill", "/IM", "vlc.exe", "/F"])
            logger.info("Stopped VLC player on Windows.")
        else:
            subprocess.call(["pkill", "vlc"])
            logger.info("Stopped VLC player on Linux/Mac.")
    except (OSError, FileNotFoundError) as e:
        logger.error(f"Failed to stop song: {e}")
