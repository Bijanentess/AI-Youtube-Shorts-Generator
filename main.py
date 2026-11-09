import os
import json
from gemini_engine import generate_short_content
from voice_engine import generate_voice
from video_engine import render_final_video
from youtube_uploader import upload_short

def main():
    lang = os.environ.get("SHORTS_LANG", "en")
    print(f"1. Asking Gemini 3.8 Flash for trending topic (Language: {lang})...")
    short_data = generate_short_content(language=lang)
    print(f"Topic: {short_data.topic}")
    print(f"Title: {short_data.title}")

    full_voice_text = " ".join([s.text for s in short_data.scenes])

    print("2. Generating voiceover and dynamic subtitles...")
    generate_voice(full_voice_text, language=lang)

    print("3. Fetching stock videos and rendering 9:16 vertical Short...")
    render_final_video(short_data.scenes, "final_short.mp4")

    print("4. Uploading directly to YouTube channel...")
    video_id = upload_short(
        video_file="final_short.mp4",
        title=short_data.title,
        description=short_data.description,
        tags=short_data.tags
    )

    used = []
    if os.path.exists("used_topics.json"):
        with open("used_topics.json", "r", encoding="utf-8") as f:
            try:
                used = json.load(f)
            except Exception:
                pass
    used.append(short_data.topic)
    with open("used_topics.json", "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)

    print(f"Done! https://youtube.com/shorts/{video_id}")

if __name__ == "__main__":
    main()
