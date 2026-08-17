# C:\Zgemini Project Overview

This directory serves as a personal automation and content generation hub, integrating various social media platforms, AI tools, and interactive web components.

## Core Components

### 1. Social Media Automation
- **Threads Automation (`threads_poster.py`, `post_happy.py`)**: Uses **Playwright** to automate posting on Threads.net. It utilizes a persistent browser profile stored in `./threads_profile` to maintain login sessions.
- **YouTube Integration (`youtube_uploader.py`, `video_generator.py`)**: A workflow to generate financial news videos (using `gTTS` for speech and `MoviePy` for video synthesis) and upload them to YouTube via the Data API.

### 2. Google Calendar Integration
- **Calendar Management (`verify_all.py`, `check_calendar.py`, etc.)**: Tools for retrieving and verifying Google Calendar events.
- **Authentication**: Uses Google Application Default Credentials (ADC) and OAuth 2.0. Configuration is typically managed through `gcloud` and stored in `~/.config/gws/`.

### 3. Data Processing
- **Excel/CSV Handling (`create_excel.py`, `update_excel.py`, `data.xlsx`)**: Scripts for managing structured data using `openpyxl`.

### 4. Interactive Web Projects
- **Wang Yangming Chat (`wang-yangming-chat/`)**: A web-based "chat with a philosopher" application using Vanilla JS, CSS, and HTML. It features a keyword-based response system mimicking the teachings of Wang Yangming.

## Tech Stack
- **Languages**: Python, JavaScript (HTML/CSS)
- **Libraries**:
  - `playwright`: Web automation
  - `google-api-python-client`: YouTube & Calendar APIs
  - `moviepy`, `gTTS`: Video and Audio generation
  - `openpyxl`: Excel manipulation
- **Tools**: `gws` (Google Workspace CLI), `gcloud` (Google Cloud CLI)

## Directory Structure
- `threads_profile/`: Persistent Chrome user data for automated social media sessions.
- `wang-yangming-chat/`: Source code for the interactive chat application.
- `sap_news.html`/`.pdf`: Sample data or reports used in automation workflows.

## Development Conventions
- **Automation**: Most Python scripts are designed for CLI execution.
- **Authentication**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` is correctly set for API-related tasks.
- **Encoding**: Pay attention to UTF-8 vs. Big5 encoding issues when handling traditional Chinese text from legacy sources.

## TODO / Placeholders
- [ ] Centralize requirements into a `requirements.txt`.
- [ ] Add a master shell script to orchestrate the daily news-to-video-to-post workflow.
