# ProjectAlma — Frontend

Next.js 14 (App Router, TypeScript) — a public lead-intake site plus an
auth-guarded internal dashboard for attorneys.

## Stack

| Concern | Choice |
| --- | --- |
| Framework | Next.js 14 App Router, React Server Components |
| Language | TypeScript (strict) |
| Forms | react-hook-form + zod (shared schemas in `lib/validation.ts`) |
| Styling | CSS Modules + design tokens (`app/globals.css`) — no CSS framework |
| Fonts | `next/font` (self-hosted Lora for display + Inter for body) |
| Auth | JWT in an `httpOnly` cookie, set by a route handler; `middleware.ts` guards `/leads/*` |
| Data | server components call FastAPI via `lib/api.ts` (server-only, `cache()`-deduped) |

## Structure

```
src/
  app/
    page.tsx              public hero + lead form
    login/ signup/        sign-in / role-aware sign-up (applicant | attorney)
    leads/                attorney dashboard (stats + list + [id] detail + activity)
    my/                   applicant portal — read-only view of your own case(s)
      loading.tsx error.tsx   route-level states
    api/                  route handlers that proxy FastAPI (same-origin, token stays server-side)
    error.tsx global-error.tsx not-found.tsx
  components/
    ui/                   design-system primitives (Button, Field, FileDropzone, ConfirmDialog, …)
    auth/                 AuthShell (shared login/signup layout)
    marketing/            PublicHeader, SiteFooter, hero styles
    leads/                LeadForm, LeadsTable, LeadsToolbar, Pagination, ActivityTimeline, ReachOutButton
    dashboard/            DashboardHeader, LogoutButton, StatTiles, RecentActivity
    portal/               PortalHeader, CaseCard (applicant view)
  lib/                    api client, config, session, formatters, validation, param helpers
  middleware.ts
```

## How the pieces talk

- The browser only ever calls **this origin**. `/api/*` route handlers forward to
  FastAPI, attaching the JWT from the cookie server-side.
- The public lead form posts `multipart/form-data` to `/api/leads` → FastAPI.
- The dashboard is server-rendered; filters/search/pagination live in the URL
  (`?state=&search=&page=`) so views are shareable and there's no client/server
  state to sync. Column sort is client-side within the current page.
- "Mark reached out" is a **server action** (`app/leads/actions.ts`) behind a
  confirm dialog, with `revalidatePath` + `router.refresh()`.

## Develop

```bash
npm install
cp .env.example .env.local        # point API_BASE_URL at the running backend
npm run dev                        # http://localhost:3000
```

The backend must be running (see the repo-root `README.md`). Seed the attorney +
demo leads, then sign in at `/login` with `attorney@example.com` / `changeme123`,
or create an account at `/signup` with the invite code `welcome`.

## Checks

```bash
npm run lint        # eslint (next/core-web-vitals)
npm run typecheck   # tsc --noEmit
npm run build       # production build (also runs lint)
npm run format      # prettier
```

## Notes

- `next/font/google` downloads the font files at build time — the build needs
  network access (CI and the Docker build both have it).
- "ProjectAlma" is a generic placeholder name for this exercise.
