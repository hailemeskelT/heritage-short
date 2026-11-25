import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHOT_COUNT = 10
MAX_SUBTITLE_LENGTH = 100


def _read_shot_lines(value, label, max_length):
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if len(lines) != SHOT_COUNT:
        raise ValueError(f"{label} must contain exactly {SHOT_COUNT} non-empty lines, one per shot.")
    if any(len(line) > max_length for line in lines):
        raise ValueError(f"Each {label.lower()} line must be at most {max_length} characters.")
    return lines


def build_storyboard(title, title_am, audience, story, narration, subtitles):
    title = title.strip()
    title_am = title_am.strip()
    audience = audience.strip()
    story = story.strip()
    if not title:
        raise ValueError("Enter a film title.")
    if len(title) > 100:
        raise ValueError("Film title must be at most 100 characters.")
    if not title_am:
        raise ValueError("Enter an Amharic film title.")
    if len(title_am) > 100:
        raise ValueError("Amharic film title must be at most 100 characters.")
    if len(audience) < 5:
        raise ValueError("Enter an intended audience of at least five characters.")
    if len(audience) > 200:
        raise ValueError("Intended audience must be at most 200 characters.")
    if len(story) < 5:
        raise ValueError("Enter the source story (at least five characters).")
    if len(story) > 20000:
        raise ValueError("Source story must be at most 20,000 characters.")

    narration_lines = _read_shot_lines(narration, "Amharic narration", 500)
    subtitle_lines = _read_shot_lines(subtitles, "English subtitles", MAX_SUBTITLE_LENGTH)
    template_path = ROOT / "storyboard.json"
    storyboard = json.loads(template_path.read_text(encoding="utf-8"))
    storyboard["project"].update({
        "title_am": title_am,
        "title_en": title,
        "story_source": story,
        "audience": audience,
        "intent": "Share the user-provided story without adding unverified details.",
    })
    storyboard["style_block"] = (
        "Non-photorealistic abstract illustrated story cards in a warm palette. "
        "Do not depict identifiable people or invent factual scenes."
    )
    storyboard["music"]["mood"] = "Gentle, reflective instrumental."
    storyboard["music"]["instruments"] = "Soft synthetic tones; no culturally specific instruments."

    for shot, narration_line, subtitle_line in zip(
        storyboard["shots"], narration_lines, subtitle_lines
    ):
        shot["narration_am"] = narration_line
        shot["subtitle_en"] = subtitle_line
        shot["visual_prompt"] = (
            "Non-photorealistic abstract story card. Reflect only the supplied caption: "
            + subtitle_line
        )
        shot["motion_prompt"] = "Still illustrated card with a gentle fade between shots."
        shot["shot_reason"] = "Present one segment of the user-reviewed story."
        shot["status"] = "user_story_illustration"

    return storyboard
