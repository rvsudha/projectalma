# Skills

Task-scoped instruction sets for building and maintaining the ProjectAlma lead app.
Claude Code loads a skill when the task matches its `description`, or when you
invoke it explicitly with `/<name>`.

| Skill | Invoke when you want to… |
| --- | --- |
| [`lead-agent`](lead-agent/SKILL.md) | Build the lead app end-to-end, or add a feature that spans API + UI + email + storage |
| [`system-design`](system-design/SKILL.md) | Keep the design docs in `docs/` current before non-trivial changes |
| [`email-integration`](email-integration/SKILL.md) | Add or change a transactional email (provider, template, trigger) |
| [`git`](git/SKILL.md) | Branch / commit / open a PR to this repo, or refresh the README |

## Conventions shared by all skills

- **Layering:** `routes → services → models`. Business rules live in
  `backend/app/services/*` and never import from `app.api`.
- **Config:** every new knob is a field on `Settings`
  (`backend/app/core/config.py`) with a safe local default and a line in
  `backend/.env.example`.
- **Tests first-class:** backend changes ship with `pytest` coverage; run
  `make backend-test backend-lint` before handing work back.
- **No secrets in the repo.** `.env` files are git-ignored; `.env.example` is the
  documented contract.
