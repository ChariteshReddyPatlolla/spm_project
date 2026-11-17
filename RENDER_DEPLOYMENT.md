# 🚀 Deploying to Render with Google Gemini API

This guide walks you through deploying the **Multi-Paper Research Assistant** to [Render](https://render.com/) as a production cloud web service powered by the **Google Gemini API** (`gemini-1.5-flash`).

---

## 📋 Prerequisites

1. **A Render Account**: Sign up for free at [render.com](https://render.com/).
2. **A GitHub / GitLab Account**: With this repository pushed to your remote.
3. **A Google Gemini API Key**: Free at [Google AI Studio](https://aistudio.google.com/).

---

## 🔑 Step 1: Obtain Your Free Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **Get API Key** in the top navigation.
3. Click **Create API Key in new project** (or select an existing project).
4. Copy the generated API key.

---

## 🌐 Deployment Options

### Option A: Render Blueprint (`render.yaml`) — Recommended & Easiest

The repository includes a ready-to-use `render.yaml` blueprint that configures everything automatically.

1. Push this repository to your GitHub account:
   ```bash
   git add .
   git commit -m "Configure for Render deployment with Gemini API"
   git push origin main
   ```
2. Log into [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** in the top right and select **Blueprint**.
4. Connect your GitHub repository.
5. Render will detect `render.yaml`.
6. Under **Environment Variables**, enter your `GEMINI_API_KEY`.
7. Click **Apply**. Render will automatically build the React frontend and Python backend into a unified container and deploy your live URL!

---

### Option B: Manual Web Service (Docker)

If you prefer setting up the web service manually:

1. In Render Dashboard, click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Choose your repository.
4. Fill in the service settings:
   - **Name**: `multi-paper-research-assistant`
   - **Region**: Any (e.g., `Oregon (US West)` or `Frankfurt (EU Central)`)
   - **Branch**: `main`
   - **Runtime**: **Docker**
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: **Free** (or Starter)
5. Expand **Environment Variables** and add:
   | Key | Value | Description |
   |-----|-------|-------------|
   | `GEMINI_API_KEY` | `<your-gemini-api-key>` | Your Google Gemini API Key |
   | `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model to use |
   | `LLM_PROVIDER` | `gemini` | Enables cloud Gemini API engine |
   | `ENABLE_OCR` | `true` | Enables Tesseract OCR |
   | `DEBUG` | `false` | Production mode |
6. Click **Create Web Service**.

---

### Option C: Native Python Web Service (Build Script)

If you choose the native Python environment instead of Docker:

1. In Render Dashboard, select **Runtime: Python 3**.
2. Set:
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`
3. Add the environment variables from the table above.
4. Click **Create Web Service**.

---

## ⚙️ How It Works in Production

- **Unified Single Container**: The multi-stage `Dockerfile` compiles the Vite React frontend (`frontend/dist`) and bundles it directly into FastAPI.
- **Single Port & Zero CORS Issues**: FastAPI serves the React SPA at `/` and handles API requests at `/api/v1`, eliminating cross-origin errors.
- **Online Cloud LLM**: Queries are synthesized using Google Gemini API (`gemini-1.5-flash`), eliminating the need for a local Ollama daemon or expensive cloud GPU.
- **Verified Citations**: All answers retain strict citation attribution in `[Paper Title, Page X]` format, validated by the grounding engine.
- **Local Fallback**: If `GEMINI_API_KEY` is not supplied, the system seamlessly falls back to local neural synthesis or local Ollama.

---

## 🔍 Verification

Once your service status turns **Live** in Render:

1. Open your Render service URL (e.g., `https://multi-paper-research-assistant.onrender.com`).
2. Look at the top navigation bar:
   - The **LLM Engine** badge will display `gemini-1.5-flash` with a bright green indicator (**Gemini API Online**).
3. Upload research papers (or use sample papers) and begin querying!
