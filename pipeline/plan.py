from pathlib import Path
import json
from pipeline.logger import log_event

ROOT = Path(__file__).resolve().parents[1]


def create_plan(storyboard, output_path=None):
    ROOT.joinpath('outputs').mkdir(exist_ok=True)
    plan = {
        "project": storyboard['project'],
        "stages": ["storyboard_validation", "keyframes", "moving_shots", "music", "narration", "assembly"],
        "shots": []
    }
    for shot in storyboard['shots']:
        plan['shots'].append({
            "id": shot['id'],
            "duration_seconds": shot['duration_seconds'],
            "keyframe_path": f"outputs/keyframes/{shot['id']}.png",
            "video_path": f"outputs/shots/{shot['id']}.mp4",
            "visual_prompt": shot['visual_prompt'],
            "motion_prompt": shot['motion_prompt'],
            "seed": shot.get('seed'),
            "status": shot.get('status', 'draft')
        })
    out = Path(output_path) if output_path else ROOT / 'outputs' / 'pipeline_plan.json'
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    try:
        logged_path = out.relative_to(ROOT)
    except ValueError:
        logged_path = out
    log_event('planning', 'local-pipeline', parameters={"shot_count":len(plan['shots'])}, output_path=logged_path)
    print(f'Plan written: {logged_path}')
    return out
