import json
import os
import re


def load_transcript(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_template(template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# -------------------------
# Extraction Functions
# -------------------------

def extract_company_name(transcript):

    match = re.search(r"Ben'?s Electric Solutions", transcript, re.IGNORECASE)

    if match:
        return "Ben's Electric Solutions"

    return ""


def extract_business_hours(transcript):

    days = []
    start = ""
    end = ""

    text = transcript.lower()

    # detect weekday schedule
    if re.search(r"monday\s*(to|-)\s*friday", text):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # flexible time extraction
    time_match = re.search(
        r"(\d{1,2}[:\s]?\d{0,2})\s*(?:to|-)\s*(\d{1,2}[:\s]?\d{0,2})",
        text
    )

    if time_match:
        start = time_match.group(1).replace(" ", ":")
        end = time_match.group(2).replace(" ", ":")

    return days, start, end
def extract_timezone(transcript):

    text = transcript.lower()

    # common US timezones
    if "pacific" in text or "pst" in text:
        return "PST"

    if "eastern" in text or "est" in text:
        return "EST"

    if "central" in text or "cst" in text:
        return "CST"

    if "mountain" in text or "mst" in text:
        return "MST"

    # if transcript says "same time zone"
    if "same time zone" in text:
        return ""

    return ""

def extract_services(transcript):

    services = []
    text = transcript.lower()

    if "service call" in text:
        services.append("service calls")

    if "quote" in text:
        services.append("quotes")

    if "small jobs" in text:
        services.append("small electrical jobs")

    return services


def extract_emergency_definition(transcript):

    if "gnm pressure washing" in transcript.lower():
        return ["Gas station electrical issues for GNM Pressure Washing properties"]

    return []


# -------------------------
# Fill JSON
# -------------------------

def fill_account_memo(transcript, memo, account_id):

    memo.setdefault("questions_or_unknowns", [])

    memo["account_id"] = account_id

    company = extract_company_name(transcript)
    memo["company_name"] = company

    days, start, end = extract_business_hours(transcript)

    memo["business_hours"]["days"] = days
    memo["business_hours"]["start"] = start
    memo["business_hours"]["end"] = end

    timezone = extract_timezone(transcript)
    memo["business_hours"]["timezone"] = timezone

    memo["services_supported"] = extract_services(transcript)

    memo["emergency_definition"] = extract_emergency_definition(transcript)

    memo["emergency_routing_rules"] = [
        "Transfer emergency gas station calls from GNM Pressure Washing properties directly to Ben"
    ]

    memo["non_emergency_routing_rules"] = [
        "Collect caller name, phone number and service request then notify Ben"
    ]

    memo["integration_constraints"] = [
        "Send post-call notifications via SMS and email"
    ]

    memo["office_hours_flow_summary"] = (
        "Clara answers incoming customer calls and transfers to Ben when needed"
    )

    memo["after_hours_flow_summary"] = (
        "After hours calls handled next business day except emergency calls from property manager"
    )

    if not company:
        memo["questions_or_unknowns"].append("Company name not mentioned")

    if not start:
        memo["questions_or_unknowns"].append("Business hours not specified")
    if not timezone:
        memo["questions_or_unknowns"].append("Timezone not specified")
    return memo


# -------------------------
# Main Pipeline
# -------------------------

if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    transcript_folder = os.path.join(base_dir, "datasets", "demo")

    template_path = os.path.join(
        base_dir,
        "templates",
        "account_memo_template.json"
    )

    transcripts = [f for f in os.listdir(transcript_folder) if f.endswith(".txt")]

    for transcript_file in transcripts:

        transcript_path = os.path.join(transcript_folder, transcript_file)

        transcript = load_transcript(transcript_path)

        memo = load_template(template_path)

        account_number = transcript_file.replace("transcript_", "").replace(".txt", "")

        account_id = f"account_{account_number}"

        filled = fill_account_memo(transcript, memo, account_id)

        output_path = os.path.join(
            base_dir,
            "outputs",
            "accounts",
            account_id,
            "v1",
            "account_memo.json"
        )

        save_json(filled, output_path)

        print(f"Generated memo for {account_id}")