
# Reencode Service (Railway)

A tiny FastAPI + FFmpeg service that **sharpens** and **re-encodes** your Kie Veo 3 Fast videos to ~2.6 Mbps, so they look crisper in Telegram.

## What it does
- Input: `video_url` (direct MP4 link from Kie)
- Output: returns an improved MP4 (same resolution/fps, higher bitrate, light sharpening)
- Default bitrate: **2600 kbps**

---

## 1) Deploy on Railway (free)
1. Create an account: https://railway.app
2. In GitHub, create a new empty repo and upload these four files:
   - `main.py`
   - `Dockerfile`
   - `requirements.txt`
   - `README.md`
3. In Railway: **New Project → Deploy from GitHub** → select your repo.
4. Wait for the build to finish.
5. In your service **Settings → Domains**: add a public domain (e.g., `https://your-app.up.railway.app`).
6. Test:
   - `GET https://your-app.up.railway.app/health` → should return `{"ok": true}`

---

## 2) Use it from Make.com

### A) HTTP: Make a request (process the video)
- **Method:** GET
- **URL:** `https://your-app.up.railway.app/reencode?video_url={{<KIE_VIDEO_URL>}}&bitrate_kbps=2600&sharpen=true`
- **Download:** **Yes** (this is important; it tells Make to keep the binary file in `data`)
- **Parse response:** leave default

This module's output will contain a **binary file** in `{{<http_module_number>.data}}`.

### B) Telegram: Send a document (uncompressed)
- **Send by:** `Data`
- **File Name:** `veo3_sharp.mp4`
- **Data:** `{{<http_module_number>.data}}`
- **Caption:** your existing text
- **Chat ID:** map as usual

> Why "Send a document"? Because `sendDocument` does **no recompression**. Your bitrate & quality stay intact.

---

## Optional parameters
- `bitrate_kbps` (default `2600`, range `300–20000`)
- `sharpen` (`true`/`false`)

Example:
```
GET /reencode?video_url=https://example.com/kie.mp4&bitrate_kbps=3000&sharpen=false
```

---

## Notes
- This does **not** upscale resolution. It keeps your original (e.g., 720×1280).
- If you want 1080×1920 output, upscale after this step (a different endpoint can be added).
- Railway free plan is plenty for 1,000+ short clips/month.

