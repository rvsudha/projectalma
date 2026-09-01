---
name: git
description: >-
  Git and repository conventions for the ProjectAlma lead app — branch naming, commit
  message format, pre-commit checks, opening a pull request, and keeping
  README.md / docs current with the change. Use when the task is to commit,
  branch, open or update a PR, write a changelog/release note, or generate/refresh
  the project README.
---

# git

## Branching

- Never commit directly to `main`.
- Branch name: `<type>/<short-kebab-summary>` where `<type>` ∈
  `feat | fix | chore | docs | refactor | test`.
  e.g. `feat/lead-notes-field`, `fix/resume-content-type-check`.

## Before you commit

Run and pass:

```bash
make backend-test backend-lint
cd frontend && npm run lint && npm run typecheck   # if frontend changed
```

Never commit: `.env`, anything under `var/`, `node_modules/`, `.next/`, `.idea/`
(all git-ignored — keep it that way).

## Commit messages

Conventional Commits, imperative mood:

```
<type>(<scope>): <summary in ≤72 chars>

<why the change is needed; what changed at a high level>

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
```

`<scope>` is usually `backend`, `frontend`, `infra`, `skills`, or `docs`.
Keep each commit coherent (one logical change); don't mix a refactor with a
feature.

## Pull requests

Use `gh pr create`. The body must have:

- **What & why** — the user-facing change and the motivation.
- **How it works** — key implementation notes / new files.
- **Testing** — commands run and their result; new test coverage.
- **Docs** — which of `README.md`, the `docs/` design docs, `.env.example`, skill
  files were updated (or why none needed it). A structural or reversed decision
  needs the design-decisions doc updated too.

End the body with:

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## README upkeep (this skill also owns the README)

Regenerate or update `README.md` from [`README-template.md`](README-template.md)
when the project's surface changes. `README.md` must always let a new engineer:

1. Run the whole stack in one command (`docker compose up --build`).
2. Know the seeded attorney credentials and how to change them.
3. Run backend tests and the frontend dev server without Docker.
4. Find the config contract (`.env.example` per service) and the design docs
   (`docs/`).

Keep the feature table and the skills table in sync with reality.

## Definition of done for a change

- [ ] Branch off `main`, conventional commits.
- [ ] Tests + lint green (backend always; frontend if touched).
- [ ] `README.md` / `docs/` design docs / `.env.example` updated if the surface
      moved.
- [ ] PR opened with the four-section body.
