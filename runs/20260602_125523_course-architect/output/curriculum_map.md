# Curriculum map

`curriculum_map.md` здесь означает «карта курса».

## 1. Course identity

- Course title: Управляемый AI-workflow для новичка
- Working course type: Вводный практический курс / учебный проект
- Target audience: Полные новички
- Learner starting level: С нуля
- Course goal: Научиться управлять AI-разработкой как последовательным и проверяемым процессом
- Expected practical result: Учебный проект с понятной цепочкой артефактов, проверок и handoff между агентами

## 2. Source basis

- Accepted source digest: `runs/20260602_125523_course-architect/input/upstream_artifacts/20260602_124454_source-analyst/source_digest.md`
- Main source topics used: управляемый agent workflow; правило одного шага; проверка состояния перед изменением; GitHub как история проекта; сервер и публичная проверка; документация как источник правды; безопасность секретов
- Main source procedures used: один раз загрузить исходники и выбрать настройки; подготовить точное задание; выполнить одну ограниченную задачу; проверить результат; только потом переходить к следующему шагу
- Important vocabulary used: source material; source digest; course brief / «Задание на курс»; agent; tool; commit; push; localhost; public GitHub; workflow
- Safety constraints carried forward: не показывать `localhost` как адрес для ученика; не печатать секреты, токены и `.env`; не смешивать несколько задач в один запуск; не запускать следующий агент без готового исходного разбора
- Source gaps carried forward: нет полного примера `AGENTS.md`; нет шаблонов Codex prompt; нет примеров хорошего и плохого Codex report; нет примера безопасного deploy key workflow; нет карты модулей учебного проекта; нет чётких критериев готовности каждого этапа
- Human decisions carried forward: точный размер первого курса; глубина объяснения Git и сервера; нужен ли отдельный урок про безопасность секретов; делать ли первый проект более простым workflow или «фермой агентов»; какие артефакты считать обязательными для следующего агента

## 3. Course shape

- Recommended number of lessons: 6
- Recommended lesson format: короткое объяснение + одна практическая задача + одна проверка результата
- Recommended progression model: от понимания исходников и правил к одному контролируемому действию, затем к проверке результата, передаче артефактов и безопасному завершению
- What the course is: вводный практический курс про управляемый AI-workflow, source grounding и проверяемые шаги
- What the course is not: не production-платформа, не полный курс по программированию, не учебник по продвинутому prompt engineering, не полноценный курс по деплою и не каталог всех возможных агентских сценариев

## 4. Lesson list

| Lesson | Title | Main purpose | Learner outcome | Source basis |
|---:|---|---|---|---|
| 1 | Исходники, brief и границы курса | Понять, что является source material, что является course brief, и что нельзя смешивать | Ученик различает исходные материалы, курс-бриф и downstream artifacts | Source digest + course brief; Instructional inference |
| 2 | Проверка состояния перед изменением | Закрепить правило «сначала доказать текущее состояние, потом менять» | Ученик проверяет файлы, `git status`, страницу или endpoint перед правкой | Source digest; Instructional inference |
| 3 | Разбор исходников и source digest | Научиться выделять темы, процедуры, термины, gaps и human decisions | Ученик извлекает из источников факты, ограничения и недостающую информацию | Source digest; Instructional inference |
| 4 | Один controlled task и границы действия | Научиться задавать одну ограниченную задачу для агента и не смешивать шаги | Ученик формулирует один шаг, одно ожидаемое изменение и один критерий проверки | Source digest + course brief; Instructional inference |
| 5 | Проверка результата и история проекта | Научиться сверять output с ожидаемыми файлами и результатами | Ученик сравнивает результат агента с контрактом и понимает, что означает commit/push | Source digest; Instructional inference |
| 6 | Handoff следующему агенту и безопасный MVP | Научиться передавать артефакты дальше и не раздувать MVP | Ученик объясняет, какие артефакты передаются следующему агенту и какие темы исключены из MVP | Source digest + course brief + methodology references; Instructional inference |

## 5. Lesson order rationale

Lesson 1 comes first because the learner must separate source facts, course brief, and workflow artifacts before any work starts. Later lessons depend on that distinction.

Lesson 2 comes next because the source material repeatedly insists on checking the current state before changing anything. This supports safe execution and prevents random edits.

Lesson 3 follows because the learner must know how the Source Analyst-style reading works before the workflow can be safely executed or verified. It depends on lessons 1 and 2 and prepares the learner for later handoff logic.

Lesson 4 comes after the source-digest reading step because one controlled task only makes sense once the learner understands scope boundaries, one-step thinking, and the expected output shape.

Lesson 5 depends on the previous lessons because verification only works when the learner knows what to compare against. It introduces the idea that output quality is proven by file/state checks, not by assumptions.

Lesson 6 is last because handoff, MVP boundaries, and downstream readiness require the learner to understand the full chain: source -> digest -> brief -> controlled task -> verified output. It also carries forward gaps instead of hiding them.

## 6. Prerequisite chain

| Lesson | Requires before this lesson | Enables after this lesson |
|---:|---|---|
| 1 | Source pack and course brief are present | Distinguish source facts from workflow artifacts |
| 2 | Lesson 1 | Safe pre-change verification habit |
| 3 | Lessons 1-2 | Reliable source analysis and gap detection |
| 4 | Lessons 1-3 | One-step execution with clear boundaries |
| 5 | Lessons 1-4 | Output verification and history tracking |
| 6 | Lessons 1-5 | Upstream handoff awareness and MVP scoping |

## 7. Outcome per lesson

| Lesson | Observable outcome |
|---:|---|
| 1 | Ученик объясняет, какие файлы являются source material, какие относятся к course brief, а какие являются workflow artifacts |
| 2 | Ученик проверяет текущее состояние проекта перед изменением и называет минимум три обязательные проверки |
| 3 | Ученик выделяет из источника основные темы, процедуры, термины, gaps и human decisions |
| 4 | Ученик формулирует один controlled task без смешивания нескольких задач |
| 5 | Ученик сверяет результат агента с ожидаемыми файлами, статусом и историей изменений |
| 6 | Ученик объясняет, какие артефакты переходят к следующему агенту, а какие темы остаются за пределами MVP |

## 8. Practice per lesson

| Lesson | Practice task direction |
|---:|---|
| 1 | Разложить примеры файлов на source material, brief и workflow artifact |
| 2 | Выполнить чек перед изменением: файлы, git status, нужная страница или endpoint |
| 3 | Выписать темы, процедуры, термины, gaps и human decisions из source digest |
| 4 | Составить одно ограниченное задание для агента и определить expected output |
| 5 | Сопоставить output с контрактом и отметить, чего не хватает |
| 6 | Проследить цепочку артефактов от source pack до next-agent handoff и отнести темы к MVP / non-MVP |

## 9. Assessment idea per lesson

| Lesson | Assessment idea |
|---:|---|
| 1 | Сценарий на различение source facts, brief и artifact roles |
| 2 | Сценарий на выбор правильных pre-change checks |
| 3 | Короткая проверка на выявление gaps и human decisions |
| 4 | Сценарий на формулировку одного controlled task |
| 5 | Короткая проверка на сопоставление output с контрактом |
| 6 | Сценарий на определение, что передаётся дальше, а что исключается из MVP |

## 10. Difficulty progression

Курс начинается с простого различения ролей файлов и правил работы, потому что новичок сначала должен понять, что именно является источником фактов, а что является артефактом процесса.

Затем вводится безопасная привычка проверять состояние перед изменением. Это намеренно ставится раньше практического действия, чтобы не поощрять хаотичные правки.

После этого курс переходит к разбору исходников и выделению gaps. Здесь появляется первое многослойное мышление: факты, ограничения, human decisions и instructional inferences.

Только затем вводится controlled task. Это важный переход от анализа к действию, но действие остаётся ограниченным и проверяемым.

Проверка результата вводится после controlled task, чтобы закрепить мысль: правильность подтверждается файлами, статусом и контрактом, а не ощущением, что «вроде получилось».

Финальный шаг специально отложен до конца: handoff следующему агенту, MVP boundaries и явное описание того, что курс не делает. Это снижает риск разрастания курса и помогает передать безопасный, готовый к следующему этапу пакет.

## 11. Topics excluded from MVP

| Excluded topic | Why excluded | Can be added later? |
|---|---|---|
| Полный production deployment | Не нужен для первого контролируемого workflow | Да |
| Продвинутый prompt engineering как отдельная теория | Не требуется для первого результата | Да |
| Подробные уроки по безопасности enterprise-уровня | Выходят за рамки первого курса | Да |
| Полный курс по Git и GitHub | Слишком широкий для MVP | Да |
| Детальный шаблон всех возможных Codex report | Нужен позже, когда появятся дополнительные источники | Да |
| Полноценная библиотека assessment sets | Это задача следующего этапа | Да |
| Написание финального текста уроков | Это не задача Course Architect | Да |

## 12. Source gaps and human decisions carried forward

| Gap or decision | Why it matters | Who must resolve it | Suggested timing |
|---|---|---|---|
| Нет полного примера `AGENTS.md` | Без него трудно стандартизировать стартовые вопросы и агентные контракты | Человек / методический владелец | До расширения курса за пределы MVP |
| Нет шаблонов Codex prompt и хорошего/плохого report | Это влияет на практику, проверку и quality gates | Человек / методист | Перед Lesson Designer |
| Нет примера безопасного deploy key workflow | Это влияет на безопасный серверный блок курса | Человек / технический владелец | До отдельного урока про деплой |
| Нет карты модулей учебного проекта | Сложно уточнить итоговую структуру курса | Человек / course owner | До финализации lesson sequence |
| Не определён точный размер первого курса | Влияет на глубину и объём практики | Человек / product owner | Перед Lesson Designer |
| Не решено, нужен ли отдельный урок про секреты | Влияет на MVP и безопасность | Человек / product owner | До финализации lesson list |

## 13. Risks

| Risk | Mitigation |
|---|---|
| Аудитория слишком общая для безопасного курса | Держать формулировки простыми и ориентироваться на полный новичок / zero level |
| Новичок путает `commit` и `push` | Выделить это в ранних уроках и использовать только наблюдаемые проверки |
| Новичок показывает `localhost` как адрес для пользователя | Явно учить разнице между локальным и публичным адресом |
| В один шаг смешиваются несколько задач | Повторять правило одного шага и не расширять практику раньше времени |
| Секреты, токены или `.env` могут попасть в материал | Держать safety rules в явном виде и использовать STOP при риске |
| Курс начнёт зависеть от неподтверждённых догадок | Отмечать `Instructional inference` и не скрывать gaps |
| Темы MVP разрастутся до production-архитектуры | Явно исключать production и переносить его в later course |

## 14. Readiness for next agent

PASS_CURRICULUM_MAP_READY

## 15. STOP status

PASS_CURRICULUM_MAP_READY
