import os
import json
from google import genai
from pydantic import BaseModel, Field

class Scene(BaseModel):
    text: str = Field(description="Sentence of voiceover script")
    search_keyword: str = Field(description="1-2 English words for stock footage search, e.g. 'deep ocean', 'galaxy nebula'")

class ShortPayload(BaseModel):
    topic: str = Field(description="Topic name")
    title: str = Field(description="Viral YouTube Shorts title with #Shorts")
    description: str = Field(description="SEO optimized description with tags")
    tags: list[str] = Field(description="5 to 8 trending tags")
    scenes: list[Scene] = Field(description="4 to 6 scenes forming a 35-45 second video")

def generate_short_content(language: str = "en") -> ShortPayload:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)

    used = []
    if os.path.exists("used_topics.json"):
        with open("used_topics.json", "r", encoding="utf-8") as f:
            try:
                used = json.load(f)
            except Exception:
                pass

    lang_instruction = "English for narration text" if language == "en" else "Persian (Farsi) for narration text"

    prompt = f"""
    You are a viral YouTube Shorts creator. Choose a fascinating, mind-blowing, or bizarre topic 
    in science, psychology, bizarre history, or cosmic mysteries that is completely unique.
    Already used topics to AVOID: {used[-30:]}

    Language: {lang_instruction}.
    Rules:
    1. Hook the viewer in the first 3 seconds.
    2. Total reading duration must be around 35 to 45 seconds (approx 80-110 words total).
    3. Break it down into 4-6 scenes. For each scene provide 'text' and a high-relevance 'search_keyword' (in English) for stock video clips.
    4. Provide a click-worthy title with #Shorts, engaging description, and tags.
    """

    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ShortPayload.model_json_schema()
        }
    )

    data = ShortPayload.model_validate_json(interaction.output_text)
    return data
