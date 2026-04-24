# Prompt: Unified Summit Shifts — Django + React (V1: OS + SupSci + Tailgate)

## Context

I'm replacing a Google Sheet that the Vera Rubin Observatory summit team uses to plan nightly shifts. The sheet has one tab per "role group" (OS, SupSci, Camera, Calibration, Electric, Electronic, Tailgate, Triage, TestSci, Admin) plus a `Summary` tab that aggregates all role assignments into one wide table indexed by date.

For V1, I want to replicate **only** three role groups — OS (Observing Specialist), SupSci (Science Support), and Tailgate (Summit Morning Meeting Coordination) — plus a Summary view that shows the assignments from those groups in the same look-and-feel as the spreadsheet's `Summary` tab. The architecture must let me add the remaining role groups later without rework.

### Important: cross-group overlaps are allowed but discouraged — and OS/SupSci are disjoint

Two different things to keep straight:

1. **Person membership.** OS and SupSci are two distinct populations of staff — a single person is **never** in both. Tailgate draws its people from either OS or SupSci. So the only real memberships a person can have are: `{OS}`, `{SupSci}`, `{OS, Tailgate}`, `{SupSci, Tailgate}`, or `{Tailgate}` (for any Tailgate-only people, which is rare but possible). This is enforced by the `MUTUALLY_EXCLUSIVE_GROUPS` setting in the Person model.

2. **Same-day cross-group assignments.** Because OS and SupSci share no people, same-day OS↔SupSci conflicts are impossible by construction. The cross-group overlap that actually happens in practice is **OS↔Tailgate** or **SupSci↔Tailgate**: a person covering an OS (or SupSci) shift can in principle also run the Tailgate morning meeting. Policy for those:
   - A person should **not** be assigned to cross-group shifts on the same date if anyone else is available.
   - If it must happen (no other options), the system **allows** the assignment but flags it as a warning, and the user must confirm.
   - The system must **never silently accept** a cross-group same-day assignment — always surface it.
   - The only genuine block within a single group is two assignments for the same person on the same date.

Concretely: if OT1 is already assigned to "OS Day shift" on 2026-04-03, then on the Tailgate schedule for that date, OT1's cell should render with an amber warning indicating they're busy with OS; assigning them requires a confirmation dialog. Same in reverse.

## Tech stack

- **Backend:** Django 5.x + Django REST Framework. Use SQLite for local dev, but keep the ORM portable (no SQLite-only features). Provide a `docker-compose.yml` with optional Postgres.
- **Frontend:** React 18 + Vite + TypeScript. Use TanStack Table v8 for the wide spreadsheet-like grids. Use Tailwind for styling. No heavy UI framework (no MUI / Ant).
- **API:** REST under `/api/v1/`. JSON only. CORS open to `localhost:5173` in dev.
- **Auth:** Skip for V1. Add a `# TODO: auth` comment where session/token auth would slot in later.
- **Tests:** pytest-django for the backend (models + a smoke test per endpoint). Vitest + React Testing Library for one render test per main view.

## Data model

```
RoleGroup
  - code              (str, unique)        e.g. "OS", "SupSci", "Tailgate"
  - name              (str)                e.g. "Observing Specialists"
  - sort_order        (int)
  - coverage_policy   (enum: "always" | "weekdays_only")
                                           # "always": missing coverage is a red-highlighted error
                                           # "weekdays_only": coverage only expected Mon–Fri;
                                           #                  weekend empty cells are neutral (not red)
                                           # Future policies may consult a holiday calendar.

Role  (a specific shift slot inside a role group; one row in the per-group sheet's "code legend")
  - group             (FK RoleGroup)
  - code              (str)                e.g. "1", "2", "3", "4", "R", "B", "T", "S", "N"
  - label             (str)                e.g. "Late shift lead"
  - is_lead           (bool)
  - is_remote         (bool)
  - is_backup         (bool)                # enables "promoted from backup" analytics
  - sort_order        (int)
  - effective_from    (date)               # first date this Role definition is valid
  - effective_to      (date, nullable)     # last date + 1 this Role definition is valid; NULL = still current
  - unique_together: (group, code, effective_from)   # same code can exist in different windows

Person
  - full_name     (str)              # "Lastname, Firstname" to match the sheet convention
  - initials      (str, unique)      # 2–3 chars, used as the cell value in the grid
  - groups        (M2M RoleGroup)    # which role groups they can take shifts in
  - active        (bool)
  - validators:
      * groups must not contain any pair listed in MUTUALLY_EXCLUSIVE_GROUPS (see settings)
        → raises ValidationError on model.full_clean() / serializer validation

Settings constant:
  MUTUALLY_EXCLUSIVE_GROUPS = [("OS", "SupSci")]   # tuples of RoleGroup codes that cannot co-exist on one Person
  # OS and SupSci are two disjoint populations of staff. Tailgate draws from both but a single
  # person is never in both OS and SupSci. Kept as a config list so it's trivial to extend
  # or relax as the org evolves.

Availability   # one row per person per date — a SINGLE source of truth, not per-group
  - person        (FK Person)
  - date          (date)
  - status        (enum: A, AS, AR, X, Q, NA)   # see vocabulary below
  - unique_together: (person, date)

Assignment    # one cell in the "Shift" row — who is covering which Role on which date
  - person        (FK Person)
  - role          (FK Role)
  - date          (date)
  - unique_together: (person, role, date)
  - validators:
      * person.groups must include role.group
      * an Availability(person, date) must exist with status in {A, AS, AR}
      * a person can hold at most one Assignment per (date, role.group)  — no double-booking **inside a group**
      * cross-group assignments on the same date are ALLOWED but must be flagged as warnings (see below)
      * the chosen Role must be effective on the assignment date:
          role.effective_from <= date AND (role.effective_to IS NULL OR date < role.effective_to)

AssignmentChangeLog   # append-only audit log of every Assignment mutation
  - id                (int, PK)
  - timestamp         (datetime, auto_now_add)
  - action            (enum: "create" | "update" | "delete" | "drop")
                                                 # "drop" is a semantic variant of "delete": the assigned
                                                 # person could not or would not fulfill the shift.
                                                 # "delete" is for edits/corrections (e.g. undoing a mistake).
                                                 # DB effect is the same; analytics treat them very differently.
  - person            (FK Person, PROTECT)       # who the assignment applied to
  - date              (date)                     # the date of the assignment
  - role_before       (FK Role, nullable)        # NULL for create
  - role_after        (FK Role, nullable)        # NULL for delete/drop
  - was_forced        (bool)                     # true if written via ?force=true
  - drop_reason       (enum, nullable: "sick" | "personal" | "reassigned" | "shift_canceled" | "other")
                                                 # populated ONLY when action="drop"; NULL otherwise
  - reason            (str, nullable, blank)     # optional free text; good for details like "flu, out 3 days"
  - correlation_id    (UUID, nullable, indexed)  # groups related changes (e.g. a substitution = 1 drop + 1 create
                                                 # that share a correlation_id). Populated when the caller sends one;
                                                 # OK to be NULL for simple one-shot edits.
  - indexes on: (person, date), (role_after, date), (timestamp), (action, drop_reason)

AvailabilityChangeLog  # append-only audit log of Availability mutations (lighter, but same shape)
  - id                (int, PK)
  - timestamp         (datetime, auto_now_add)
  - action            (enum: "create" | "update" | "delete")
  - person            (FK Person, PROTECT)
  - date              (date)
  - status_before     (str, nullable)            # raw availability code, e.g. "A", "X"
  - status_after      (str, nullable)
  - reason            (str, nullable, blank)
  - indexes on: (person, date), (timestamp)
```

### Role supersession workflow

The set of Roles inside a RoleGroup changes roughly once per quarter (decreasing over time). When the operations team redefines the shift model:

1. Every existing `Role` in the affected group gets its `effective_to` set to the switchover date.
2. A new set of `Role` rows is inserted with `effective_from = switchover date` and `effective_to = NULL`.
3. `Assignment` rows still reference the old Role records they were created against — their FKs keep working because the old Roles are never deleted, only expired. Historical data stays intact.
4. New assignments on/after the switchover date can only reference the new Role set (enforced by the validator above).
5. Creating/editing roles in the same group with **overlapping** effective windows for the same `code` is allowed — the `unique_together: (group, code, effective_from)` constraint guarantees no exact duplicates, and queries always filter by date.

A simple management command `python manage.py supersede_roles <group_code> <switchover_date> --from=<fixture.json>` should handle this atomically. For V1, only the current set needs to be seeded — no historical supersession required — but the model must support it from day one.

### Audit logging: how and when log rows are written

All mutations on `Assignment` and `Availability` must produce a corresponding `AssignmentChangeLog` or `AvailabilityChangeLog` row inside the same database transaction as the mutation itself. Prefer an explicit service-layer function over Django signals — signals are easy to accidentally skip in tests, and the write paths are all well-defined (the bulk upsert endpoints). A write helper roughly like:

```python
def apply_assignment_change(*, action, person, date, role_before, role_after,
                             was_forced=False, reason="", correlation_id=None):
    with transaction.atomic():
        # ...mutate the Assignment row...
        AssignmentChangeLog.objects.create(
            action=action, person=person, date=date,
            role_before=role_before, role_after=role_after,
            was_forced=was_forced, reason=reason,
            correlation_id=correlation_id,
        )
```

Write endpoints accept two optional query params that flow into the log:

- `?reason=<urlencoded text>` — captured verbatim in `reason`.
- `?correlation_id=<uuid>` — the frontend generates one UUID per user-initiated operation that spans multiple row changes (e.g. a substitution). For single-cell edits, omit it.

The UI should expose a simple optional "reason" text field when the user is making a change that's likely to matter for later analysis — specifically: clearing/re-assigning a shift, or any `?force=true` save. For routine edits (filling an initially-empty cell), the field stays hidden.

### Example: answering "how often does someone get promoted from Backup?"

Given `is_backup=True` on the relevant Roles, the analytical query is:

```sql
SELECT acl.date, p.initials, r_before.code AS from_code, r_after.code AS to_code
FROM assignment_change_log acl
JOIN person p      ON p.id = acl.person_id
JOIN role r_before ON r_before.id = acl.role_before_id
JOIN role r_after  ON r_after.id  = acl.role_after_id
WHERE acl.action = 'update'
  AND r_before.is_backup = TRUE
  AND r_after.is_backup  = FALSE
  AND acl.date BETWEEN :from AND :to
ORDER BY acl.date;
```

Grouped by `p.initials` it answers "who gets called up most often", by `r_after.code` it answers "which roles get backup-filled most often", by `date` it gives a timeline. A thin `/api/v1/analytics/backup-promotions/?from=&to=&group=` endpoint is a nice-to-have but not required in V1 — as long as the data is there, analysts (including you) can hit the DB directly.

### Tracking drops (someone can't fulfill a shift)

A "drop" is a delete with meaning: the assigned person got sick, had a personal emergency, was reassigned, or the shift itself was canceled. The DB effect is the same as a regular delete (the `Assignment` row goes away), but the log records it with `action="drop"` and a structured `drop_reason` enum so it's cleanly analyzable.

Two user flows trigger a drop:

1. **Direct drop from the Shift cell.** In the per-role view, clearing a filled Shift cell opens a small modal: *"Clearing this assignment. Is this a drop?"* with a choice: "No, just an edit" → `action="delete"`; or "Yes, this is a drop" → pick a reason from the enum plus an optional free-text detail → `action="drop"`.

2. **Cascade from an availability flip.** When the user flips a person's `Avail` to `X` or `-` and that person has existing Assignment(s) on that date, the confirmation modal lists the affected assignments and asks for a drop reason. All cleared assignments get logged as drops under one `correlation_id` shared with the matching `AvailabilityChangeLog` row.

The UI should never silently cascade-delete an assignment when availability changes — always surface the modal.

### Example: answering "how often do people drop due to sickness?"

```sql
SELECT acl.date, p.initials, r_before.code AS role, acl.reason
FROM assignment_change_log acl
JOIN person p      ON p.id = acl.person_id
JOIN role r_before ON r_before.id = acl.role_before_id
WHERE acl.action = 'drop'
  AND acl.drop_reason = 'sick'
  AND acl.date BETWEEN :from AND :to
ORDER BY acl.date;
```

Aggregations follow naturally: drops by person, drops by month, drops per role, drops per reason, drop-to-substitution lag time (by joining on `correlation_id` to find the paired create). No analytics tab is required in V1; having the data cleanly structured is the point.

### Person lifecycle: deactivation

A Person is never deleted. To retire someone, set `active = False`.

Behavior rules:

- All list endpoints (`/people/`, `/availability/`, `/effective-availability/`) filter to `active=True` by default. Pass `?include_inactive=true` to see everyone (for an admin/archive view — out of scope for V1 UI, but the API should support it).
- Deactivated people **do not appear** in the per-role view's person blocks, and are removed from any Shift-cell dropdowns.
- Historical `Assignment` rows referencing deactivated people are preserved and **still render** in the Summary grid and in the "covered by" legend rows of per-role views. The initials still show, just no editable block for that person.
- The Summary's `multi_assignment_days` still includes conflicts involving deactivated people (if they somehow exist historically).
- Reactivating a person (`active = True`) restores them to the editable views without touching their historical data.

### Derived concept: effective availability per group per date

Availability is stored once per person per date. But when viewing or editing a specific role group's schedule, we compute an **effective availability** that downgrades the raw status if the person is already committed elsewhere that day:

```python
def effective_availability(person, group, date):
    raw = Availability.get(person=person, date=date).status  # or "NA" if missing
    if raw in {"X", "NA", "Q"}:
        return {"status": raw, "busy_elsewhere": False, "conflicting_assignments": []}

    # Person is nominally available. Check for assignments in OTHER groups on this date.
    other = Assignment.filter(person=person, date=date).exclude(role__group=group)
    if other.exists():
        return {
            "status": raw,                       # keep underlying status (A/AS/AR)
            "busy_elsewhere": True,              # UI shows a warning badge
            "conflicting_assignments": [         # informational
                {"group": a.role.group.code, "role_code": a.role.code, "role_label": a.role.label}
                for a in other
            ],
        }

    return {"status": raw, "busy_elsewhere": False, "conflicting_assignments": []}
```

**Rule of thumb the UI must enforce:** a cell where `busy_elsewhere=True` renders with an amber warning style. The user can still assign that person, but the action requires an explicit confirmation ("Already assigned to OS Day shift; assign to Tailgate anyway?"). This matches the real-world policy: cross-group same-day is a last resort, not a block.

### Availability vocabulary (matches the spreadsheet)

| stored | display | meaning |
|--------|---------|---------|
| `A`    | A       | Available for shift |
| `AS`   | AS      | Available at summit only |
| `AR`   | AR      | Available remote only |
| `X`    | X       | Not available |
| `Q`    | ?       | Unsure (`?` is reserved in some contexts, store as `Q` and render as `?`) |
| `NA`   | -       | Not answered yet |

### Seed RoleGroups and Roles for V1

All seed Roles use `effective_from` = the app's `SYSTEM_EPOCH` date (set in settings; suggest `2026-01-01`) and `effective_to` = NULL.

**RoleGroups**
| code     | name                                   | coverage_policy |
|----------|----------------------------------------|-----------------|
| OS       | Observing Specialists                  | always          |
| SupSci   | Science Support                        | always          |
| Tailgate | Summit Morning Meeting Coordination    | weekdays_only   |

**OS roles** (`is_backup = true` only for `B`; false for all others)
| code | label              | is_lead | is_remote | is_backup |
|------|--------------------|---------|-----------|-----------|
| 1    | Late shift lead    | true    | false     | false     |
| 2    | Late shift         | false   | false     | false     |
| 3    | Day shift lead     | true    | false     | false     |
| 4    | Day shift          | false   | false     | false     |
| R    | Day shift (remote) | false   | true      | false     |
| B    | Summit backup      | false   | false     | true      |
| T    | Training           | false   | false     | false     |

**SupSci roles**
| code | label           | is_lead | is_remote |
|------|-----------------|---------|-----------|
| S    | Science Support | false   | false     |

**Tailgate roles**
| code | label                        | is_lead | is_remote |
|------|------------------------------|---------|-----------|
| N    | Morning Tailgate Note-Taker  | false   | false     |

(The legacy spreadsheet uses `o` + label "Covered by" — we're promoting the code to `N` and the label to describe the actual responsibility: attending the morning tailgate meeting and taking notes.)

## Anonymized seed data

The real spreadsheet has staff names. For dev/demo, **do not** import real names. Generate a seed fixture that mirrors the real-world membership pattern — OS and SupSci are disjoint populations, Tailgate pulls from both:

- 14 OS-only people (initials `O01`–`O14`, names `"OS Person 01"`, …) — groups = {OS}
- 6 SupSci-only people (initials `S01`–`S06`) — groups = {SupSci}
- 5 people in OS + Tailgate (initials `OT1`–`OT5`) — groups = {OS, Tailgate}
- 3 people in SupSci + Tailgate (initials `ST1`–`ST3`) — groups = {SupSci, Tailgate}
- A 60-day date range starting from today
- Availability per (person, date) with weights ~70% A, 10% X, 10% AS, 5% AR, 5% `?` — **one row per person per date**, shared across whichever groups they belong to
- Plausible assignments that satisfy the validators:
  - Every OS role code filled on most days
  - SupSci filled ~5 days/week
  - Tailgate filled on weekdays, occasionally gapped on weekends
  - **At least 3 clear examples** in the seed where a single person has both a group shift (OS or SupSci) AND a Tailgate assignment on the same date — this is the warning pattern we want to demo.

Provide this as a `seed_demo` Django management command so it's idempotent and easy to re-run.

## REST API

```
GET    /api/v1/role-groups/                       list groups
GET    /api/v1/roles/?group=OS                    list roles, filterable by group code
GET    /api/v1/people/?group=OS                   list people, filterable by group code

# Availability is per-person-per-date (single source of truth, not per-group)
GET    /api/v1/availability/?from=YYYY-MM-DD&to=YYYY-MM-DD&person=<id>
PUT    /api/v1/availability/                      bulk upsert: [{person_id, date, status}, ...]

# Effective availability is derived per group — used to render per-role views
GET    /api/v1/effective-availability/?group=OS&from=YYYY-MM-DD&to=YYYY-MM-DD
       returns [{person_id, date, status, busy_elsewhere, conflicting_assignments: [...]}]

GET    /api/v1/assignments/?group=OS&from=...&to=...
PUT    /api/v1/assignments/                       bulk upsert with optional ?force=true query param
       Behavior:
       - If a request would create a cross-group same-day assignment (the person already has an
         assignment in a different group on that date), the DEFAULT (no ?force) is to return 409
         with a "warnings" payload listing each conflict and NOT persist any row.
       - With ?force=true, the writes persist AND the response includes a "warnings" array so the
         client can show a post-hoc "saved with conflicts" toast.
       - Within-group double-book always returns 400 regardless of ?force.
DELETE /api/v1/assignments/                       bulk delete by (person_id, role_id, date) tuples
       Optional query params:
       - ?drop=true                   — mark this removal as a real-world "drop" (person can't fulfill);
                                         log rows are written with action="drop" instead of "delete"
       - ?drop_reason=<enum>          — required when ?drop=true; one of sick/personal/reassigned/shift_canceled/other
       - ?reason=<text>               — optional free-text detail
       - ?correlation_id=<uuid>       — ties this drop to a sibling create (substitution) in the log

# Read-only audit log endpoints
GET    /api/v1/assignment-history/?from=&to=&person=&group=&only_forced=false
       returns AssignmentChangeLog rows, filterable; default ordering is (date desc, timestamp desc)
GET    /api/v1/availability-history/?from=&to=&person=
       returns AvailabilityChangeLog rows, same shape

GET    /api/v1/summary/?from=YYYY-MM-DD&to=YYYY-MM-DD&groups=OS,SupSci,Tailgate
       returns a denormalized payload optimized for the Summary grid:
       {
         "dates": ["2026-04-01", ...],
         "rows": [
           {"role_group": "OS", "role_code": "1", "label": "OS Late shift - Shift Manager",
            "cells": ["KP", "KP", "EC", ...]},                 # initials per date, "" if unfilled
           ...
         ],
         "totals_available": {"OS": [11, 11, 12, ...], "SupSci": [...], "Tailgate": [...]},
         "multi_assignment_days": [                             # informational — already-occurred overlaps
           {"person_initials": "OT1", "date": "2026-04-03",
            "assignments": [{"group": "OS", "role": "4"}, {"group": "Tailgate", "role": "o"}]}
         ]
       }
```

The `?force` pattern on `PUT /assignments/` is deliberate: it makes every cross-group same-day assignment a two-step action, preventing silent overlaps. Bulk upserts should be transactional.

## Frontend — two main views

### 1. Summary view (`/`) — read-only, mirrors the spreadsheet's `Summary` tab

- **Layout:** wide grid. Frozen left column (role label). Frozen top row (dates). Each data cell shows person initials or `-` if unfilled.
- **Date range:** date-range picker top-left, defaults to today through today+30. Horizontal scroll for the date columns.
- **Row grouping:** group rows by RoleGroup with a subtle separator row between groups (matches spreadsheet's blank row between OS, SupSci, Camera, etc.).
- **Header rows above the role rows:**
  - Date row (formatted `MMM DD`)
  - Weekday row (`Mon`/`Tue`/...) — weekend columns get a light grey background
  - "Total available per group" row (aggregated count from availability)
- **Cell coloring:**
  - Lead roles (is_lead=true): bold text
  - Remote roles (is_remote=true): italic text
  - Empty cell where the role's group has `coverage_policy=always`: **light red background** (missing coverage is an error)
  - Empty cell where the role's group has `coverage_policy=weekdays_only` AND the date is Sat/Sun: **neutral grey** (coverage not needed)
  - Empty cell where the role's group has `coverage_policy=weekdays_only` AND the date is a weekday: **light red background** (missing coverage is an error)
  - Initials of a person with **multiple assignments that date across groups**: small dot indicator next to the initials (e.g. `OT1•`) with a tooltip listing all their assignments for that date. Informational — never an error state.
- No editing here. Clicking a cell jumps to the per-role view for that group + date.

### 2. Per-role view (`/groups/:groupCode`) — editable, mirrors a per-role sheet

- Same wide-grid pattern as the spreadsheet's `OS` / `SupSci` / `Tailgate` tabs:
  - Header rows: title, dates, weekday, "Total people available per day" (counts of raw availability status `A`/`AS`/`AR`)
  - Role-code legend rows (one row per Role in this group), with a computed "who is covering this role on this date" cell — read-only, derived from Assignments
  - Per-person blocks: each person occupies **two stacked rows** — `Avail` and `Shift`
- **`Avail` row semantics:** this is the person's availability for the *date* (not for the group). Editing it here updates the single per-person-per-date availability record, which means the same change will be visible when viewing any other group's per-role page for that person + date. The UI should make this clear — e.g. a subtle tooltip on the Avail cell: "Shared across all groups this person belongs to."
- **`Shift` row semantics:** dropdown of the group's role codes, restricted to roles compatible with the person's availability:
  - If raw availability is `X`, `-`, or `?` → Shift cell disabled.
  - If raw availability is `A`/`AS`/`AR` AND person has no assignments in other groups that date → normal editable state.
  - If raw availability is `A`/`AS`/`AR` AND person has an assignment in another group that date (`busy_elsewhere=true`) → cell renders with an **amber warning background** and a tooltip listing the conflicting assignment(s). Selecting a shift pops a confirmation modal: *"OT1 is already covering OS Day shift on 2026-04-03. Assign them to Tailgate anyway? Use only if no other options."* Confirming sends `PUT /assignments/?force=true`.
- Inline edit on click. Debounced bulk PUT every 500ms of inactivity, or on blur. Force-confirmation assignments bypass the debounce and submit immediately after the user confirms.
- Show a toast on save success/failure. Force-saved assignments get a distinct toast style ("Saved with conflict warning").
- Changing `Avail` to `X` or `-` should prompt to clear any existing assignment(s) for that date (in this group and any other) and surface a confirmation before doing so.
- Date range picker matches Summary view; default same window.

## Out of scope for V1 (do not build, but design so they can be added later)

- Authentication / per-user permissions
- Holiday calendar overlays (CL/US holidays) — `coverage_policy` may later gain a `weekdays_and_weekdays_off_holidays` variant
- Statistics tabs (shift counts per person, fairness reports). Weekend and holiday dates should remain queryable so future statistics can apply different weights.
- **Four-day shift blocks / rotation units** for OS and SupSci — in practice shifts come in 4-day chunks, but V1 treats every day as independent. A future Block model can group consecutive Assignments.
- **Auto-scheduler / suggestion engine** to populate shifts automatically from availability + fairness rules. For now, all assignments are manual.
- Other role groups (Camera, Calibration, Electric, Electronic, Triage, TestSci, Admin)
- Email/Slack notifications
- Import from the existing Google Sheet
- **Dedicated UI for browsing history.** The backend audit logs (`AssignmentChangeLog`, `AvailabilityChangeLog`) and their read endpoints are *in* scope. A polished history-browser UI — filters, diff views, charts — is not. For V1, analysts query the log via API or directly against the DB.
- Mobile layout (desktop-first; basic responsive is fine, but no mobile-specific work)

## Assumptions (confirm before building)

- `TIME_ZONE = "America/Santiago"` in Django settings. All dates are interpreted in Chile time. Shifts that cross midnight (e.g. OS Late 22h–8h) are tagged to the date on which they *start* — matching the spreadsheet convention.
- `SYSTEM_EPOCH = 2026-01-01` is the `effective_from` for all seed Roles.
- No authentication in V1 means the backend effectively trusts its caller. Do not deploy this V1 outside a trusted network.

## Acceptance criteria

1. `docker-compose up` brings up the backend on `:8000` and the frontend on `:5173`.
2. `python manage.py seed_demo` populates anonymized OS + SupSci + Tailgate data for 60 days, including people who belong to multiple groups.
3. Visiting `/` shows the Summary grid with all three groups visible, filled cells, missing-coverage highlighting, and multi-assignment indicators on days where a person covers more than one group.
4. Visiting `/groups/OS`, `/groups/SupSci`, or `/groups/Tailgate` lets me change a person's availability and assign them a shift; the change is reflected in the Summary view on refresh.
5. Editing a person's `Avail` cell on one group's page updates it for the same person + date on every other group's page (single source of truth).
6. Trying to assign a person whose availability is `X`, `-`, or `?` returns a 400 with a clear error message.
7. Trying to double-book a person on the same date in the same group returns a 400 regardless of `?force`.
8. Creating or updating a Person with `groups = {OS, SupSci}` returns a validation error (the two groups are mutually exclusive by config).
9. Trying to assign a person to a Tailgate shift when they're already in an OS shift that date **without `?force`** returns a 409 with a `warnings` payload and no row is written.
10. The same request with `?force=true` writes the row and returns 200 with the `warnings` payload in the response body.
11. In the UI, attempting step 9 through the per-role view shows a confirmation modal; confirming sends the forced request and shows the "saved with conflict warning" toast.
12. The Summary grid shows a dot indicator next to `OT1` on the overlap date, with a tooltip listing both assignments.
13. On a Saturday or Sunday, an empty Tailgate cell in the Summary renders in neutral grey (not red), because `Tailgate.coverage_policy = weekdays_only`. Empty OS/SupSci cells on the same dates still render red.
14. A Role with `effective_to` set before a target date cannot be referenced by new Assignments on that date — the validator rejects the write with a clear error message. Running `supersede_roles` against a fixture is atomic: either all new Role rows land and all old ones get `effective_to` set, or nothing persists.
15. Setting a person's `active = False` immediately removes them from `/groups/:code` person blocks and dropdowns, but their existing assignments still render in the Summary. Setting `active = True` restores them.
16. **Every** Assignment create/update/delete writes exactly one `AssignmentChangeLog` row in the same transaction. Same for Availability. If the mutation is rolled back, no log row is left behind.
17. A write accompanied by `?reason=covering+for+flu&correlation_id=<uuid>` persists both values onto the log row.
18. Moving a person from the Backup role to a non-backup role (e.g. `B` → `2`) on the same date produces exactly one `AssignmentChangeLog` row with `action=update`, `role_before.is_backup=true`, `role_after.is_backup=false`. A backend test must verify this and demonstrate the example SQL query returning the row.
19. `GET /api/v1/assignment-history/?only_forced=true` returns only log rows where `was_forced=true`.
20. Clearing a filled Shift cell with `?drop=true&drop_reason=sick` produces one `AssignmentChangeLog` row with `action="drop"`, `drop_reason="sick"`, and no leftover `Assignment` row. Clearing the same cell without `?drop=true` produces a row with `action="delete"` and `drop_reason=NULL`.
21. `DELETE /api/v1/assignments/?drop=true` without `?drop_reason=` returns 400.
22. Flipping a person's availability to `X` while they have existing assignments produces: one `AvailabilityChangeLog` row (status_before="A", status_after="X"), N `AssignmentChangeLog` rows with `action="drop"`, and all N+1 rows share the same `correlation_id`.
23. All backend tests pass with `pytest`. All frontend tests pass with `vitest`. Include at least backend tests for: (a) within-group double-book rejection, (b) Person OS+SupSci validation error, (c) cross-group same-day rejection without `?force`, (d) cross-group same-day success with `?force=true` writes a log row with `was_forced=true`, (e) availability edit visible across groups, (f) Role supersession atomicity, (g) Assignment validator rejects expired Roles, (h) deactivated people hidden from active queries but historical assignments preserved, (i) audit log rollback behavior, (j) backup-promotion query returns the expected row, (k) drop log row written correctly with structured reason, (l) availability-flip cascade produces correlated drop log rows.

## Deliverables

- `backend/` — Django project
- `frontend/` — Vite + React + TS project
- `docker-compose.yml` at repo root
- `README.md` with setup, seed, and "how to add a new role group" instructions
- `ARCHITECTURE.md` with a one-page diagram of models + API + frontend routes

## Style notes

- Backend: black + ruff defaults, type hints on all public functions.
- Frontend: prettier defaults, ESLint with `@typescript-eslint/recommended`.
- Commit history: small, focused commits with conventional-commit prefixes.
