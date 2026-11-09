import os
import random
import requests
import subprocess
import glob

# Optional: If PEXELS_API_KEY is provided, it can be used. Otherwise, zero-key fallbacks are used.
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "").strip()

# High-quality direct public domain / CC0 vertical/landscape background loops (Nature, Galaxy, Cosmic)
DEFAULT_VIDEO_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c0/Big_Buck_Bunny_4K.webm/Big_Buck_Bunny_4K.webm.360p.vp9.webm",
]

def get_local_asset_video() -> str | None:
    """Check if the user placed any custom video or gameplay in assets/ directory."""
    asset_files = glob.glob("assets/*.mp4") + glob.glob("assets/*.webm") + glob.glob("assets/*.mov")
    if asset_files:
        return random.choice(asset_files)
    return None

def download_pexels_video(query: str, output_path: str) -> bool:
    """Download vertical video from Pexels if API key is provided."""
    if not PEXELS_API_KEY:
        return False
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait"
        res = requests.get(url, headers=headers, timeout=15).json()
        videos = res.get("videos", [])
        if not videos:
            return False
        video_files = videos[0].get("video_files", [])
        if not video_files:
            return False
        # Pick best resolution portrait
        chosen = next((v for v in video_files if v.get("width", 0) <= 1080 and v.get("height", 0) >= 1920), video_files[0])
        with requests.get(chosen["link"], stream=True, timeout=25) as r:
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=16384):
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Pexels fetch error ({e}), falling back...")
        return False

def generate_procedural_background(output_path: str, duration: int = 45):
    """Generate a stunning dynamic ambient vertical motion background via pure FFmpeg (Zero API needed)."""
    # Dynamic dark nebula / synthwave color gradients
    c0 = random.choice(["0x1a0933", "0x0a192f", "0x1b1035", "0x0f2027", "0x141e30"])
    c1 = random.choice(["0x3b156b", "0x162447", "0x1f4068", "0x203a43", "0x243b55"])
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"gradients=s=1080x1920:r=30:c0={c0}:c1={c1}:x0=0:y0=0:x1=1080:y1=1920,noise=alls=12:allf=t+u",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    subprocess.run(cmd, check=True)

def vtt_to_ass(vtt_path: str, ass_path: str):
    """Convert VTT subtitles to viral ASS style (Impact font, yellow text, bold black outline, centered)."""
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,68,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,5,40,40,960,1

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
    """Assemble final 9:16 vertical short video with voiceover and captions."""
    local_bg = get_local_asset_video()
    
    if local_bg:
        print(f"🎮 Using local background asset: {local_bg}")
        # Crop to 1080x1920
        subprocess.run([
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", local_bg,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-t", "60",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "merged_bg.mp4"
        ], check=True)
    elif PEXELS_API_KEY:
        print("🔍 Downloading clips from Pexels...")
        clip_files = []
        for idx, scene in enumerate(scenes):
            clip_path = f"clip_{idx}.mp4"
            ok = download_pexels_video(scene.search_keyword, clip_path)
            if ok:
                clip_files.append(clip_path)

        if clip_files:
            with open("clips.txt", "w") as f:
                for c in clip_files:
                    f.write(f"file '{c}'\n")

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clips.txt",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "merged_bg.mp4"
            ], check=True)
        else:
            print("⚡ Generating aesthetic procedural background...")
            generate_procedural_background("merged_bg.mp4", duration=50)
    else:
        print("⚡ No Pexels key provided. Generating high-retention aesthetic background automatically...")
        generate_procedural_background("merged_bg.mp4", duration=50)

    # Style subtitles
    vtt_to_ass("subs.vtt", "subs.ass")

    # Combine video background, audio voiceover and burnt-in subtitles
    print("🎬 Merging audio, video and subtitles...")
    subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", "merged_bg.mp4",
        "-i", "voice.mp3",
        "-vf", "ass=subs.ass",
        "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac",
        "-shortest",
        output_video
    ], check=True)
    print("✅ Final video rendered successfully!")
