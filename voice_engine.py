import asyncio
import edge_tts

async def create_voiceover(
    full_text: str,
    voice: str = "en-US-ChristopherNeural",
    audio_path: str = "voice.mp3",
    srt_path: str = "subs.srt"
):
    communicate = edge_tts.Communicate(full_text, voice)
    submaker = edge_tts.SubMaker()

    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(submaker.get_srt())

def generate_voice(full_text: str, language: str = "en"):
    # English default: en-US-ChristopherNeural
    # Persian default: fa-IR-FaridNeural
    voice = "fa-IR-FaridNeural" if language == "fa" else "en-US-ChristopherNeural"
    asyncio.run(create_voiceover(full_text, voice=voice))
