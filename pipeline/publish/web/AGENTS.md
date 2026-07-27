<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# UI conventions

Good UI here means **things do what you'd expect**. These rules exist because each was
broken in a way nobody noticed until a user hit it.

## Clickability

1. **If it does something, it looks like it.** Pointer cursor + a visible hover state.
   Tailwind v4 dropped the preflight rule that gave buttons a pointer cursor — all 64
   buttons on a profession page rendered with the default arrow until `globals.css` put
   it back. Don't remove that base rule.
2. **If it doesn't do anything, it must not look like it does.** No pointer/hover
   affordance on inert elements.
3. **Clickable means keyboard-reachable.** Use a real `<button>`/`<a>` where possible;
   otherwise `role="button"` + `tabIndex={0}` + an Enter/Space `onKeyDown`, and route it
   through the *same* handler as the mouse path rather than duplicating the logic. Only
   genuinely interactive elements get a tab stop — a no-data map state is not a control.
4. **Say what it will do.** `title` / `aria-label` describe the action ("open this
   state's Fraud items"), not just the value.
5. **The destination confirms the click landed.** Don't leave the user hunting. Prefer
   *filtering* to what they clicked over merely highlighting it — and when you filter,
   the filter must be visible and removable (see below).

Watch for **affordance through an ancestor**: an element that "works" only because a
parent has the handler. No lint rule catches it — it's how the category chips ended up
clickable-looking, mouse-only, and keyboard-dead.

## Filters must be visible and removable

Any filtering the UI applies on the user's behalf gets a stated, dismissible control.
A filter the user can't see is an invisible reason they're not seeing everything.

Derive filter state from props; track only what the user *dismissed*. Mirroring a prop
into state needs a sync effect, and `setState` inside an effect cascades renders
(`react-hooks/set-state-in-effect` will flag it). Key the dismissal so clearing one
filter doesn't suppress the next.

## The click contract

| You click | You get |
|---|---|
| a value cell | the Sheet, focused on that field |
| a category chip | the Sheet, **filtered** to that category |
| a state (any view) | that state's detail Sheet |
| a column header | sorting/filtering — never navigation |

A state is the primary object and appears in nearly every view. Opening its detail is a
shared capability, not a per-view prop: call `useOpenStateDetail()` from
`components/state-focus.tsx`. It returns `null` outside a provider, so a view can ask
whether detail is available and render itself non-interactive rather than showing a dead
affordance.

## Color

**Every color meaning lives in `config/web_colors.yaml`** and is generated into
`src/lib/web-colors.ts` by `scripts/generate-colors.mjs`. Never hardcode a Tailwind hue
in a component — if you're reaching for `bg-sky-50`, the meaning needs a name in the
yaml. Semantic roles today: `attention`, `highlight`, `restrictive`, `permissive`,
`interaction` (the UI talking about itself — focus, landing, active filter), `verified`
(a claim checked verbatim against the statute).

Need a class shape that doesn't exist (a ring, a subtle panel tint)? Add it to
`hueClasses()` so every role gets it — don't hand-roll it in one component.

Dynamic class names are where Tailwind's content scan silently drops styles. After
touching colors, check a computed style in the browser, not just that it typechecks.

## Absence

Three different things are not the same and must not render identically:

| Meaning | Where it comes from |
|---|---|
| **not addressed** — the statute is silent | evidence node absent for a field in the profession's schema |
| **no data** — we never extracted it | no record for that cell |
| **coverage gap** — we couldn't get the corpus | `coverage_gap` / `coverage_gap_label` |

A bare `—` for all three hides real findings: 27,806 (state, field) pairs across 67
professions were silently dropped from the Sheet before "not addressed" existed.
