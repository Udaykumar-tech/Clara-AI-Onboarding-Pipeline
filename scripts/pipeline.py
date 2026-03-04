import argparse
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script):

    script_path = os.path.join(BASE_DIR, script)

    if not os.path.exists(script_path):
        print(f"{script} not found")
        return

    subprocess.run(["python", script_path])


def main():

    parser = argparse.ArgumentParser(description="Clara AI Pipeline")

    parser.add_argument(
        "command",
        choices=["extract", "generate", "onboarding", "patch", "full"],
        help="Pipeline step to run"
    )

    args = parser.parse_args()

    if args.command == "extract":
        run_script("extract_demo.py")

    elif args.command == "generate":
        run_script("generate_prompt.py")

    elif args.command == "onboarding":
        run_script("onboarding_demo.py")

    elif args.command == "patch":
        run_script("apply_patch.py")

    elif args.command == "full":
        run_script("extract_demo.py")
        run_script("generate_prompt.py")
        run_script("onboarding_demo.py")
        run_script("apply_patch.py")


if __name__ == "__main__":
    main()