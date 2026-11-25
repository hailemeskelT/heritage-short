import json
import os
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
MAX_REQUEST_BYTES = 150000
USER_RUNS = ROOT / "outputs" / "user_runs"

_jobs = {}
_jobs_lock = threading.Lock()
_generation_lock = threading.Lock()


PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Heritage Short | Story Studio</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #20342d;
      --muted: #64746b;
      --paper: #f7f3e9;
      --card: #fffdf8;
      --line: #e4ddce;
      --accent: #9c573a;
      --accent-dark: #77402d;
      --green: #2f5a48;
      --soft-green: #e8efe7;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif;
    }
    header {
      padding: 48px 24px 34px;
      color: #fffaf0;
      background: linear-gradient(115deg, #17392f, #395c48 70%, #876043);
    }
    .wrap { width: min(940px, 100% - 32px); margin: 0 auto; }
    header .wrap { width: min(940px, 100% - 32px); }
    .eyebrow {
      margin: 0 0 8px;
      color: #e3cda9;
      font-size: 12px;
      font-weight: 750;
      letter-spacing: .15em;
      text-transform: uppercase;
    }
    h1 { margin: 0; font-family: Georgia, serif; font-size: clamp(32px, 6vw, 52px); }
    header p { max-width: 700px; margin: 12px 0 0; color: #f1e9d8; }
    main { padding: 28px 0 52px; }
    .notice {
      margin-bottom: 20px;
      padding: 16px 18px;
      border: 1px solid #d5c7a8;
      border-radius: 12px;
      background: #f3ead6;
      color: #4a412f;
    }
    .notice strong { color: #3b3426; }
    form, .status-card {
      padding: clamp(18px, 4vw, 32px);
      border: 1px solid var(--line);
      border-radius: 16px;
      background: var(--card);
      box-shadow: 0 12px 36px #26392b0d;
    }
    .section-title {
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 0 0 18px;
      font: 24px Georgia, serif;
    }
    .step {
      display: inline-grid;
      width: 30px;
      height: 30px;
      place-items: center;
      border-radius: 50%;
      background: var(--soft-green);
      color: var(--green);
      font: 700 14px system-ui, sans-serif;
    }
    .field { margin: 0 0 18px; }
    label { display: block; margin-bottom: 6px; font-weight: 700; }
    .help { margin: 5px 0 0; color: var(--muted); font-size: 13px; }
    input[type="text"], textarea {
      display: block;
      width: 100%;
      padding: 12px 13px;
      border: 1px solid #cfc8ba;
      border-radius: 9px;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }
    input:focus, textarea:focus { outline: 3px solid #9c573a33; border-color: var(--accent); }
    textarea { min-height: 120px; resize: vertical; }
    textarea.tall { min-height: 210px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .check-row { display: flex; align-items: flex-start; gap: 10px; }
    .check-row input { margin-top: 6px; accent-color: var(--green); }
    .check-row label { font-weight: 500; }
    button {
      border: 0;
      border-radius: 9px;
      padding: 13px 20px;
      background: var(--accent);
      color: #fff;
      font: 700 16px system-ui, sans-serif;
      cursor: pointer;
    }
    button:hover { background: var(--accent-dark); }
    button:disabled { opacity: .6; cursor: wait; }
    .status-card { display: none; margin-top: 20px; }
    .status-card.visible { display: block; }
    #statusText { margin: 0; white-space: pre-wrap; }
    .links { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 15px; }
    .links a { color: var(--green); font-weight: 700; }
    footer { padding: 0 0 30px; color: var(--muted); font-size: 13px; }
    @media (max-width: 660px) {
      .two-col { grid-template-columns: 1fr; gap: 0; }
      header { padding-top: 34px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <p class="eyebrow">Local story-to-video pipeline</p>
      <h1>Heritage Short Studio</h1>
      <p>Shape a verified story into a 10-shot illustrated short. You review the narration and subtitles before rendering.</p>
    </div>
  </header>
  <main class="wrap">
    <div class="notice">
      <strong>What this version generates:</strong> abstract illustrated story cards, Amharic narration,
      English subtitles, original synthetic score, and 9:16 / 16:9 video exports. It does not generate
      photorealistic scenes or use an image/video model.
      <br><strong>Privacy:</strong> source story and storyboard are saved locally and excluded from Git.
      Only the Amharic narration text is sent to Edge TTS to create speech. Do not include private details
      unless you have permission to use them. Subtitle timing follows the fixed shot durations, so review
      it against the generated narration before sharing.
    </div>
    <form id="storyForm">
      <h2 class="section-title"><span class="step">1</span> Story details</h2>
      <div class="two-col">
        <div class="field">
          <label for="title">Film title (English)</label>
          <input id="title" name="title" type="text" maxlength="100" required value="The Light We Inherited">
        </div>
        <div class="field">
          <label for="title_am">Film title (Amharic)</label>
          <input id="title_am" name="title_am" type="text" maxlength="100" required value="የወረስነው ብርሃን">
        </div>
      </div>
      <div class="field">
        <label for="audience">Intended audience</label>
        <input id="audience" name="audience" type="text" maxlength="200" required value="Family and community viewers">
      </div>
      <div class="field">
        <label for="story">Source story</label>
        <textarea id="story" name="story" maxlength="20000" required placeholder="Enter the real, verified story. This source text stays on this computer."></textarea>
        <p class="help">Up to 20,000 characters. This is stored only in a local, Git-ignored storyboard.</p>
      </div>

      <h2 class="section-title"><span class="step">2</span> Review the 10-shot script</h2>
      <div class="field">
        <label for="narration">Amharic narration (10 lines)</label>
        <textarea class="tall" id="narration" name="narration" maxlength="6000" required placeholder="Write 10 lines in Amharic, one shot per line."></textarea>
        <p class="help">Exactly 10 non-empty lines, one for each shot. Review names and pronunciation. This text is sent to Edge TTS.</p>
      </div>
      <div class="field">
        <label for="subtitles">English subtitles (10 lines)</label>
        <textarea class="tall" id="subtitles" name="subtitles" maxlength="1400" required placeholder="Write 10 concise English subtitles, one shot per line."></textarea>
        <p class="help">Exactly 10 non-empty lines; keep each subtitle under 100 characters.</p>
      </div>
      <div class="field check-row">
        <input id="consent" name="consent" type="checkbox" required>
        <label for="consent">I have permission to use this story and have reviewed the narration for privacy. I understand the Amharic narration text will be sent to Edge TTS.</label>
      </div>
      <button id="generateButton" type="submit">Generate illustrated short</button>
    </form>

    <section class="status-card" id="statusCard" aria-live="polite">
      <h2 class="section-title"><span class="step">3</span> Generation status</h2>
      <p id="statusText">Waiting to start.</p>
      <div class="links" id="resultLinks"></div>
    </section>
  </main>
  <footer class="wrap">Runs on this computer at 127.0.0.1. The completed video is a still-image sequence with audio and subtitles.</footer>
  <script>
    const form = document.getElementById("storyForm");
    const button = document.getElementById("generateButton");
    const card = document.getElementById("statusCard");
    const statusText = document.getElementById("statusText");
    const resultLinks = document.getElementById("resultLinks");
    let pollTimer = null;

    function showLinks() {
      resultLinks.replaceChildren();
      for (const [href, label] of [
        ["/media/vertical", "Download vertical video"],
        ["/media/horizontal", "Download horizontal video"]
      ]) {
        const link = document.createElement("a");
        link.href = href;
        link.textContent = label;
        link.download = "";
        resultLinks.appendChild(link);
      }
    }

    async function poll(jobId) {
      try {
        const response = await fetch(`/status?id=${encodeURIComponent(jobId)}`);
        const job = await response.json();
        statusText.textContent = job.message;
        if (job.status === "completed") {
          showLinks();
          button.disabled = false;
          return;
        }
        if (job.status === "failed") {
          button.disabled = false;
          return;
        }
        pollTimer = window.setTimeout(() => poll(jobId), 1500);
      } catch (error) {
        statusText.textContent = "Could not read generation status. Check the app terminal.";
        button.disabled = false;
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (pollTimer) window.clearTimeout(pollTimer);
      button.disabled = true;
      card.classList.add("visible");
      resultLinks.replaceChildren();
      statusText.textContent = "Submitting story...";
      try {
        const response = await fetch("/generate", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
          body: new URLSearchParams(new FormData(form))
        });
        const result = await response.json();
        if (!response.ok) {
          statusText.textContent = result.error || "Could not start generation.";
          button.disabled = false;
          return;
        }
        statusText.textContent = "Generation started...";
        poll(result.job_id);
      } catch (error) {
        statusText.textContent = "Could not contact the local app. Check that it is still running.";
        button.disabled = false;
      }
    });
  </script>
</body>
</html>"""


def _update_job(job_id, **values):
    with _jobs_lock:
        _jobs[job_id].update(values)


def _generate_job(job_id, run_dir):
    if not _generation_lock.acquire(blocking=False):
        _update_job(job_id, status="failed", message="Another generation is running. Please try again when it finishes.")
        return

    try:
        from pipeline.assemble import assemble_from_stills
        from pipeline.generate_local_assets import generate_assets
        from pipeline.media import get_ffmpeg_executable
        from pipeline.plan import create_plan
        from pipeline.validate import validate_storyboard

        os.environ["IMAGEIO_FFMPEG_EXE"] = get_ffmpeg_executable()

        storyboard_path = run_dir / "storyboard.json"
        _update_job(job_id, status="running", message="Validating the story and 68-second storyboard...")
        validated = validate_storyboard(storyboard_path)

        _update_job(job_id, status="running", message="Generating illustrated cards, narration, score, and subtitles...")
        generate_assets(validated)

        _update_job(job_id, status="running", message="Creating the plan and assembling both video formats...")
        create_plan(validated, output_path=run_dir / "pipeline_plan.json")
        assemble_from_stills(validated)
        _update_job(job_id, status="completed", message="Done. Both 68-second videos are ready.")
    except Exception as error:
        _update_job(job_id, status="failed", message=f"Generation failed: {error}")
        print(f"Generation job {job_id} failed: {error}")
    finally:
        _generation_lock.release()


class StoryStudioHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        request = urlsplit(self.path)
        if request.path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        if request.path == "/status":
            job_id = parse_qs(request.query).get("id", [""])[0]
            with _jobs_lock:
                job = _jobs.get(job_id)
            if not job:
                self._send_json({"status": "failed", "message": "Job not found."}, status=404)
                return
            self._send_json(job)
            return

        media_files = {
            "/media/vertical": ROOT / "outputs" / "final" / "Heritage_Short_9x16.mp4",
            "/media/horizontal": ROOT / "outputs" / "final" / "Heritage_Short_16x9.mp4",
        }
        if request.path in media_files:
            path = media_files[request.path]
            if not path.is_file():
                self.send_error(404, "Video has not been generated yet.")
                return
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(path.stat().st_size))
            self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
            self.end_headers()
            with path.open("rb") as media:
                while chunk := media.read(1024 * 1024):
                    self.wfile.write(chunk)
            return

        self.send_error(404)

    def do_POST(self):
        if urlsplit(self.path).path != "/generate":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "Invalid request length."}, status=400)
            return
        if length <= 0 or length > MAX_REQUEST_BYTES:
            self._send_json({"error": "Request is empty or too large."}, status=413)
            return
        try:
            form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
            values = {key: items[0] for key, items in form.items()}
            if values.get("consent") != "on":
                raise ValueError("Confirm permission and the Edge TTS privacy notice before generating.")
            from pipeline.story_input import build_storyboard

            storyboard = build_storyboard(
                title=values.get("title", ""),
                title_am=values.get("title_am", ""),
                audience=values.get("audience", ""),
                story=values.get("story", ""),
                narration=values.get("narration", ""),
                subtitles=values.get("subtitles", ""),
            )
        except (UnicodeDecodeError, ValueError) as error:
            self._send_json({"error": str(error)}, status=400)
            return

        job_id = uuid.uuid4().hex
        run_dir = USER_RUNS / job_id
        run_dir.mkdir(parents=True, exist_ok=False)
        storyboard_path = run_dir / "storyboard.json"
        storyboard_path.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8")
        with _jobs_lock:
            _jobs[job_id] = {"status": "queued", "message": "Waiting for generation to start."}
        worker = threading.Thread(
            target=_generate_job,
            args=(job_id, run_dir),
            daemon=True,
        )
        worker.start()
        self._send_json({"job_id": job_id}, status=202)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


def main():
    USER_RUNS.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), StoryStudioHandler)
    url = f"http://{HOST}:{PORT}"
    print(f"Heritage Short Studio is running at {url}")
    print("Press Ctrl+C to stop. The app is only available on this computer.")
    if os.environ.get("HERITAGE_SHORT_NO_BROWSER") != "1":
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Heritage Short Studio.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
