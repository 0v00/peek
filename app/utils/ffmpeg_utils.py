import subprocess

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