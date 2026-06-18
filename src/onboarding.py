"""
Onboarding — first run.
Reads options from config/user_config.yaml.
"""
import json
import shutil
from pathlib import Path
from src.config import USER_DATA_DIR, GLOBAL_DATA_DIR, TEMPLATES_DIR, FIRE_OPTIONS, MAX_FOLLOW_UP, DEFAULT_FOLDERS


def check_first_run() -> bool:
    """Return True if first run (no profile.json in _global/)."""
    profile_path = GLOBAL_DATA_DIR / "profile.json"
    return not profile_path.exists()


def ask(question: str) -> str:
    """Helper for input with question displayed."""
    return input(f"\n{question}\n> ").strip()


def ask_multiple(question: str) -> list[str]:
    """Helper for multi-answer questions."""
    print(f"\n{question}")
    response = ask("(comma-separated)")
    return [x.strip() for x in response.split(",") if x.strip()]


def run_onboarding() -> dict:
    """
    Run essential questions from Rule 2.
    Fire options and max follow-up come from config/user_config.yaml.
    """
    print("\n" + "=" * 60)
    print("FIRST RUN — let me get to know you")
    print("=" * 60)

    profile = {}

    # Essential questions (Rule 2)
    profile["name"] = ask("What's your name? (you can use a pseudonym)")
    profile["age"] = ask("How old are you?")

    # Fire - with options from config
    print(f"\n📌 Choose 3-5 traits that describe you:")
    print(f"Options: {', '.join(FIRE_OPTIONS)}")
    fire_input = ask(f"Your choices (e.g.: calm, direct, analytical)")
    profile["traits"] = [x.strip() for x in fire_input.split(",") if x.strip()]

    # Follow-up (max from config)
    follow_up_count = 0
    profile["additional_context"] = ""

    while follow_up_count < MAX_FOLLOW_UP:
        context_hint = ask(f"Follow-up question {follow_up_count + 1}/{MAX_FOLLOW_UP} (or 'done' to finish):")
        if context_hint.lower() in ("done", "deajuns", "destul"):
            break
        if context_hint.lower() != "later":
            if profile["additional_context"]:
                profile["additional_context"] += f" | {context_hint}"
            else:
                profile["additional_context"] = context_hint
        follow_up_count += 1

    return profile


def save_onboarding_profile(profile: dict) -> None:
    """Create folder structure and save global profile."""
    GLOBAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    profile_path = GLOBAL_DATA_DIR / "profile.json"
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    for template_file in TEMPLATES_DIR.iterdir():
        dest = GLOBAL_DATA_DIR / template_file.name
        if not dest.exists():
            shutil.copy2(template_file, dest)

    print(f"\n✅ Profile saved to {profile_path}")


def create_default_folders() -> None:
    """Create default folders from config/user_config.yaml."""
    for folder_name in DEFAULT_FOLDERS:
        folder_path = USER_DATA_DIR / folder_name
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            for template_file in TEMPLATES_DIR.iterdir():
                if template_file.name.endswith(".json"):
                    dest = folder_path / template_file.name
                    if not dest.exists():
                        shutil.copy2(template_file, dest)


def setup_initial_structure() -> None:
    """Set up entire initial structure."""
    GLOBAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    create_default_folders()
