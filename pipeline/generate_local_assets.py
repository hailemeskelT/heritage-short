import asyncio
import math
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1080
HEIGHT = 1080


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\Nirmala.ttf",
    ]
    if bold:
        candidates.insert(0, r"C:\Windows\Fonts\arialbd.ttf")
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_reference_sheets():
    refs = ROOT / "references"
    refs.mkdir(parents=True, exist_ok=True)

    sheet = Image.new("RGB", (WIDTH, HEIGHT), "#18352f")
    draw = ImageDraw.Draw(sheet)
    draw.ellipse((390, 210, 690, 510), fill="#b86b45")
    draw.ellipse((430, 250, 650, 470), fill="#d29a73")
    draw.rectangle((330, 500, 750, 870), fill="#d7b38b")
    draw.ellipse((350, 520, 730, 900), fill="#eee1bd")
    draw.text((60, 60), "ILLUSTRATIVE CHARACTER REFERENCE", fill="#fff8df", font=font(42, True))
    draw.text((60, 930), "No identifiable real person depicted", fill="#fff8df", font=font(30))
    sheet.save(refs / "character_sheet.png")

    style = Image.new("RGB", (WIDTH, HEIGHT), "#d9c7a2")
    draw = ImageDraw.Draw(style)
    for i, color in enumerate(["#18352f", "#8c4a32", "#c69a5d", "#eee1bd"]):
        draw.rectangle((80 + i * 230, 180, 290 + i * 230, 760), fill=color)
    draw.text((60, 60), "STYLE / COLOUR REFERENCE", fill="#18352f", font=font(44, True))
    draw.text((60, 840), "Warm / respectful / documentary-inspired", fill="#18352f", font=font(34))
    style.save(refs / "style_reference.png")


def make_keyframes(storyboard):
    output = ROOT / "outputs" / "keyframes"
    output.mkdir(parents=True, exist_ok=True)
    palette = [
        ("#18352f", "#d9c7a2", "#c69a5d"),
        ("#4e4a3d", "#d8b76a", "#8c4a32"),
        ("#2a3d35", "#b86b45", "#eee1bd"),
        ("#4d3529", "#d29a73", "#18352f"),
        ("#5b513e", "#c69a5d", "#eee1bd"),
        ("#26382f", "#9f7454", "#d8b76a"),
        ("#6c5842", "#d29a73", "#18352f"),
        ("#1e3b38", "#d8b76a", "#eee1bd"),
        ("#7b593f", "#b86b45", "#d9c7a2"),
        ("#18352f", "#eee1bd", "#c69a5d"),
    ]

    for index, shot in enumerate(storyboard["shots"], start=1):
        dark, light, accent = palette[index - 1]
        image = Image.new("RGB", (WIDTH, HEIGHT), dark)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 690, WIDTH, HEIGHT), fill=light)
        draw.ellipse((120, 180, 960, 1020), outline=accent, width=18)
        draw.ellipse((360, 320, 720, 680), fill=accent)
        draw.rectangle((150, 760, 930, 790), fill=dark)
        draw.text((60, 60), f"SHOT {index:02d}", fill="#fff8df", font=font(58, True))
        draw.text((60, 110), "ILLUSTRATIVE / PLACEHOLDER", fill="#fff8df", font=font(28))
        subtitle = shot["subtitle_en"]
        if subtitle.startswith("[") or "PLACEHOLDER" in subtitle.upper():
            subtitle = "Replace with a verified family story"
        lines = [subtitle[i:i + 34] for i in range(0, len(subtitle), 34)]
        y = 820
        for line in lines[:3]:
            draw.text((60, y), line, fill=dark, font=font(34, True))
            y += 48
        draw.text((60, 990), "Illustrative scene - made with AI", fill=dark, font=font(24))
        image.save(output / f"{shot['id']}.png")


async def make_narration(storyboard):
    narration_dir = ROOT / "outputs" / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)
    mp3 = narration_dir / "_narration.mp3"
    text = " ".join(shot["narration_am"] for shot in storyboard["shots"])
    text = text.replace("[የቤተሰብ አባል]", "ቤተሰብ አባል")
    text = text.replace("[የታሪኩን መጀመሪያ እውነታ እዚህ ያስገቡ።]", "የታሪኩ መጀመሪያ እውነታ ነው።")
    text = text.replace("[ዋናውን ክስተት በአጭሩ ያብራሩ።]", "ዋናውን ክስተት እናብራራ።")
    text = text.replace("[እውነተኛ ትምህርት]", "የእውነተኛ ትምህርት")
    communicate = edge_tts.Communicate(text, "am-ET-MekdesNeural")
    await communicate.save(str(mp3))

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    wav = narration_dir / "narration.wav"
    import subprocess
    subprocess.run([
        ffmpeg, "-y", "-i", str(mp3),
        "-af", "apad=whole_dur=68,atrim=0:68,highpass=f=80,lowpass=f=12000",
        "-ar", "48000", "-ac", "1", str(wav)
    ], check=True, capture_output=True)
    mp3.unlink(missing_ok=True)


def make_score():
    music_dir = ROOT / "outputs" / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    path = music_dir / "score.wav"
    rate = 44100
    duration = 68
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(rate)
        frames = bytearray()
        import struct
        chords = [(130.81, 164.81, 196.0), (146.83, 174.61, 220.0),
                  (130.81, 155.56, 196.0), (110.0, 164.81, 220.0)]
        for i in range(rate * duration):
            t = i / rate
            chord = chords[min(3, int(t // 17))]
            envelope = 0.18 * (0.72 + 0.28 * math.sin(math.pi * t / duration))
            left = sum(math.sin(2 * math.pi * f * t) for f in chord) * envelope / len(chord)
            right = sum(math.sin(2 * math.pi * f * t + 0.02) for f in chord) * envelope / len(chord)
            frames += struct.pack("<hh", int(left * 32767), int(right * 32767))
        output.writeframes(frames)


def make_subtitles(storyboard):
    lines = ["1"]
    start = 0
    for index, shot in enumerate(storyboard["shots"], start=1):
        end = start + shot["duration_seconds"]
        text = shot["subtitle_en"]
        if text.startswith("["):
            text = "Replace with the verified family story."
        lines.append(f"{start // 3600:02d}:{(start % 3600) // 60:02d}:{start % 60:02d},000 --> "
                     f"{end // 3600:02d}:{(end % 3600) // 60:02d}:{end % 60:02d},000")
        lines.append(text)
        lines.append("")
        if index < len(storyboard["shots"]):
            lines.append(str(index + 1))
        start = end
    (ROOT / "subtitles" / "narration.en.srt").write_text("\n".join(lines), encoding="utf-8")


def main():
    import json
    storyboard = json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))
    make_reference_sheets()
    make_keyframes(storyboard)
    make_score()
    make_subtitles(storyboard)
    asyncio.run(make_narration(storyboard))
    print("Generated illustrative references, keyframes, narration, score, and subtitles.")


if __name__ == "__main__":
    main()
