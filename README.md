# Mihai — Personal Thinking Partner

> Your thinking partner who tells you the truth to your face.

Mihai is a local-first, terminal-based thinking partner. He observes patterns in your life, logs your decisions and conversations, and speaks to you directly — no fluff, no corporate speak.

**Bilingual:** Mihai responds in whatever language you use. Romanian query → Romanian reply. English query → English reply. No forced translation.

---

## Features

- **Strategic Audit** — analyzes contradictions and patterns in your life
- **Conversation Logging** — email, chat, Slack, face-to-face
- **Pattern Detection** — recurring mistakes, typical reactions, repeating situations
- **Proactive Discoveries** — "I've observed that..." with percentages and reasoning when the data is clear
- **Connections** — links people and events: "You said this 3 months ago about Y"
- **Scenario Simulation** — "70% chance the real problem is X"
- **Learning from Feedback** — when wrong, notes it and doesn't repeat

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MiniMax API key

python main.py
```

On first run, Mihai asks about you (name, traits, values). Data is stored locally in `memory/user_data/`.

---

## Configuration

Edit `config/user_config.yaml` to customize:

```yaml
onboarding:
  fire_options:          # personality traits users can choose from
    - calm
    - impulsiv
    - analitic
    - ...
  max_follow_up: 3       # max follow-up questions during onboarding

folders:
  default:               # default life domains
    - "Muncă"
    - "Familie"
    - "Relații"
```

Edit `.env` for the LLM:

```
MINIMAX_API_KEY=your_key_here
MINIMAX_BASE_URL=https://api.minimax.chat/v1
```

---

## How Mihai Works

Mihai doesn't wait for commands. He **deduces intent** from what you say:

| What you say | What Mihai does |
|--------------|-----------------|
| You tell a story about an interaction | Logs it as a conversation |
| You say "I've decided" or "I've chosen" | Logs it as a decision |
| You say "I'm worried" or "I don't know what to do" | Starts audit/exploration |
| You mention a new topic without a folder | Proposes creating a folder |
| You ask "what do you observe?" | Shows patterns and discoveries |
| You ask "who am I?" or "how do you see me?" | Shows identities per context |

Mihai may ask: *"Do you want to log this or is it just passing thoughts?"*

---

## Folder System

Mihai uses multiple folders — one per life domain:

```
memory/user_data/
├── _global/              # your global profile (always present)
├── Muncă/                # Work
├── Familie/              # Family
├── Relații/              # Relationships
└── [any custom folder]   # create with "create folder for X"
```

When making discoveries, Mihai reads from **all folders** and can say: "At work you're X, at home you're Y."

---

## Project Structure

```
Personal-Thinker/
├── README.md
├── main.py                # entry point
├── requirements.txt
├── .env.example
├── config/
│   └── user_config.yaml   # customizable settings
├── prompts/
│   └── system_prompt.md   # "My name is Mihai" + bilingual
├── docs/
│   └── MEMORY_RULES.md   # full documentation
├── memory/
│   ├── templates/         # empty JSON templates (in repo)
│   └── user_data/         # your data (gitignored)
└── src/
    ├── __init__.py
    ├── config.py
    ├── onboarding.py
    ├── memory_manager.py
    └── agent.py
```

---

## Privacy

- **100% local** — all data stays on your device
- **Zero cloud** — nothing leaves your machine
- `memory/user_data/` is gitignored — only empty templates are in the repo
