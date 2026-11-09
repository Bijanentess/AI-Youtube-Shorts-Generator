import os
import requests
import subprocess

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def download_stock_video(query: str, output_path: str):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait"
    
    try:
        res = requests.get(url, headers=headers, timeout=20).json()
        videos = res.get("videos", [])
    except Exception:
        videos = []

    if not videos:
        # Fallback query
        res = requests.get("https://api.pexels.com/videos/search?query=nature+timelapse&orientation=portrait", headers=headers, timeout=20).json()
        videos = res.get("videos", [])

    video_files = videos[0]["video_files"]
    # Pick portrait file
    portrait_video = next((v for v in video_files if v.get("width", 0) <= 1080 and v.get("height", 0) >= 1920), video_files[0])
    
    with requests.get(portrait_video["link"], stream=True, timeout=30) as r:
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def vtt_to_ass(vtt_path: str, ass_path: str):
    """Convert VTT to ASS subtitle format with viral Shorts typography."""
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,65,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,5,40,40,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    subprocess.run(["ffmpeg", "-y", "-i", vtt_path, ass_path], check=True)
    with open(ass_path, "r", encoding="utf-8") as f:
        content = f.read()

    events_idx = content.find("[Events]")
    if events_idx != -1:
        styled_ass = ass_header + content[events_idx + 8:]
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(styled_ass)

def render_final_video(scenes: list, output_video: str = "final_short.mp4"):
    clip_files = []
    for idx, scene in enumerate(scenes):
        clip_path = f"clip_{idx}.mp4"
        download_stock_video(scene.search_keyword, clip_path)
        clip_files.append(clip_path)

    with open("clips.txt", "w") as f:
        for c in clip_files:
            f.write(f"file '{c}'\n")

    # Merge clips into a unified 1080x1920 canvas
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clips.txt",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "merged_bg.mp4"
    ], check=True)

    vtt_to_ass("subs.vtt", "subs.ass")

    # Combine video background, audio voiceover and burnt-in subtitles
    subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", "merged_bg.mp4",
        "-i", "voice.mp3",
        "-vf", "ass=subs.ass",
        "-c:v", "libx264", "-c:a", "aac",
        "-shortest",
        output_video
    ], check=True)
