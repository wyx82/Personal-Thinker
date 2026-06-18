"""
Personal Thinker — Entry Point.
CLI loop with explicit commands and free chat.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import Agent
from src.onboarding import check_first_run, run_onboarding, save_onboarding_profile, setup_initial_structure


def print_banner():
    print(r"""
╔══════════════════════════════════════════════════════╗
║  Personal Thinker — AI Thinking Partner             ║
║  Your partner who tells you the truth to your face  ║
╚══════════════════════════════════════════════════════╝
""")


def print_help():
    print("""
📌 COMMANDS:

  📂 FOLDERS:
    mihai folder              — List all folders
    mihai folder new [name]   — Create new folder
    mihai folder [name]       — Switch active folder
    mihai muta [id] in [folder] — Move item to another folder
    mihai conexiuni           — Links between folders
    mihai cine sunt           — Identities per context

  📊 ANALYSIS:
    mihai audit          — Complete strategic audit
    mihai pattern        — Display your patterns
    mihai descoperiri    — Discoveries to report
    mihai stats          — Memory statistics
    mihai context        — Your complete profile

  🗂️ LOGGING:
    mihai conversatie    — Log a conversation
    mihai decizie        — Log a decision
    mihai problema       — Log a problem

  🔥 OTHER:
    mihai provoaca-ma    — A difficult question
    mihai ajutor         — Full command list

  exit / quit          — Exit

💬 Or just type — normal conversation.
""")


def handle_command(agent: Agent, cmd: str) -> bool:
    """
    Parse and execute a command.
    Returns True if exit command, False otherwise.
    """
    cmd = cmd.strip()
    lower = cmd.lower()

    if lower in ("exit", "quit", "q"):
        print("See you! 👋")
        return True

    if lower == "mihai ajutor":
        print_help()
        return False

    # ─── Folder: list ───────────────────────────────────────────────────────
    if lower == "mihai folder":
        folders = agent.get_all_folders()
        active = agent.get_active_folder()
        print("\n📂 FOLDERS:")
        print("=" * 40)
        print(f"  _global (always present)")
        for folder in folders:
            marker = " ◄─ active" if folder == active else ""
            print(f"  {folder}{marker}")
        print(f"\n  Total: {len(folders)} folders")
        return False

    # ─── Folder: create ──────────────────────────────────────────────────────
    if lower.startswith("mihai folder nou "):
        folder_name = cmd[len("mihai folder nou "):].strip()
        if not folder_name:
            print("⚠️  Tell me a name: mihai folder new [name]")
            return False
        success = agent.create_folder(folder_name)
        if success:
            print(f"\n✅ Folder '{folder_name}' created.")
        else:
            print(f"\n⚠️  Folder '{folder_name}' already exists.")
        return False

    # ─── Folder: switch ──────────────────────────────────────────────────────
    if lower.startswith("mihai folder "):
        folder_name = cmd[len("mihai folder "):].strip()
        if not folder_name:
            print("⚠️  Tell me a name: mihai folder [name]")
            return False
        success = agent.set_active_folder(folder_name)
        if success:
            print(f"\n📂 Active folder: {folder_name}")
        else:
            print(f"\n⚠️  Folder '{folder_name}' doesn't exist. Create it with 'mihai folder new {folder_name}'")
        return False

    # ─── Folder: move item ───────────────────────────────────────────────────
    if lower.startswith("mihai muta "):
        parts = cmd[len("mihai muta "):].split(" in ")
        if len(parts) != 2:
            print("⚠️  Format: mihai muta [id] in [folder]")
            return False
        item_id = parts[0].strip()
        target_folder = parts[1].strip()
        if not item_id or not target_folder:
            print("⚠️  Format: mihai muta [id] in [folder]")
            return False
        print(f"\nMoving item {item_id} to folder {target_folder}...")
        print("⚠️  Not yet implemented.")
        return False

    # ─── Folder: connections ─────────────────────────────────────────────────
    if lower == "mihai conexiuni":
        patterns = agent.get_all_patterns()
        discoveries = agent.get_all_discoveries()
        print("\n🔗 CONNECTIONS BETWEEN FOLDERS:")
        print("=" * 40)
        if not patterns:
            print("  No discoveries yet.")
        for folder, data in patterns.items():
            if data:
                print(f"\n  📁 {folder}:")
                for key, items in data.items():
                    if items:
                        print(f"    {key}: {len(items)} records")
        return False

    # ─── Folder: who am I ───────────────────────────────────────────────────
    if lower == "mihai cine sunt":
        profile = agent.get_profile()
        identities = agent.get_identities()
        print("\n👤 IDENTITIES:")
        print("=" * 40)
        print(f"\n  Global: {profile.get('nume', 'unknown')}")
        print(f"  Age: {profile.get('varsta', '?')}")
        print(f"  Traits: {', '.join(profile.get('fire', [])) or 'not specified'}")
        if identities:
            print(f"\n  Per folder:")
            for ident in identities:
                print(f"    {ident.get('folder')}: {ident.get('nume', '?')}")
        return False

    # ─── Profile ────────────────────────────────────────────────────────────
    if lower == "mihai context":
        profile = agent.get_profile()
        print("\n📋 YOUR PROFILE (GLOBAL)")
        print("=" * 40)
        for key, val in profile.items():
            if val:
                print(f"  {key}: {val}")
        return False

    # ─── Stats ──────────────────────────────────────────────────────────────
    if lower == "mihai stats":
        stats = agent.get_stats()
        print("\n📊 STATISTICS PER FOLDER")
        print("=" * 40)
        for folder, folder_stats in stats.items():
            print(f"\n  📁 {folder}:")
            for key, val in folder_stats.items():
                print(f"    {key}: {val}")
        return False

    # ─── Patterns ───────────────────────────────────────────────────────────
    if lower == "mihai pattern":
        all_patterns = agent.get_all_patterns()
        print("\n🔄 PATTERNS PER FOLDER")
        print("=" * 40)
        if not all_patterns:
            print("  No patterns detected yet.")
        for folder, patterns in all_patterns.items():
            print(f"\n  📁 {folder}:")
            for cat, items in patterns.items():
                if items:
                    print(f"    {cat}: {items}")
        return False

    # ─── Discoveries ────────────────────────────────────────────────────────
    if lower == "mihai descoperiri":
        all_discoveries = agent.get_all_discoveries()
        print("\n💡 DISCOVERIES PER FOLDER")
        print("=" * 40)
        if not all_discoveries:
            print("  No discoveries yet.")
        for folder, discoveries in all_discoveries.items():
            if discoveries:
                print(f"\n  📁 {folder}:")
                for d in discoveries:
                    print(f"    - {d.get('description', '')[:80]}")
        return False

    # ─── Log: Conversation ─────────────────────────────────────────────────
    if lower == "mihai conversatie":
        print("\n🗣️  LOG CONVERSATION")
        print("=" * 40)

        folder = _ask_folder(agent)

        cu_cine = input("Who did you talk to?\n> ").strip()
        despre = input("About what?\n> ").strip()
        emotii = input("How did you feel?\n> ").strip()
        decizii = input("Any decisions made?\n> ").strip()
        actiuni = input("What actions result?\n> ").strip()

        conv_id = agent.log_conversation(cu_cine, despre, emotii, decizii, actiuni, folder)
        print(f"\n✅ Conversation logged: {conv_id} in {folder}")
        return False

    # ─── Log: Decision ──────────────────────────────────────────────────────
    if lower == "mihai decizie":
        print("\n⚖️  LOG DECISION")
        print("=" * 40)

        folder = _ask_folder(agent)

        context = input("Decision context:\n> ").strip()
        decizia = input("What did you decide?\n> ").strip()
        rational = input("Rationale (why did you choose this):\n> ").strip()
        emotional = input("Emotional component:\n> ").strip()
        asteptare = input("Expected result:\n> ").strip()

        dec_id = agent.log_decision(context, decizia, rational, emotional, asteptare, folder)
        print(f"\n✅ Decision logged: {dec_id} in {folder}")
        return False

    # ─── Log: Problem ───────────────────────────────────────────────────────
    if lower == "mihai problema":
        print("\n🚧 LOG PROBLEM")
        print("=" * 40)

        folder = _ask_folder(agent)

        tip = input("Problem type (professional / personal / relationship):\n> ").strip()
        descriere = input("Description:\n> ").strip()
        cauza = input("Root cause (if you know it):\n> ").strip()
        actiuni = input("Actions taken / planned?\n> ").strip()

        prob_id = agent.log_problem(tip, descriere, cauza, actiuni, folder)
        print(f"\n✅ Problem logged: {prob_id} in {folder}")
        return False

    # ─── Audit ──────────────────────────────────────────────────────────────
    if lower == "mihai audit":
        print("\n🔍 STRATEGIC AUDIT")
        print("=" * 40)
        print("Let's explore. Answer briefly and honestly.\n")

        raspunsuri = {}
        intrebari = [
            ("realitate", "How does your life look now, strictly? (not how you want it to look)"),
            ("skilluri", "What skills do you have that actually work for you?"),
            ("energie", "What gives you energy? What kills it?"),
            ("valori", "What values really matter to you — and where do you compromise them?"),
            ("frici", "What are you most afraid of right now?"),
            ("relatii", "How are your main relationships right now?"),
        ]

        for key, intrebare in intrebari:
            raspunsuri[key] = input(f"{intrebare}\n> ").strip()

        folder = _ask_folder(agent)
        problem_desc = raspunsuri.get("realitate", "") + " | " + raspunsuri.get("frici", "")
        if problem_desc.strip() != "|":
            agent.log_problem_from_chat(problem_desc, folder)

        print("\n🤖 AUDIT:")
        audit_text = "\n".join([f"{k}: {v}" for k, v in raspunsuri.items() if v])
        analysis = agent.chat(
            f"Here are the audit answers: {audit_text}. What do you observe? What contradictions? What's clear?",
            mode="audit",
        )
        print(analysis)
        return False

    # ─── Provocare ──────────────────────────────────────────────────────────
    if lower == "mihai provoaca-ma":
        profile = agent.get_profile()
        nume = profile.get("nume", "friend")
        provocare = agent.chat(
            f"Generate a difficult question for {nume}, based on their data: {profile}. One question, direct, that provokes.",
            mode="provocare",
        )
        print(f"\n🔥 {provocare}")
        return False

    # ─── Unknown command ───────────────────────────────────────────────────
    print(f"⚠️  Unknown command: {cmd}")
    print("   Type 'mihai ajutor' for the full list.")
    return False


def _ask_folder(agent: Agent) -> str:
    """Ask user which folder to save to. Deduce from context if possible."""
    folders = agent.get_all_folders()
    active = agent.get_active_folder()

    if active:
        response = input(f"Folder [{active}]: ").strip()
        if response:
            return response
        return active

    if not folders:
        return "general"

    print(f"\n📂 Available folders: {', '.join(folders)}")
    response = input("Where should I save it? (folder name or 'new [name]' for a new folder)\n> ").strip()

    if response.startswith("new "):
        new_folder = response[4:].strip()
        agent.create_folder(new_folder)
        print(f"✅ Folder '{new_folder}' created.")
        return new_folder

    if response in folders:
        return response

    return response if response else folders[0]


def main():
    """Main loop: check first run → onboarding → chat loop."""
    print_banner()

    if check_first_run():
        print("\n👋 Welcome! Let me get to know you.")
        profile = run_onboarding()
        save_onboarding_profile(profile)
        setup_initial_structure()
        print("\n✅ Done! Let's talk.\n")

    try:
        agent = Agent()
    except Exception as e:
        print(f"\n❌ Initialization error: {e}")
        print("Check .env and your API key.")
        sys.exit(1)

    profile = agent.get_profile()
    nume = profile.get("nume", "friend")
    print(f"Hi, {nume}! Type something or a command.\n")

    while True:
        try:
            user_input = input(f"{nume}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSee you! 👋")
            break

        if not user_input:
            continue

        if user_input.lower().startswith("mihai ") or user_input.lower() in ("exit", "quit", "q"):
            should_exit = handle_command(agent, user_input)
            if should_exit:
                break
        else:
            reply = agent.chat(user_input)
            print(f"\n🤖 {reply}\n")


if __name__ == "__main__":
    main()
