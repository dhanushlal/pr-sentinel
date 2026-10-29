# PR-Sentinel: Automated AI Pull Request Code Review Bot

PR-Sentinel is an automated, event-driven code review bot built with FastAPI, Groq LLM inference, and the GitHub REST API. It listens for repository pull request activities via webhooks, retrieves the raw code diffs, evaluates the changes for bugs and code quality, and automatically posts detailed feedback back to the PR.

---

## Architecture Flow

1. **Pull Request Event**: A developer opens or pushes code to a pull request on GitHub.
2. **Webhook Ingestion**: GitHub sends an asynchronous webhook event payload to the `/webhook` endpoint.
3. **Diff Retrieval**: The backend fetches the raw Git diff of the PR via the GitHub API.
4. **AI Code Analysis**: The diff is submitted to Groq utilizing high-speed inference on `qwen/qwen3.8-27b`.
5. **Automated Feedback**: The structured AI review is automatically published as a comment directly on the pull request.

---

## Tech Stack

* **Language**: Python 3.10+
* **Framework**: FastAPI, Uvicorn
* **AI Inference**: Groq API (`qwen/qwen3.8-27b`)
* **Developer APIs**: GitHub REST API (Webhooks, Pull Requests, Issues)
* **Configuration**: python-dotenv, Requests

---

## Setup & Local Deployment

### 1. Clone & Set Up Virtual Environment
```bash
git clone [https://github.com/dhanushlal/pr-sentinel.git](https://github.com/dhanushlal/pr-sentinel.git)
cd pr-sentinel
python -m venv venv
venv\Scripts\activate  # Windows