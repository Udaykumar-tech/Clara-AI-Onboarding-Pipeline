import json
import os


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


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


def generate_agent_spec(memo):

    company = memo["company_name"]

    hours = memo["business_hours"]
    days = ", ".join(hours["days"])
    start = hours["start"]
    end = hours["end"]

    version = memo.get("version", "v1")

    system_prompt = f"""
You are Clara, an AI voice assistant answering calls for {company}.

Business hours:
{days} from {start} to {end}.

During business hours:
- Greet the caller
- Ask their name and phone number
- Ask the purpose of the call
- If needed transfer to Ben
- If transfer fails inform caller Ben will return the call
- Ask if they need anything else before ending call

After hours:
- Ask if the issue is an emergency
- If emergency and related to GNM Pressure Washing gas stations transfer immediately
- Otherwise collect details and inform caller they will be contacted next business day
"""

    agent_spec = {
        "agent_name": f"{company} AI Assistant",
        "voice_style": "professional and friendly",
        "version": version,
        "system_prompt": system_prompt.strip(),
        "key_variables": {
            "business_hours": memo["business_hours"],
            "services_supported": memo["services_supported"],
            "emergency_definition": memo["emergency_definition"]
        },
        "call_transfer_protocol": {
            "transfer_target": "Ben",
            "fallback": "Inform caller Ben will call back shortly"
        },
        "fallback_protocol": {
            "if_unknown": "Politely inform caller someone will follow up shortly"
        }
    }

    return agent_spec


if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    accounts_dir = os.path.join(base_dir, "outputs", "accounts")

    for account in os.listdir(accounts_dir):

        account_root = os.path.join(accounts_dir, account)

        latest_version = get_latest_version(account_root)

        if not latest_version:
            continue

        account_path = os.path.join(account_root, latest_version)

        memo_path = os.path.join(account_path, "account_memo.json")

        if not os.path.exists(memo_path):
            continue

        memo = load_json(memo_path)

        agent_spec = generate_agent_spec(memo)

        output_path = os.path.join(account_path, "agent_spec.json")

        save_json(agent_spec, output_path)

        print(f"Agent spec generated for {account} → {latest_version}")