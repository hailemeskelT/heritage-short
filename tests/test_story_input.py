import json
import tempfile
import unittest
from pathlib import Path

from pipeline.story_input import build_storyboard
from pipeline.validate import validate_storyboard


NARRATION = "\n".join(f"የታሪክ ክፍል {number}" for number in range(1, 11))
SUBTITLES = "\n".join(f"Story moment {number}" for number in range(1, 11))


class StoryInputTests(unittest.TestCase):
    def test_build_storyboard_validates_and_preserves_story(self):
        storyboard = build_storyboard(
            title="A Family Story",
            title_am="የቤተሰብ ታሪክ",
            audience="Family and community viewers",
            story="A verified family story with permission.",
            narration=NARRATION,
            subtitles=SUBTITLES,
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "storyboard.json"
            path.write_text(json.dumps(storyboard, ensure_ascii=False), encoding="utf-8")
            validated = validate_storyboard(path)

        self.assertEqual(validated["project"]["story_source"], "A verified family story with permission.")
        self.assertEqual(len(validated["shots"]), 10)
        self.assertEqual(validated["shots"][0]["narration_am"], "የታሪክ ክፍል 1")
        self.assertEqual(validated["shots"][0]["subtitle_en"], "Story moment 1")

    def test_requires_exactly_ten_narration_lines(self):
        with self.assertRaisesRegex(ValueError, "exactly 10"):
            build_storyboard(
                title="A Family Story",
                title_am="የቤተሰብ ታሪክ",
                audience="Family and community viewers",
                story="A verified family story with permission.",
                narration="\n".join(["one"] * 9),
                subtitles=SUBTITLES,
            )

    def test_rejects_long_subtitles(self):
        long_subtitles = "\n".join(["x" * 101] + ["short"] * 9)
        with self.assertRaisesRegex(ValueError, "at most 100 characters"):
            build_storyboard(
                title="A Family Story",
                title_am="የቤተሰብ ታሪክ",
                audience="Family and community viewers",
                story="A verified family story with permission.",
                narration=NARRATION,
                subtitles=long_subtitles,
            )


if __name__ == "__main__":
    unittest.main()
