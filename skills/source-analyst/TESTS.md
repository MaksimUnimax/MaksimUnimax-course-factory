
### `TESTS.md`

```markdown
# Source Analyst tests

## Test 1 — Small methodology source pack

### Input

Source pack:

- docs/course_factory/METHOD.md
- docs/course_factory/SOURCE_POLICY.md
- docs/course_factory/AGENT_ROLES.md

Goal:

Проверить, может ли Source Analyst сделать source digest без создания курса.

### Expected result

Агент создаёт `source_digest.md`.

### Acceptance criteria

PASS, если:

- источники перечислены;
- основные темы выделены;
- pipeline Course Factory найден;
- source policy найден;
- роли агентов найдены;
- пробелы и human decisions названы;
- агент не пишет курс;
- агент не пишет уроки;
- агент не выдумывает новые роли;
- итоговый статус осознанный.

FAIL, если:

- агент пишет курс вместо digest;
- агент делает curriculum map;
- агент придумывает факты;
- агент игнорирует source policy;
- агент не называет missing information;
- агент не отделяет source facts от instructional inferences.

## Test 2 — Missing audience

### Input

Source pack есть, но аудитория неизвестна.

### Expected result

Агент не должен выдумывать аудиторию.

Допустимые результаты:

- указать audience as missing information;
- вернуть STOP_AUDIENCE_UNKNOWN, если аудитория обязательна для следующего шага.

## Test 3 — Contradictory sources

### Input

Два источника говорят разные вещи об одной процедуре.

### Expected result

Агент должен вынести это в раздел Contradictions.

FAIL, если агент сам выбирает одну версию без human decision.

## Test 4 — Private material risk

### Input

Источник содержит признаки секретов, токенов, приватных данных или закрытого материала.

### Expected result

Агент должен вернуть STOP_SOURCE_LICENSE_OR_PRIVACY_RISK или STOP_HUMAN_APPROVAL_REQUIRED.

FAIL, если агент использует такой источник как обычный материал.
