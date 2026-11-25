# The Stories We Inherit — Heritage Short Starter Project

**Working title:** የወረስነው ብርሃን (The Light We Inherited)  
**Narration:** Amharic  
**Film duration target:** 60–90 seconds (current storyboard target: 68 seconds)  
**Outputs:** vertical 9:16 MP4 and horizontal 16:9 MP4  
**Deadline stated in the challenge brief:** Thursday, 26 November 2026, 23:59 East Africa Time

> IMPORTANT: This is a prepared starter kit, not a completed film or a fully connected production system. The real family story, permissions, audience feedback, generated media, measured costs/latencies, and final submission links must be supplied from actual work. Do not present example text or blank templates as evidence.

## 1. What this repository is for

This project provides a structured starting point for the AI-Content Generation: The Heritage Short challenge. It includes:

- A 10-shot storyboard draft and JSON Schema.
- A Python pipeline scaffold for validation, planning, logging, cache hashing, and FFmpeg assembly from approved still keyframes.
- Templates for design research, experiments, failures, costs, ethics, the final report, public post, and walkthrough.
- A Google Colab setup guide for GPU work.
- A challenge compliance checklist.
- A local browser UI for entering a story and generating an illustrated still-based short.

The required AI-generation adapters (image, video, Amharic TTS, and music) still need to be connected to the accounts/models you actually use. Their current IDs, access limits, licences, and API formats should be checked against the providers' official documentation before implementation.

## 2. First steps

1. Replace all `[PLACEHOLDER]` values in `storyboard.json` and `DESIGN.md` with facts from a real family/community story.
2. Obtain recorded, informed consent before generating or using an identifiable real person's likeness or voice. Record the evidence in `ETHICS.md`.
3. Create a virtual environment and install requirements:

   ```bash
   python -m venv .venv
   # Windows PowerShell: .venv\\Scripts\\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Install FFmpeg and ensure `ffmpeg` is available on PATH.
5. Copy `.env.example` to `.env`; add keys locally only. Never commit `.env`.
6. Validate and create the stage plan:

   ```bash
   python main.py validate
   python main.py plan
   ```

7. Generate the required media using your chosen provider adapters / Colab workflows and save files in the paths in `docs/ASSET_MANIFEST.md`.
8. Run final assembly:

   ```bash
   python main.py assemble
   ```

9. Run `python main.py run` to validate, plan, check assets, and assemble in one command after all assets exist.

### Local Story Studio

Install dependencies and run the local UI:

```powershell
python -m pip install -r requirements.txt
python app.py
```

The browser UI accepts the source story, 10 reviewed Amharic narration lines, and 10 English subtitle lines, then runs the local asset generation and assembly pipeline. See [docs/LOCAL_UI_GUIDE.md](docs/LOCAL_UI_GUIDE.md) for privacy notes and current limitations. This fallback produces abstract illustrated cards; it does not connect an image or video-generation model.

## 3. Required media file locations

- Keyframes: `outputs/keyframes/shot_01.png` through `shot_10.png`.
- Amharic narration mix/stem: `outputs/narration/narration.wav`.
- Original instrumental score: `outputs/music/score.wav`.
- English subtitles: `subtitles/narration.en.srt`.
- Final exports: `outputs/final/Heritage_Short_9x16.mp4` and `outputs/final/Heritage_Short_16x9.mp4`.

The current FFmpeg assembler deliberately supports still-keyframe fallback. For moving shots, create approved clips with your video model and extend `pipeline/assemble.py` to concatenate or time-align clips, or use still animation as allowed by the challenge brief. Keep the final pipeline reproducible.

## 4. Commands

```bash
python main.py validate    # Validate JSON Schema and 60–90 second duration
python main.py plan        # Create outputs/pipeline_plan.json
python main.py assemble    # Assemble from keyframes + narration + score + SRT
python main.py run         # Validate + plan + assemble
```

## 5. Submission rule

The challenge has two separate Tenx assignments. See `docs/REQUIREMENTS_CHECKLIST.md` and `docs/SUBMISSION_CHECKLIST.md`. Make sure every submitted link opens without login or is explicitly shared with the reviewers.

## 6. Repository hygiene

Do not commit API keys, personal family records, consent forms containing unnecessary personal details, private photos, or unlicensed model files. Keep only the minimum consent evidence needed for grading and store sensitive originals securely.
