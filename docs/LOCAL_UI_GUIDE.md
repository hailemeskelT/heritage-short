# Local Story Studio

The local browser UI collects a source story, a reviewed 10-line Amharic narration, and 10 English subtitle lines. It validates the storyboard, generates illustrated keyframes, narration, score, and subtitles, then uses the existing FFmpeg pipeline to export vertical and horizontal videos.

## Run it

From the project directory, install the project dependencies and start the UI:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

The app opens `http://127.0.0.1:8000`. Keep the terminal open while generating. Stop the local server with `Ctrl+C`.

If generation reports that FFmpeg cannot be found, restart the app so it loads the latest resolver. If needed, reinstall the bundled FFmpeg package using the same interpreter that starts the UI:

```powershell
.\.venv\Scripts\python.exe -m pip install --force-reinstall imageio-ffmpeg
```

## Prepare the story

- Enter the verified source story and intended audience.
- Enter exactly 10 Amharic narration lines, one for each shot.
- Enter exactly 10 concise English subtitle lines, one for each shot. Each line is limited to 100 characters.
- Review names and sensitive details. The UI requires confirmation that you have permission to use the story and understand the TTS data flow.

The UI does not write or translate the script for you. This keeps it from inventing family-story details or claiming a translation was verified.

## Current generation mode and privacy

- Keyframes are abstract illustrated cards, not photorealistic scenes or generated video-model footage.
- The source story and storyboard are stored under `outputs/user_runs/`, which is ignored by Git.
- The Amharic narration text is sent to Edge TTS to synthesize speech. Do not submit private details unless you have permission and have reviewed the provider's data-use terms.
- Subtitle timing follows the fixed shot durations; listen to the narration and verify subtitle timing before sharing the film.
- Video exports are written to `outputs/final/` and overwrite the prior exports. The generated keyframes, narration, score, and subtitles also replace the current pipeline assets.
- Provider-based image and moving-video generation is not connected by this UI. Use the documented Colab workflows separately if you configure and approve those providers.
