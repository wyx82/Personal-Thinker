"""
Agent — LLM calls, context building, discovery detection.
Folder-aware: knows which folder it's in and reads from all.
"""
import re
from typing import Optional

from openai import OpenAI

from src.config import LLM_CONFIG, AGENT_CONFIG, PROMPTS_DIR
from src.memory_manager import MemoryManager


class Agent:
    """Main agent — chat, logging, proactive discoveries, folder-aware."""

    def __init__(self):
        self.memory = MemoryManager()
        self.client = OpenAI(
            base_url=LLM_CONFIG["base_url"],
            api_key=LLM_CONFIG["api_key"],
        )
        self.system_prompt = self._load_system_prompt()
        self.conversation_history = []

    # ─── Init ────────────────────────────────────────────────────────────────

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        path = PROMPTS_DIR / "system_prompt.md"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return "You are Mihai, a direct and honest thinking partner."

    def _build_context(self) -> str:
        """
        Build context string from memory.
        Reads from _global/ and active folder.
        """
        parts = []
        profile = self.memory.get_profile()

        # Global profile
        if profile.get("name"):
            parts.append(f"## Global Profile")
            parts.append(f"Name: {profile.get('name')}")
            if profile.get("age"):
                parts.append(f"Age: {profile.get('age')}")
            if profile.get("traits"):
                parts.append(f"Traits: {', '.join(profile.get('traits', []))}")
            if profile.get("motivates"):
                parts.append(f"Motivates: {', '.join(profile.get('motivates', []))}")
            if profile.get("frustrates"):
                parts.append(f"Frustrates: {', '.join(profile.get('frustrates', []))}")
            if profile.get("current_problem"):
                parts.append(f"Current problem: {profile.get('current_problem')}")
            if profile.get("additional_context"):
                parts.append(f"Context: {profile.get('additional_context')}")

        # Active folder
        active_folder = self.memory.get_active_folder()
        if active_folder:
            parts.append(f"\n## Active Folder: {active_folder}")

            patterns = self.memory.load("patterns.json", active_folder)
            if patterns and any(patterns.values()):
                parts.append(f"\n### Patterns in {active_folder}")
                for cat, items in patterns.items():
                    if items:
                        parts.append(f"{cat}: {', '.join(items) if isinstance(items, list) else items}")

            discoveries = self.memory.load("discoveries.json", active_folder)
            if discoveries:
                unreported = [d for d in discoveries if not d.get("reported_to_mihai", False)]
                if unreported:
                    parts.append(f"\n### Discoveries to report in {active_folder}:")
                    for d in unreported:
                        parts.append(f"- {d.get('descriere', '')[:150]}")

        # Learning from mistakes (cross-folder)
        all_learning = self.memory.get_all_learning()
        if all_learning:
            parts.append(f"\n## Lessons from mistakes")
            for folder, learnings in all_learning.items():
                if learnings:
                    recent = learnings[-2:]
                    for l in recent:
                        parts.append(f"- [{folder}] {l.get('descriere', '')} → {l.get('corectie', '')}")

        # Cross-folder patterns
        all_patterns = self.memory.get_all_patterns()
        if len(all_patterns) > 1:
            parts.append(f"\n## Folder comparison:")
            for folder, patterns in all_patterns.items():
                if patterns and any(patterns.values()):
                    parts.append(f"- {folder}: {patterns}")

        return "\n".join(parts) if parts else ""

    # ─── Chat ─────────────────────────────────────────────────────────────

    def chat(self, user_input: str, mode: str = "normal") -> str:
        """
        Main chat. Build context, call LLM, save history, detect discoveries.
        """
        context = self._build_context()
        extra_system = ""
        if context:
            extra_system = f"\n\n## CONTEXT FROM MEMORY\n{context}"

        messages = [{"role": "system", "content": self.system_prompt + extra_system}]
        messages += self.conversation_history[-AGENT_CONFIG["max_context_messages"]:]
        messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=messages,
            temperature=LLM_CONFIG["temperature"],
            max_tokens=LLM_CONFIG["max_tokens"],
        )

        reply = response.choices[0].message.content

        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": reply})

        self._maybe_log_discovery(user_input, reply)

        return reply

    # ─── Discovery detection ─────────────────────────────────────────────────

    def _maybe_log_discovery(self, user_input: str, reply: str) -> None:
        """
        Heuristic: if reply contains 'am observat' + percentages,
        extract and log to active folder.
        """
        combined = user_input + " " + reply

        has_observation = re.search(r"am observat", combined, re.IGNORECASE)
        has_probability = re.search(r"\d+\s*%", combined)

        if has_observation and has_probability:
            folder = self.memory.get_active_folder() or "general"
            match = re.search(r"(\d+)\s*%\s*șans[ăa]?[^.]*", combined, re.IGNORECASE)
            prob = match.group(1) + "%" if match else "unknown"

            discovery = {
                "type": "percentage",
                "description": reply[:300],
                "based_on": "heuristic: 'am observat' + percentage",
                "probability": prob,
                "prediction": "",
                "impact": "",
                "reported_to_mihai": True,
                "validated": False,
            }
            self.memory.append("discoveries.json", discovery, folder)

    # ─── Folder operations ──────────────────────────────────────────────────

    def get_all_folders(self) -> list[str]:
        """Return all available folders."""
        return self.memory.get_all_folders()

    def set_active_folder(self, folder_name: str) -> bool:
        """Set active folder."""
        return self.memory.set_active_folder(folder_name)

    def get_active_folder(self) -> str | None:
        """Return current active folder."""
        return self.memory.get_active_folder()

    def create_folder(self, folder_name: str) -> bool:
        """Create a new folder."""
        return self.memory.create_folder(folder_name)

    # ─── Log wrappers (folder-aware) ─────────────────────────────────────────

    def log_conversation(
        self,
        cu_cine: str,
        despre: str,
        emotii_mihai: str,
        decizii: str,
        actiuni: str,
        folder: str | None = None,
    ) -> str:
        """Log a conversation to the specified or active folder."""
        target_folder = folder or self.memory.get_active_folder() or "general"
        return self.memory.append("conversations.json", {
            "with_who": cu_cine,
            "about": despre,
            "emotions": emotii_mihai,
            "decisions_made": decizii,
            "actions": actiuni,
        }, target_folder)

    def log_decision(
        self,
        context: str,
        decizia: str,
        rational: str,
        emotional: str,
        rezultat_asteptat: str,
        folder: str | None = None,
    ) -> str:
        """Log a decision to the specified or active folder."""
        target_folder = folder or self.memory.get_active_folder() or "general"
        return self.memory.append("decisions.json", {
            "context": context,
            "decision": decizia,
            "rationale": rational,
            "emotional": emotional,
            "expected_result": rezultat_asteptat,
            "actual_result": "",
            "regret": "",
            "lesson": "",
        }, target_folder)

    def log_problem(
        self,
        tip: str,
        descriere: str,
        cauza_radacina: str,
        actiuni_luate: str = "",
        folder: str | None = None,
    ) -> str:
        """Log a problem to the specified or active folder."""
        target_folder = folder or self.memory.get_active_folder() or "general"
        return self.memory.append("problems.json", {
            "type": tip,
            "description": descriere,
            "root_cause": cauza_radacina,
            "actions_taken": actiuni_luate,
            "result": "",
            "status": "active",
        }, target_folder)

    def log_problem_from_chat(self, descriere: str, folder: str | None = None) -> str:
        """Log a problem detected in conversation."""
        return self.log_problem(
            tip="detected_in_conversation",
            descriere=descriere,
            cauza_radacina="unknown",
            folder=folder,
        )

    # ─── Query wrappers (cross-folder) ───────────────────────────────────────

    def find_person_connections(self, person: str) -> list:
        """Find all connections for a person across all folders."""
        return self.memory.find_connections(person)

    def get_stats(self) -> dict:
        """Return statistics for all folders."""
        return self.memory.get_stats()

    def check_unreported_discoveries(self) -> dict:
        """Return unreported discoveries from all folders."""
        return self.memory.get_all_discoveries()

    def get_all_patterns(self) -> dict:
        """Return patterns from all folders."""
        return self.memory.get_all_patterns()

    def get_all_discoveries(self) -> dict:
        """Return discoveries from all folders."""
        return self.memory.get_all_discoveries()

    def get_profile(self) -> dict:
        """Return global profile."""
        return self.memory.get_profile()

    def get_identities(self) -> list[dict]:
        """Return identities per folder."""
        return self.memory.get_identities()
