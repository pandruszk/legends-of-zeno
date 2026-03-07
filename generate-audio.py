#!/usr/bin/env python3
"""Generate narration audio for Legends of Zeno using ElevenLabs"""
import json
import os
import re
import requests

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_e9b275e43b3c3cf61f95d90d4990b0570630ee2ca197c730")
VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"  # Josh
MODEL = "eleven_multilingual_v2"
OUTPUT_DIR = "audio"

VOICE_SETTINGS = {
    "stability": 0.6,
    "similarity_boost": 0.8,
    "style": 0.4
}

def strip_html(html):
    return re.sub(r'<[^>]+>', ' ', html).replace('&mdash;', '—').replace('&nbsp;', ' ').replace('  ', ' ').strip()

def get_narration(slide):
    # Use the narration field if present (short voiceover script)
    if slide.get("narration"):
        return slide["narration"]
    # Fallback for legacy slides without narration
    t = slide.get("type", "")
    if t == "title":
        return f"{slide['heading']}... {slide['subheading']}"
    elif t == "narrative":
        return strip_html(slide["text"])
    elif t == "agents":
        return f"{slide['heading']}... {slide['subheading']}"
    elif t == "tips":
        return f"{slide['heading']}... {slide['subheading']}"
    elif t == "cta":
        return f"{slide['heading']}... {slide['subheading']}"
    return ""

def generate_audio(text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": MODEL,
        "voice_settings": VOICE_SETTINGS
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True
    else:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open("data/legends.json") as f:
        legends = json.load(f)

    for legend in legends:
        lid = legend["id"]
        for i, slide in enumerate(legend["slides"]):
            text = get_narration(slide)
            if not text:
                continue
            outfile = os.path.join(OUTPUT_DIR, f"{lid}-{i}.mp3")
            print(f"Generating {outfile} ({len(text)} chars)...")
            if generate_audio(text, outfile):
                size_kb = os.path.getsize(outfile) / 1024
                print(f"  Done ({size_kb:.0f}KB)")

    print("\nAll audio generated!")

if __name__ == "__main__":
    main()
