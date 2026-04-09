# AGENTS.md

## Mission
Build this project strictly from the spec and active task files.

## Authority order
When instructions conflict, follow this order:
1. `docs/specs/content_engine_v2.md`
2. `docs/tasks/active_sprint_02.md`
3. `docs/tasks/next_task.md`
4. `docs/state/current_state.md`

## Operating rules
1. Do not improvise outside the spec.
2. Do not add features not listed in the current task.
3. Do not refactor unrelated files.
4. Keep implementation minimal and modular.
5. Prefer explicit data contracts over loose dicts.
6. Use typed outputs for agent results when helpful.
7. Keep coordinator logic separate from agent instructions.
8. Keep tools separate from agent definitions.
9. Every change must update `current_state.md`.
10. If blocked, write the blocker into `current_state.md` instead of inventing a workaround.

## Development loop
For every task:
1. Read the spec
2. Read `current_state.md`
3. Read `active_sprint_02.md`
4. Read `next_task.md`
5. Execute only the next task
6. Run relevant tests
7. Update `current_state.md`, and `next-task.md`
8. Update `decisions.md` if architecture changed

## Guardrails
- No UI unless explicitly assigned
- No persistence unless explicitly assigned
- No Notion integration unless explicitly assigned
- No additional agents unless explicitly assigned

## Definition of done
A task is done only when:
- code is implemented
- tests for that task exist or are updated
- `docs/state/current_state.md`, and `docs/tasks/next_task.md` are updated