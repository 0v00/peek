import base64
import subprocess

def generate_gif(file_path: str, start_time: float) -> str:
    command = [
        "ffmpeg",
        "-ss", str(start_time),
        "-t", "10",
        "-i", file_path,
        "-vf", "fps=10,scale=320:-1:flags=lanczos",
        "-c:v", "gif",
        "-f", "gif",
        "pipe:1"
    ]
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    base64_encoded_gif = base64.b64encode(proc.stdout).decode('utf-8')
    return base64_encoded_gif

def take_screenshot(file_path: str, time: str) -> bytes:
    command = [
        "ffmpeg",
        "-ss", str(time),
        "-i", file_path,
        "-vframes", "1",
        "-f", "image2pipe",
        "-c:v", "mjpeg",
        "pipe:1"
    ]
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return proc.stdout

def get_movie_duration(file_path: str) -> float:
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return float(proc.stdout)