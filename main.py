import os
import requests
from fastapi import FastAPI, Header, Request
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()

def review_code_with_ai(diff_text: str) -> str:
    prompt = (
        "You are PR-Sentinel, an automated senior code review assistant.\n"
        "Analyze the following git diff patch carefully.\n\n"
        "Check for:\n"
        "1. Security vulnerabilities (leaked secrets, injection risks, unsafe practices).\n"
        "2. Bugs or unhandled edge cases (e.g., division by zero, null references).\n"
        "3. Code quality and formatting suggestions.\n\n"
        "Provide your response in clean GitHub Markdown format with clear headings, bullet points, and actionable suggestions.\n\n"
        f"Diff:\n```diff\n{diff_text}\n```"
    )
    response = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer providing precise, helpful, and concise PR reviews."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def post_github_comment(repo_full_name: str, pr_number: int, comment_body: str):
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"body": comment_body}
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 201:
        print(f"[+] Successfully posted AI review to PR #{pr_number}!")
    else:
        print(f"[-] Failed to post comment: {resp.status_code} - {resp.text}")


@app.post("/webhook")
async def github_webhook(request: Request, x_github_event: str = Header(None)):
    if x_github_event == "ping":
        return {"status": "pong"}

    if x_github_event == "pull_request":
        data = await request.json()
        action = data.get("action")

        if action in ["opened", "synchronize", "reopened"]:
            pr_data = data.get("pull_request", {})
            pr_number = pr_data.get("number")
            repo_name = data.get("repository", {}).get("full_name")
            diff_url = pr_data.get("diff_url")

            print(f"[+] Reviewing PR #{pr_number} for repository: {repo_name}")

            diff_res = requests.get(diff_url)
            diff_text = diff_res.text

            print("[+] Sending diff to Groq for analysis...")
            ai_review = review_code_with_ai(diff_text)

            print("[+] Posting AI review back to GitHub...")
            post_github_comment(repo_name, pr_number, ai_review)

            return {"status": "review_posted"}

    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)