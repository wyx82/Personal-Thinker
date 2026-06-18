# Personal Thinker

> Your AI thinking partner that helps you identify patterns in your personal problems.

Mihai observes patterns across your life — investments, relationships, decisions — and tells you the truth when he sees contradictions.

**Bilingual:** Mihai responds in whatever language you use. Romanian → Romanian. English → English.

---

## What Mihai Does

- **Identifies patterns** — recurring mistakes, typical reactions, repeating situations
- **Logs decisions** — so you can see why you chose what you chose
- **Makes connections** — "You said this 3 months ago about X"
- **Observes contradictions** — between what you say and what you do
- **Tells you the truth** — even when it's uncomfortable

---

## How It Works

1. Open this project in Claude Code
2. Mihai reads your profile and memory files
3. You talk naturally — Mihai observes and logs
4. When he sees a pattern, he tells you

---

## Folder System

Your data is organized by life domain:

```
memory/user_data/
├── _global/              # your profile (always read)
├── Work/
├── Family/
├── Relationships/
└── [any folder you create]
```

Mihai reads from all folders when making observations.

---

## Privacy

- **100% local** — your data stays on your device
- **Zero cloud** — nothing leaves your machine
- `memory/user_data/` is gitignored — your data never goes public

---

## For Developers

See `docs/MEMORY_RULES.md` for full documentation.
