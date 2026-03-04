import os
import json
import subprocess


def get_next_version(account_path):

    versions = []

    for folder in os.listdir(account_path):
        if folder.startswith("v"):
            try:
                versions.append(int(folder[1:]))
            except:
                pass

    if not versions:
        return "v1"

    return f"v{max(versions)+1}"


def get_latest_version(account_path):

    versions = []

    for folder in os.listdir(account_path):
        if folder.startswith("v"):
            try:
                versions.append(int(folder[1:]))
            except:
                pass

    if not versions:
        return "v1"

    return f"v{max(versions)}"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    account_id = "account_001"

    account_path = os.path.join(base_dir, "outputs", "accounts", account_id)

    latest_version = get_latest_version(account_path)

    latest_path = os.path.join(
        account_path,
        latest_version,
        "account_memo.json"
    )

    memo = load_json(latest_path)

    # simulate onboarding update
    memo["notes"] = "Updated after onboarding call"

    next_version = get_next_version(account_path)

    memo["version"] = next_version

    new_path = os.path.join(
        account_path,
        next_version,
        "account_memo.json"
    )

    save_json(memo, new_path)

    print("Onboarding update applied for", account_id, "→", next_version)

    generate_script = os.path.join(base_dir, "scripts", "generate_prompt.py")

    subprocess.run(["python", generate_script])