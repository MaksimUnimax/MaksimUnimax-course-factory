# Source Analyst output contract

## Основной файл результата

Source Analyst должен создать файл:

`source_digest.md`

Если работа невозможна, Source Analyst должен создать файл:

`STOP_REPORT.md`

## Обязательная структура source_digest.md

Файл `source_digest.md` должен содержать следующие разделы:

### 1. Source inventory

Список источников.

Для каждого источника указать:

- название;
- путь или идентификатор;
- тип источника;
- краткое назначение;
- можно ли использовать источник для курса.

### 2. Main topics

Основные темы, найденные в источниках.

### 3. Key procedures

Рабочие процессы, шаги, инструкции или процедуры.

### 4. Terms and vocabulary

Термины, которые нужно объяснить ученику.

### 5. Target audience clues

Что источники говорят или подразумевают об аудитории.

### 6. Safety constraints

Ограничения, риски, запреты, safety-условия.

### 7. Contradictions

Противоречия между источниками.

Если противоречий нет, написать:

`Явных противоречий не найдено.`

### 8. Missing information

Чего не хватает для создания курса.

### 9. License and privacy concerns

Риски приватности, секретов, лицензий, закрытых материалов.

### 10. Usable source facts

Факты, которые можно использовать дальше.

### 11. Instructional inferences

Методические выводы, которые не являются прямыми фактами источника.

### 12. Required human decisions

Решения, которые должен принять человек.

### 13. STOP status

Один из вариантов:

- PASS_SOURCE_DIGEST_READY
- STOP_SOURCE_MISSING
- STOP_SOURCE_TOO_LARGE_NOT_DIGESTED
- STOP_AUDIENCE_UNKNOWN
- STOP_COURSE_GOAL_UNKNOWN
- STOP_SOURCE_CONTRADICTION
- STOP_SOURCE_LICENSE_OR_PRIVACY_RISK
- STOP_DOMAIN_SOURCE_REQUIRED
- STOP_SAFETY_RISK
- STOP_HUMAN_APPROVAL_REQUIRED

## Запреты

В `source_digest.md` нельзя:

- писать уроки;
- писать curriculum map;
- писать course brief;
- скрывать пробелы;
- выдавать предположение за факт источника;
- использовать общие знания как факт источника.
