import os
import json
import subprocess


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def compute_changes(old, new):

    changes = {}

    for key in new:
        if key not in old:
            changes[key] = {"old": None, "new": new[key]}
        elif old[key] != new[key]:
            changes[key] = {"old": old[key], "new": new[key]}

    return changes


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
        return None

    return f"v{max(versions)}"


if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    accounts_dir = os.path.join(base_dir, "outputs", "accounts")

    for account in os.listdir(accounts_dir):

        account_path = os.path.join(accounts_dir, account)

        latest_version = get_latest_version(account_path)

        if not latest_version:
            continue

        latest_path = os.path.join(account_path, latest_version, "account_memo.json")

        memo_old = load_json(latest_path)

        memo_new = memo_old.copy()
        memo_new["notes"] = "Updated after onboarding call"

        next_version = get_next_version(account_path)

        memo_new["version"] = next_version

        new_path = os.path.join(account_path, next_version, "account_memo.json")

        save_json(memo_new, new_path)

        changes = compute_changes(memo_old, memo_new)

        changes_path = os.path.join(account_path, "changes.json")

        save_json(changes, changes_path)

        print(f"Updated {account} → {next_version}")

    generate_script = os.path.join(base_dir, "scripts", "generate_prompt.py")

    subprocess.run(["python", generate_script])