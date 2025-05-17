import requests, json, config

def load_data():
    response = requests.get(
        f"https://api.github.com/gists/{config.GIST_ID}",
        headers={"Authorization": f"token {config.GITHUB_TOKEN}"}
    )
    return json.loads(response.json()["files"]["bot_memory.json"]["content"])

def save_data(data):
    requests.patch(
        f"https://api.github.com/gists/{config.GIST_ID}",
        headers={"Authorization": f"token {config.GITHUB_TOKEN}"},
        json={"files": {"bot_memory.json": {"content": json.dumps(data, indent=2)}}}
    )