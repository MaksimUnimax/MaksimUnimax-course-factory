# Curriculum map

`curriculum_map.md` здесь означает «карта курса».

## 1. Course identity

- Course title: Как новичку управлять AI-разработкой через ChatGPT, Codex, сервер и GitHub
- Working course type: Практический вводный курс для абсолютных новичков
- Target audience: Абсолютные новички, не программисты, которые учатся управлять AI-разработкой через ChatGPT, Codex, сервер и GitHub
- Learner starting level: Старт с нулевой технической уверенности, без опыта Git/GitHub, терминала, сервера и Codex workflow
- Course goal: Научить запускать небольшой AI-assisted workflow, где ChatGPT планирует следующий шаг, Codex выполняет один bounded task, сервер хранит проект, GitHub сохраняет историю, а ученик проверяет результат перед следующим шагом
- Expected practical result: Публичный GitHub-репозиторий, серверная папка проекта, базовая документация source-of-truth, первый controlled Codex report, read-only preview структуры проекта по public IP и повторяемый one-step workflow

## 2. Source basis

- Accepted source digest: `input/source_pack/source_digest.md` (`PASS_SOURCE_DIGEST_READY`)
- Main source topics used: связка ChatGPT → Codex → сервер → GitHub; правило одного шага; документация как source of truth; Git/GitHub и SSH deploy key; запрет `localhost` для learner-facing адреса; read-only публичная проверка; различие agent и tool
- Main source procedures used: загрузка стартовых документов; проверка публичного repo перед первым prompt; создание первого controlled run; создание проекта и первого commit; проверка push; проверка public IP preview; чтение Codex report и сверка результата
- Important vocabulary used: ChatGPT, Codex, сервер, Git, GitHub, commit, push, repo, SSH deploy key, localhost, public IP, read-only page, agent, tool, prompt, report, source-of-truth
- Safety constraints carried forward: не печатать приватные ключи и секреты; не показывать `localhost` как адрес для ученика; не смешивать много задач в одном шаге; не гадать при нехватке фактов; не начинать без документации; source materials не являются рабочим репозиторием ученика
- Source gaps carried forward: полный roadmap первого проекта; полный `AGENTS.md`; полный набор prompt templates; техническое ТЗ; module map; current status; source/runtime boundary; vendor notes; примеры финальных Codex reports
- Human decisions carried forward: курс для абсолютных новичков; практический, а не теоретический формат; один небольшой проект; MVP на 6-8 уроков; proof-first и one-step-at-a-time; простой русский язык; без advanced production architecture; gaps остаются видимыми

## 3. Course shape

- Recommended number of lessons: 7
- Recommended lesson format: каждый урок = короткое объяснение, одна практическая задача, одна проверка результата, один короткий вывод
- Recommended progression model: от ролей и документов к GitHub и серверу, затем к controlled run, проверке результата и повторяемому циклу
- What the course is: практический вводный маршрут для человека с нулевой технической уверенностью, который учится управлять AI-workflow по одному шагу
- What the course is not: не полный академический курс, не курс по production security, не курс по сложной backend-архитектуре, не курс по автономным multi-agent схемам

## 4. Lesson list

| Lesson | Title | Main purpose | Learner outcome | Source basis |
|---:|---|---|---|---|
| 1 | Роли в workflow и правило одного шага | Понять, кто за что отвечает в цепочке ChatGPT → Codex → сервер → GitHub | Ученик может объяснить, чем отличаются ChatGPT, Codex, сервер, GitHub, agent и tool, и почему шаги нельзя смешивать | `source_digest.md` + `course_brief.md` + Instructional inference |
| 2 | Документы как источник правды | Научиться опираться на документы до действий | Ученик может найти accepted source digest, course brief и run request, и отличить source-of-truth от предположения | `source_digest.md` + `course_brief.md` |
| 3 | GitHub и история изменений | Понять, зачем нужны repo, commit и push | Ученик может проверить, что изменения сохраняются в GitHub, и назвать, что нельзя печатать как секрет | `source_digest.md` + `course_brief.md` + Source policy |
| 4 | Сервер и публичная проверка | Разобрать разницу между локальным адресом и learner-facing public IP | Ученик может проверить read-only preview по public IP и объяснить, почему `localhost` нельзя показывать ученику | `source_digest.md` + `course_brief.md` |
| 5 | Controlled run и run request | Понять, что именно запускает Codex и что он не делает | Ученик может прочитать `RUN_REQUEST.md`, определить агента, входные файлы и границы задачи, и понять, когда run должен быть остановлен | `RUN_REQUEST.md` + `source_digest.md` + `course_brief.md` + Instructional inference |
| 6 | Проверка результата и статус | Научиться сверять output, status.json и ожидаемые файлы | Ученик может проверить, соответствует ли output требуемому файлу и статусу, и заметить несоответствие | `source_digest.md` + `OUTPUT_CONTRACT.md` + `TESTS.md` + Instructional inference |
| 7 | Повторяемый one-step workflow | Собрать все элементы в повторяемую схему | Ученик может повторить короткий цикл plan → execute → verify → commit/push → report на одном bounded task без лишних предположений | `course_brief.md` + `source_digest.md` + Instructional inference |

## 5. Lesson order rationale

1. Сначала идут роли и правило одного шага, потому что у ученика нет технической базы и ему нужно понять, кто что делает, прежде чем он начнёт действовать.
2. Потом идут документы как source of truth, потому что весь workflow опирается на accepted digest, brief и request, а не на догадки.
3. Затем GitHub и история изменений, потому что ученик должен понять, где сохраняется результат и как выглядит контролируемое изменение.
4. После этого сервер и публичная проверка, потому что нужно уметь отличить локальный адрес от learner-facing адреса и проверить read-only preview.
5. Затем controlled run и run request, потому что это первая точка, где Codex выполняет bounded task, и ученику нужно видеть границы запуска.
6. Потом проверка результата и статус, потому что без сверки output/status/run files нельзя считать шаг завершённым.
7. В конце идёт повторяемый сквозной цикл, потому что только после всех предыдущих уроков ученик может собрать workflow без лишнего стресса и с понятной проверкой.

## 6. Prerequisite chain

| Lesson | Requires before this lesson | Enables after this lesson |
|---:|---|---|
| 1 | Базовое понимание, что курс практический и шаги идут по одному | Понимание ролей и правил работы |
| 2 | Урок 1 | Работа по документам и acceptance-критериям |
| 3 | Урок 2 | Осмысленная проверка истории изменений и GitHub-сохранения |
| 4 | Урок 3 | Проверка сервера и публичного preview |
| 5 | Урок 4 | Чтение run request и понимание controlled run |
| 6 | Урок 5 | Сверка output, status.json и ожидаемых файлов |
| 7 | Уроки 1-6 | Повторяемый полный цикл без догадок |

## 7. Outcome per lesson

| Lesson | Observable outcome |
|---:|---|
| 1 | Ученик объясняет, какую роль в workflow выполняет каждое звено, и почему следующий шаг нельзя делать до проверки предыдущего |
| 2 | Ученик находит accepted source digest и course brief, и отмечает, какие документы являются source of truth |
| 3 | Ученик проверяет, что результат сохраняется как commit/push в GitHub, и понимает, какие данные нельзя раскрывать |
| 4 | Ученик проверяет публичный preview по public IP и объясняет, почему `localhost` не подходит для учебной выдачи |
| 5 | Ученик читает run request и определяет, какой agent, какие входные файлы и какой границей задачи управляют запуском |
| 6 | Ученик сверяет output со статусом и ожидаемыми файлами, и отличает success от blocked/stop-ситуации |
| 7 | Ученик повторяет короткий workflow от plan до report без смешивания нескольких задач в одном шаге |

## 8. Practice per lesson

| Lesson | Practice task direction |
|---:|---|
| 1 | Сопоставить роли ChatGPT, Codex, сервера и GitHub с конкретными действиями в одном примере |
| 2 | Найти в наборе файлов тот документ, на который можно опираться, и отметить, чего пока не хватает |
| 3 | Проверить repo, commit и push в учебном сценарии и показать, где хранится история |
| 4 | Открыть read-only preview и сравнить public IP с `localhost` |
| 5 | Прочитать `RUN_REQUEST.md` и перечислить допустимые входы и границы одного запуска |
| 6 | Сверить `curriculum_map.md` или `STOP_REPORT.md` со статусом и списком входных файлов |
| 7 | Пройти мини-чеклист на одном bounded task и оформить короткий report о результате |

## 9. Assessment idea per lesson

| Lesson | Assessment idea |
|---:|---|
| 1 | Сценарий: кто должен сделать следующий шаг и почему |
| 2 | Найти, какой документ является источником правды, а какой является лишь вспомогательным |
| 3 | Определить, что нужно commit/push, а что нельзя раскрывать |
| 4 | Выбрать правильный адрес для ученика и объяснить выбор |
| 5 | Решить, можно ли запускать agent или нужно остановиться |
| 6 | Сказать, совпадает ли output с ожидаемым результатом |
| 7 | Подтвердить, что workflow можно повторить без догадок |

## 10. Difficulty progression

- Сначала вводятся роли, документы и правила безопасности, потому что это минимальный язык курса.
- Практика начинается рано, но сначала это проверка документов и адресов, а не сложное действие.
- Верификация появляется уже в первых уроках и становится обязательной привычкой на каждом шаге.
- Многошаговое мышление появляется только после того, как ученик понимает preview, run request и output checking.
- Заранее отложены production security, сложная архитектура и автоматические multi-agent сценарии, потому что они не нужны для MVP и перегружают новичка.

## 11. Topics excluded from MVP

| Excluded topic | Why excluded | Can be added later? |
|---|---|---|
| Production security и сложные политики доступа | Это не нужно для первого практического результата и уводит в продакшен-слой | Да |
| Сложная backend-архитектура | Слишком рано для абсолютного новичка | Да |
| Платежи и пользовательские аккаунты | Не входят в исходный рабочий сценарий курса | Да |
| Advanced CI/CD | Переусложняет MVP и не помогает одному bounded task | Да |
| Автоматические multi-agent цепочки | Противоречат правилу одного шага для этого курса | Да |
| OpenScript Agent Lab internals и соседние проекты | Не относятся к текущему учебному маршруту и не должны отвлекать | Да |

## 12. Source gaps and human decisions carried forward

| Gap or decision | Why it matters | Who must resolve it | Suggested timing |
|---|---|---|---|
| Полный roadmap первого проекта | Может понадобиться для следующего этапа, но не блокирует MVP-карту курса | Человек/автор курса | Перед следующим расширением курса |
| Полный `AGENTS.md` рабочего проекта | Нужен для более точных agent rules | Человек + Source Analyst/оператор, если добавляется новый source pack | До следующего агентского этапа при необходимости |
| Полный набор prompt templates | Поможет следующему агенту, но не блокирует текущую карту | Человек/автор курса | Перед Lesson Designer, если нужен более точный шаблон |
| Техническое ТЗ | Нужен для точной декомпозиции, если курс расширится | Человек/оператор | До расширения MVP |
| Module map | Уточняет структуру проекта, но сейчас достаточно high-level маршрута | Человек/автор курса | При следующей итерации курса |
| Current status | Полезен для согласования, но не обязателен для этой MVP-карты | Человек/оператор | Когда курс пойдёт в следующую стадию |
| Source/runtime boundary | Важен для точных ограничений, если будут новые run types | Человек/оператор | До следующего технического расширения |
| Vendor notes | Нужны только если появятся внешние ограничения или особенности платформы | Человек/оператор | По мере необходимости |
| Примеры финальных Codex reports | Помогают next agent, но не нужны для базовой карты | Человек/оператор | Перед следующим этапом, если хотят усилить шаблоны |
| Какие дополнительные документы Student Kit подключать дальше | Важное решение для следующей версии source pack | Человек/оператор | После этого MVP, перед новым source digest |

## 13. Risks

| Risk | Mitigation |
|---|---|
| Ученик путает ChatGPT и Codex | На каждом уроке повторять, кто планирует, а кто выполняет bounded task |
| Ученик считает `localhost` публичным адресом | Сравнивать `localhost` и public IP на конкретном примере и проверять preview отдельно |
| Ученик пропускает verification | Делать проверку обязательной частью каждого урока и каждого run |
| Ученик думает, что gaps уже решены | Отдельно хранить и показывать список gaps, не прятать его в тексте |
| Ученик пытается сделать несколько задач за один шаг | Держать один bounded task на урок и одну проверку результата |
| Ученик перегружается терминологией | Вводить термины только тогда, когда они нужны для действия, и объяснять их простым русским |

## 14. Readiness for next agent

PASS_CURRICULUM_MAP_READY

## 15. STOP status

PASS_CURRICULUM_MAP_READY
