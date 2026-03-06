#!/usr/bin/env python3
"""Generate narration audio for Legends of Zeno from legends.json"""
import asyncio
import json
import os
import re
import edge_tts

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-5%"
OUTPUT_DIR = "audio"

def strip_html(html):
    return re.sub(r'<[^>]+>', ' ', html).replace('&mdash;', '—').replace('&nbsp;', ' ').strip()

def get_narration(slide):
    t = slide.get("type", "")
    if t == "title":
        return f"{slide['heading']}. {slide['subheading']}"
    elif t == "narrative":
        return strip_html(slide["text"])
    elif t == "agents":
        agents = " ".join(
            f"The {a['name']} covers {a['domain']}. For example: {a['example']}"
            for a in slide["agents"]
        )
        return f"{slide['heading']}. {slide['subheading']}. {agents}"
    elif t == "tips":
        tips = " ".join(f"{t['title']}. {t['text']}" for t in slide["tips"])
        return f"{slide['heading']}. {slide['subheading']}. {tips}"
    elif t == "cta":
        steps = " ".join(f"Step {s['label']}: {s['title']}. {s['text']}." for s in slide["steps"])
        return f"{slide['heading']}. {slide['subheading']}. {steps}"
    return ""

async def generate():
    with open("data/legends.json") as f:
        legends = json.load(f)

    for legend in legends:
        lid = legend["id"]
        for i, slide in enumerate(legend["slides"]):
            text = get_narration(slide)
            if not text:
                continue
            outfile = os.path.join(OUTPUT_DIR, f"{lid}-{i}.mp3")
            print(f"Generating {outfile}...")
            comm = edge_tts.Communicate(text, VOICE, rate=RATE)
            await comm.save(outfile)
            print(f"  Done ({len(text)} chars)")

    print("\nAll audio generated!")

asyncio.run(generate())
