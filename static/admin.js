(() => {
  const state = window.__CF_STATE__ || {};
  const page = state.page || document.body.dataset.page || "home";
  const agents = state.agents || [];
  const RUNS_DRAFT_KEY = "course_factory_runs_form_draft_v2";
  const warningBox = document.getElementById("page-warning");
  const gitBox = document.getElementById("git-status");

  const home = {
    agentList: document.getElementById("agent-list"),
    fileList: document.getElementById("file-list"),
    editor: document.getElementById("editor"),
    currentAgent: document.getElementById("current-agent"),
    currentFile: document.getElementById("current-file"),
    filePath: document.getElementById("file-path"),
    fileMtime: document.getElementById("file-mtime"),
    filenameInput: document.getElementById("filename"),
    uploadFilenameInput: document.getElementById("upload-filename"),
    uploadInput: document.getElementById("upload-input"),
    messageBox: document.getElementById("message"),
    saveButton: document.getElementById("save-button"),
    uploadButton: document.getElementById("upload-button"),
    refreshButton: document.getElementById("refresh-button"),
  };

  const runs = {
    list: document.getElementById("run-list"),
    agentSelect: document.getElementById("run-agent-select"),
    courseType: document.getElementById("run-course-type"),
    targetAudienceType: document.getElementById("run-target-audience-type"),
    learnerStartingLevel: document.getElementById("run-learner-starting-level"),
    primaryLearningResult: document.getElementById("run-primary-learning-result"),
    finalOutputType: document.getElementById("run-final-output-type"),
    preferredCourseSize: document.getElementById("run-preferred-course-size"),
    courseDepth: document.getElementById("run-course-depth"),
    explanationStyle: document.getElementById("run-explanation-style"),
    practiceFormat: document.getElementById("run-practice-format"),
    assessmentFormat: document.getElementById("run-assessment-format"),
    feedbackMode: document.getElementById("run-feedback-mode"),
    sourceStrictness: document.getElementById("run-source-strictness"),
    domainSensitivity: document.getElementById("run-domain-sensitivity"),
    courseMode: document.getElementById("run-course-mode"),
    sourceFiles: document.getElementById("run-source-files"),
    sourceHint: document.getElementById("run-source-hint"),
    createButton: document.getElementById("create-run-button"),
    createMessage: document.getElementById("run-create-message"),
    detailId: document.getElementById("run-detail-id"),
    detailAgent: document.getElementById("run-detail-agent"),
    detailStatus: document.getElementById("run-detail-status"),
    detailInputMode: document.getElementById("run-detail-input-mode"),
    detailUpstreamRun: document.getElementById("run-detail-upstream-run"),
    detailUpstreamAgent: document.getElementById("run-detail-upstream-agent"),
    detailCourseBriefStatus: document.getElementById("run-detail-course-brief-status"),
    detailGoal: document.getElementById("run-detail-goal"),
    detailAudience: document.getElementById("run-detail-audience"),
    detailSources: document.getElementById("run-detail-sources"),
    nextRunButton: document.getElementById("create-next-course-architect"),
    nextRunHint: document.getElementById("create-next-run-hint"),
    requestView: document.getElementById("run-request-view"),
    statusView: document.getElementById("run-status-view"),
    inputFiles: document.getElementById("run-input-files"),
    upstreamInputFiles: document.getElementById("run-upstream-input-files"),
    outputEmpty: document.getElementById("run-output-empty"),
    outputFiles: document.getElementById("run-output-files"),
    fileLabel: document.getElementById("run-file-label"),
    fileView: document.getElementById("run-file-view"),
  };

  const courseSetupFieldKeys = [
    "courseType",
    "targetAudienceType",
    "learnerStartingLevel",
    "primaryLearningResult",
    "finalOutputType",
    "preferredCourseSize",
    "courseDepth",
    "explanationStyle",
    "practiceFormat",
    "assessmentFormat",
    "feedbackMode",
    "sourceStrictness",
    "domainSensitivity",
    "courseMode",
  ];

  let selectedAgent = null;
  let selectedFile = null;
  let selectedRunId = null;
  let selectedRunFileKey = null;
  let runDraftRestoreApplied = false;

  function setMessage(target, text, tone = "info") {
    if (!target) return;
    target.textContent = text;
    target.dataset.tone = tone;
  }

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function formatJson(value) {
    return JSON.stringify(value, null, 2);
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    const text = await response.text();
    let data = {};
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { error: text };
      }
    }
    if (!response.ok) {
      const error = new Error(data.error || `HTTP ${response.status}`);
      error.response = response;
      error.data = data;
      error.status = response.status;
      throw error;
    }
    return data;
  }

  function describeError(error, fallback) {
    if (error && error.data && typeof error.data === "object") {
      const pieces = [];
      if (error.data.error) pieces.push(error.data.error);
      if (error.data.code) pieces.push(`код: ${error.data.code}`);
      if (pieces.length) return pieces.join(" ");
    }
    if (error && error.message) {
      return error.message;
    }
    if (error && error.status) {
      return `HTTP ${error.status}`;
    }
    return fallback;
  }

  function getRunDraft() {
    try {
      const raw = localStorage.getItem(RUNS_DRAFT_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {};
    }
  }

  function saveRunDraft() {
    if (!runs.agentSelect) return;
    const payload = {
      agent: runs.agentSelect.value || "",
    };
    courseSetupFieldKeys.forEach((fieldKey) => {
      payload[fieldKey] = runs[fieldKey]?.value || "";
    });
    try {
      localStorage.setItem(RUNS_DRAFT_KEY, JSON.stringify(payload));
    } catch {
      // localStorage may be unavailable in hardened browsers; ignore.
    }
  }

  function restoreRunDraft() {
    if (runDraftRestoreApplied || !runs.agentSelect) return;
    const draft = getRunDraft();
    courseSetupFieldKeys.forEach((fieldKey) => {
      if (draft[fieldKey] && runs[fieldKey]) runs[fieldKey].value = draft[fieldKey];
    });
    if (draft.agent && Array.from(runs.agentSelect.options).some((option) => option.value === draft.agent)) {
      runs.agentSelect.value = draft.agent;
    }
    runDraftRestoreApplied = true;
    updateRunSourceHint();
  }

  function updateRunSourceHint() {
    if (!runs.sourceHint) return;
    const names = runs.sourceFiles && runs.sourceFiles.files ? Array.from(runs.sourceFiles.files).map((file) => file.name) : [];
    if (names.length) {
      runs.sourceHint.textContent = `Выбраны файлы: ${names.join(", ")}`;
    } else {
      runs.sourceHint.textContent = "Можно выбрать .md файлы и .zip архивы. После обновления страницы исходные файлы нужно выбрать заново — браузер не разрешает восстанавливать file input автоматически.";
    }
  }

  function syncRunDraftFromUI() {
    saveRunDraft();
    updateRunSourceHint();
  }

  function setCreateButtonBusy(isBusy) {
    if (!runs.createButton) return;
    runs.createButton.disabled = isBusy;
    runs.createButton.textContent = isBusy ? "Создаём заявку..." : "Создать запуск выбранного агента";
  }

  function setNextRunButtonBusy(isBusy) {
    if (!runs.nextRunButton) return;
    runs.nextRunButton.disabled = isBusy;
    runs.nextRunButton.textContent = isBusy ? "Создаём следующий запуск..." : "Создать следующий запуск: Course Architect";
  }

  function renderAgentCards() {
    if (!home.agentList) return;
    home.agentList.innerHTML = "";
    agents.forEach((agent) => {
      const card = document.createElement("div");
      card.className = "agent-card";
      card.dataset.agent = agent.name;
      const fileCount = (agent.files || []).length;
      card.innerHTML = `
        <div class="name">${escapeHtml(agent.title || agent.name)}</div>
        <div class="description">${escapeHtml(agent.description || "")}</div>
        <div class="meta">${escapeHtml(agent.relative_path || "")}</div>
        <div class="meta">${fileCount} markdown files</div>
      `;
      card.addEventListener("click", () => selectAgent(agent.name));
      home.agentList.appendChild(card);
    });
  }

  function renderAgentSelect() {
    if (!runs.agentSelect) return;
    runs.agentSelect.innerHTML = "";
    agents.forEach((agent, index) => {
      const option = document.createElement("option");
      option.value = agent.name;
      option.textContent = `${agent.title || agent.name} — ${agent.description || ""}`;
      runs.agentSelect.appendChild(option);
      if (index === 0) {
        runs.agentSelect.value = agent.name;
      }
    });
  }

  function renderFileList(agentName) {
    if (!home.fileList) return;
    const agent = agents.find((item) => item.name === agentName);
    home.fileList.innerHTML = "";
    if (!agent) {
      home.fileList.innerHTML = '<div class="small">Выберите агента.</div>';
      return;
    }
    (agent.files || []).forEach((file) => {
      const row = document.createElement("div");
      row.className = "file-item";
      row.dataset.file = file.name;
      row.innerHTML = `
        <div>
          <div class="file-name">${escapeHtml(file.name)}</div>
          <div class="small">${escapeHtml(file.relative_path)}</div>
        </div>
        <div class="file-meta">
          <div>${escapeHtml(file.mtime || "")}</div>
          <div>${file.size || 0} bytes</div>
        </div>
      `;
      row.addEventListener("click", () => loadAgentFile(agentName, file.name));
      home.fileList.appendChild(row);
    });
    if (!agent.files || agent.files.length === 0) {
      home.fileList.innerHTML = '<div class="small">В этой папке пока нет markdown-файлов.</div>';
    }
  }

  function highlightSelection() {
    document.querySelectorAll(".agent-card").forEach((node) => {
      node.classList.toggle("active", node.dataset.agent === selectedAgent);
    });
    document.querySelectorAll(".file-item").forEach((node) => {
      node.classList.toggle("active", node.dataset.file === selectedFile);
    });
  }

  async function loadAgentFile(agent, filename) {
    if (!home.editor) return;
    selectedAgent = agent;
    selectedFile = filename;
    home.currentAgent.textContent = agent;
    home.currentFile.textContent = filename;
    home.filenameInput.value = filename;
    home.uploadFilenameInput.value = filename;
    highlightSelection();
    setMessage(home.messageBox, `Загрузка ${agent}/${filename}...`);

    const response = await fetch(`/api/file?agent=${encodeURIComponent(agent)}&filename=${encodeURIComponent(filename)}`);
    const data = await response.json();
    if (!response.ok) {
      setMessage(home.messageBox, data.error || "Не удалось прочитать файл", "error");
      return;
    }
    home.editor.value = data.content || "";
    home.filePath.textContent = data.relative_path || "";
    home.fileMtime.textContent = data.filename ? `Файл: ${data.filename}` : "";
    setMessage(home.messageBox, `Открыт ${data.relative_path}`);
    highlightSelection();
  }

  function selectAgent(agent) {
    selectedAgent = agent;
    const current = agents.find((item) => item.name === agent);
    if (home.currentAgent) home.currentAgent.textContent = agent;
    if (home.currentFile) home.currentFile.textContent = "";
    if (home.filePath) home.filePath.textContent = current ? current.relative_path : "";
    if (home.fileMtime) home.fileMtime.textContent = "";
    renderFileList(agent);
    highlightSelection();
    const firstFile = current && current.files && current.files[0];
    if (firstFile) {
      loadAgentFile(agent, firstFile.name);
    } else if (home.editor) {
      selectedFile = null;
      home.editor.value = "";
      home.filenameInput.value = "";
      home.uploadFilenameInput.value = "";
      setMessage(home.messageBox, `Агент ${agent} выбран, но markdown-файлы не найдены.`);
    }
  }

  async function saveCurrentFile() {
    if (!selectedAgent) {
      setMessage(home.messageBox, "Сначала выберите агента.", "error");
      return;
    }
    const filename = home.filenameInput.value.trim();
    if (!filename) {
      setMessage(home.messageBox, "Укажите имя markdown-файла.", "error");
      return;
    }
    setMessage(home.messageBox, "Сохранение локально...");
    const data = await fetchJson("/api/save", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        agent: selectedAgent,
        filename,
        content: home.editor.value,
      }),
    }).catch((error) => ({ ok: false, error: error.message, data: error.data }));
    if (!data.ok) {
      setMessage(home.messageBox, data.error || "Не удалось сохранить файл", "error");
      return;
    }
    setMessage(home.messageBox, `Локально сохранено: ${data.relative_path}. Commit/push выполняются отдельным Codex-run.`);
    await refreshGit();
    renderStateAfterWrite();
  }

  async function uploadMarkdown() {
    if (!selectedAgent) {
      setMessage(home.messageBox, "Сначала выберите агента.", "error");
      return;
    }
    const file = home.uploadInput.files && home.uploadInput.files[0];
    if (!file && !home.editor.value.trim()) {
      setMessage(home.messageBox, "Выберите markdown-файл или заполните редактор перед загрузкой.", "error");
      return;
    }
    const filename = home.uploadFilenameInput.value.trim() || (file ? file.name : "");
    if (!filename) {
      setMessage(home.messageBox, "Укажите имя markdown-файла.", "error");
      return;
    }

    let content = home.editor.value;
    if (file) {
      content = await file.text();
    }

    setMessage(home.messageBox, "Загрузка markdown локально...");
    const data = await fetchJson("/api/upload", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        agent: selectedAgent,
        filename,
        content,
      }),
    }).catch((error) => ({ ok: false, error: error.message, data: error.data }));
    if (!data.ok) {
      setMessage(home.messageBox, data.error || "Не удалось загрузить файл", "error");
      return;
    }
    setMessage(home.messageBox, `Локально загружено: ${data.relative_path}. Commit/push выполняются отдельным Codex-run.`);
    await refreshGit();
    renderStateAfterWrite();
  }

  async function refreshGit() {
    if (!gitBox) return;
    const response = await fetch("/api/git-status");
    const data = await response.json();
    if (!response.ok) {
      gitBox.textContent = data.error || "Не удалось получить git status";
      return;
    }
    const statusLines = (data.status_short || []).length ? data.status_short.join("\n") : "(clean)";
    gitBox.textContent = [
      `branch: ${data.branch || ""}`,
      `head: ${data.head || ""}`,
      `remote main: ${data.remote_main || "(unavailable)"}`,
      "",
      statusLines,
    ].join("\n");
  }

  function renderStateAfterWrite() {
    const agent = agents.find((item) => item.name === selectedAgent);
    if (!agent) return;
    const fileName = home.filenameInput.value.trim();
    if (!fileName) return;
    const match = (agent.files || []).find((item) => item.name === fileName);
    if (!match) {
      agent.files = agent.files || [];
      agent.files.push({
        name: fileName,
        relative_path: `skills/${selectedAgent}/${fileName}`,
        mtime: new Date().toISOString().slice(0, 19).replace("T", " "),
        size: home.editor.value.length,
      });
    }
    renderFileList(selectedAgent);
    highlightSelection();
  }

  function renderRunFiles(container, runId, kind, files, emptyText) {
    if (!container) return;
    container.innerHTML = "";
    if (!files || !files.length) {
      container.innerHTML = `<div class="small">${escapeHtml(emptyText)}</div>`;
      return;
    }
    files.forEach((filename) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "run-file-button";
      button.dataset.runId = runId;
      button.dataset.kind = kind;
      button.dataset.filename = filename;
      button.dataset.runKey = `${runId}:${kind}:${filename}`;
      button.innerHTML = `
        <div class="title">${escapeHtml(filename)}</div>
        <div class="meta">${escapeHtml(kind)}</div>
      `;
      button.addEventListener("click", () => loadRunFile(runId, kind, filename));
      container.appendChild(button);
    });
  }

  function isEligibleForCourseArchitectRun(detail) {
    const status = detail?.status_json || {};
    const outputFiles = detail?.output_files || [];
    return status.agent === "source-analyst" && status.status === "completed_success" && outputFiles.includes("source_digest.md");
  }

  async function createNextCourseArchitectRun() {
    if (!selectedRunId || !runs.nextRunButton) return;
    setNextRunButtonBusy(true);
    setMessage(runs.createMessage, "Создаём следующий запуск из upstream artifacts...");
    try {
      const response = await fetch("/api/runs/next", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          upstream_run_id: selectedRunId,
          target_agent: "course-architect",
        }),
      });
      const text = await response.text();
      let data = {};
      if (text) {
        try {
          data = JSON.parse(text);
        } catch {
          data = { error: text };
        }
      }
      if (!response.ok || !data.ok) {
        const details = describeError({ message: data.error || `HTTP ${response.status}`, data, status: response.status }, "неизвестная ошибка");
        setMessage(runs.createMessage, `Не удалось создать следующий запуск: ${details}`, "error");
        return;
      }
      setMessage(
        runs.createMessage,
        `Создан следующий запуск ${data.run_id} из upstream artifacts. Новый run pending_codex_execution, архив повторно загружать не нужно.`
      );
      await refreshRuns(true);
      await loadRunDetail(data.run_id, { silent: true, skipFirstOutput: true });
    } finally {
      setNextRunButtonBusy(false);
    }
  }

  async function loadRunFile(runId, kind, filename) {
    if (!runs.fileView || !runs.fileLabel) return;
    selectedRunId = runId;
    selectedRunFileKey = `${runId}:${kind}:${filename}`;
    const label = `${kind}/${filename}`;
    runs.fileLabel.textContent = label;
    runs.fileView.value = "Загрузка...";
    const data = await fetchJson(`/api/runs/file?run_id=${encodeURIComponent(runId)}&kind=${encodeURIComponent(kind)}&filename=${encodeURIComponent(filename)}`)
      .catch((error) => ({ ok: false, error: error.message, data: error.data }));
    if (!data.ok) {
      runs.fileView.value = `Не удалось прочитать файл: ${describeError(data, "неизвестная ошибка")}`;
      updateRunSelection();
      return;
    }
    runs.fileView.value = data.content || "";
    updateRunSelection();
  }

  function updateRunSelection() {
    document.querySelectorAll(".run-card").forEach((node) => {
      node.classList.toggle("active", node.dataset.runId === selectedRunId);
    });
    document.querySelectorAll(".run-file-button").forEach((node) => {
      node.classList.toggle("active", node.dataset.runKey === selectedRunFileKey);
    });
  }

  function renderRunDetail(detail) {
    if (!runs.detailId) return;
    selectedRunId = detail.run_id || null;
    selectedRunFileKey = null;
    runs.detailId.textContent = detail.run_id || "-";
    runs.detailAgent.textContent = detail.status_json?.agent || "-";
    runs.detailStatus.textContent = detail.status_json?.status || "-";
    if (runs.detailInputMode) runs.detailInputMode.textContent = detail.status_json?.input_mode || "-";
    if (runs.detailUpstreamRun) runs.detailUpstreamRun.textContent = detail.status_json?.upstream_run_id || "-";
    if (runs.detailUpstreamAgent) runs.detailUpstreamAgent.textContent = detail.status_json?.upstream_agent || "-";
    if (runs.detailCourseBriefStatus) runs.detailCourseBriefStatus.textContent = detail.status_json?.course_brief_status || "-";
    runs.detailGoal.textContent = detail.status_json?.goal || "-";
    runs.detailAudience.textContent = detail.status_json?.target_audience || "-";
    runs.detailSources.textContent = (detail.status_json?.source_files || []).join(", ") || "-";
    runs.requestView.value = detail.run_request_md || "";
    runs.statusView.value = formatJson(detail.status_json || {});
    renderRunFiles(runs.inputFiles, detail.run_id, "input", detail.input_files || [], "Входных файлов пока нет.");
    renderRunFiles(runs.upstreamInputFiles, detail.run_id, "input", detail.upstream_input_files || [], "Унаследованных upstream artifacts пока нет.");
    renderRunFiles(runs.outputFiles, detail.run_id, "output", detail.output_files || [], "Результата ещё нет. Выполните отдельный Codex-run для этой заявки.");
    if (runs.outputEmpty) {
      runs.outputEmpty.style.display = (detail.output_files || []).length ? "none" : "block";
    }
    if (runs.nextRunButton) {
      const eligible = isEligibleForCourseArchitectRun(detail);
      runs.nextRunButton.style.display = eligible ? "inline-flex" : "none";
      runs.nextRunButton.disabled = false;
    }
    if (runs.nextRunHint) {
      runs.nextRunHint.textContent = isEligibleForCourseArchitectRun(detail)
        ? "Этот запуск использует upstream artifacts из completed Source Analyst run. Новый архив загружать не нужно."
        : "Для этого действия нужен completed Source Analyst run со `source_digest.md`.";
    }
    if (runs.fileLabel) {
      runs.fileLabel.textContent = "-";
    }
    if (runs.fileView) {
      runs.fileView.value = (detail.output_files || []).length ? "Выберите output-файл для просмотра." : "Результата ещё нет. Выполните отдельный Codex-run для этой заявки.";
    }
    updateRunSelection();
  }

  async function loadRunDetail(runId, options = {}) {
    const data = await fetchJson(`/api/runs/detail?run_id=${encodeURIComponent(runId)}`).catch((error) => ({ ok: false, error: error.message, data: error.data, status: error.status }));
    if (!data.ok) {
      const message = `Не удалось прочитать запуск: ${describeError(data, "неизвестная ошибка")}`;
      if (!options.silent) {
        setMessage(runs.createMessage, message, "error");
      }
      return { ok: false, error: message };
    }
    renderRunDetail(data);
    if (!options.skipFirstOutput && (data.output_files || []).length) {
      const first = data.output_files[0];
      await loadRunFile(runId, "output", first);
    }
    return { ok: true };
  }

  function renderRunsList(items) {
    if (!runs.list) return;
    runs.list.innerHTML = "";
    if (!items.length) {
      runs.list.innerHTML = '<div class="small">Пока нет запусков. Создайте первую заявку.</div>';
      return;
    }
    items.forEach((item) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "run-card";
      card.dataset.runId = item.run_id;
      card.innerHTML = `
        <div class="title">${escapeHtml(item.run_id || "")}</div>
        <div class="meta">${escapeHtml(item.agent || "")}</div>
        <div class="meta">${escapeHtml(item.status || "")}</div>
        <div class="meta">${escapeHtml(item.created_at_utc || "")}</div>
      `;
      card.addEventListener("click", () => loadRunDetail(item.run_id));
      runs.list.appendChild(card);
    });
    updateRunSelection();
  }

  async function refreshRuns(keepSelection = true) {
    if (!runs.list) return;
    const data = await fetchJson("/api/runs").catch((error) => ({ ok: false, error: error.message, data: error.data }));
    if (!data.ok) {
      runs.list.innerHTML = `<div class="small">Не удалось получить список запусков: ${escapeHtml(describeError(data, "неизвестная ошибка"))}</div>`;
      return { ok: false, error: describeError(data, "неизвестная ошибка") };
    }
    renderRunsList(data.runs || []);
    if (!keepSelection) {
      selectedRunId = null;
    }
    if (!selectedRunId && (data.runs || []).length) {
      await loadRunDetail(data.runs[0].run_id);
    } else if (selectedRunId) {
      const exists = (data.runs || []).some((item) => item.run_id === selectedRunId);
      if (!exists && (data.runs || []).length) {
        await loadRunDetail(data.runs[0].run_id);
      }
    }
    return { ok: true };
  }

  async function createRun() {
    if (!runs.agentSelect) return;
    const agent = runs.agentSelect.value.trim();
    const files = runs.sourceFiles.files;
    if (!agent) {
      setMessage(runs.createMessage, "Сначала выберите агента.", "error");
      return;
    }
    if (!files || !files.length) {
      setMessage(runs.createMessage, "Добавьте хотя бы один markdown-файл или ZIP-архив.", "error");
      return;
    }

    const form = new FormData();
    form.append("agent", agent);
    courseSetupFieldKeys.forEach((fieldKey) => {
      if (runs[fieldKey]) form.append(fieldKey.replace(/[A-Z]/g, (match) => `_${match.toLowerCase()}`), runs[fieldKey].value || "");
    });
    Array.from(files).forEach((file) => {
      form.append("files[]", file, file.name);
    });

    setCreateButtonBusy(true);
    setMessage(runs.createMessage, "Создаём заявку...");
    try {
      const response = await fetch("/api/runs/create", {
        method: "POST",
        body: form,
      });
      const text = await response.text();
      let data = {};
      if (text) {
        try {
          data = JSON.parse(text);
        } catch {
          data = { error: text };
        }
      }
      if (!response.ok || !data.ok) {
        const details = describeError({ message: data.error || `HTTP ${response.status}`, data, status: response.status }, "неизвестная ошибка");
        setMessage(runs.createMessage, `Не удалось создать заявку: ${details}`, "error");
        return;
      }

      saveRunDraft();
      setMessage(runs.createMessage, `Создан запуск ${data.run_id} со статусом ${data.status}.`);
      const listResult = await refreshRuns(true);
      if (!listResult || listResult.ok === false) {
        setMessage(runs.createMessage, `Заявка создана, но список запусков не обновился: ${listResult?.error || "неизвестная ошибка"}`, "error");
      }
      const detailResult = await loadRunDetail(data.run_id, { silent: true, skipFirstOutput: false });
      if (!detailResult || detailResult.ok === false) {
        const details = detailResult?.error || "неизвестная ошибка";
        setMessage(runs.createMessage, `Заявка создана, но не удалось открыть детали. Run ID: ${data.run_id}. Обновите список запусков. ${details}`, "error");
      } else {
        setMessage(runs.createMessage, `Создан запуск ${data.run_id} со статусом ${data.status}.`);
      }
      updateRunSourceHint();
    } finally {
      setCreateButtonBusy(false);
      saveRunDraft();
    }
  }

  function initHome() {
    renderAgentCards();
    if (home.saveButton) home.saveButton.addEventListener("click", saveCurrentFile);
    if (home.uploadButton) home.uploadButton.addEventListener("click", uploadMarkdown);
    if (home.refreshButton) home.refreshButton.addEventListener("click", refreshGit);
    if (home.uploadInput) {
      home.uploadInput.addEventListener("change", () => {
        if (home.uploadInput.files && home.uploadInput.files[0]) {
          home.uploadFilenameInput.value = home.uploadInput.files[0].name;
        }
      });
    }
    if (agents.length) {
      selectAgent(agents[0].name);
    } else {
      setMessage(home.messageBox, "Нет доступных agent-директорий.", "error");
    }
    refreshGit();
  }

  function initRuns() {
    renderAgentSelect();
    restoreRunDraft();
    if (runs.createButton) runs.createButton.addEventListener("click", createRun);
    if (runs.nextRunButton) runs.nextRunButton.addEventListener("click", createNextCourseArchitectRun);
    if (runs.agentSelect) {
      runs.agentSelect.addEventListener("change", syncRunDraftFromUI);
    }
    courseSetupFieldKeys.forEach((fieldKey) => {
      const field = runs[fieldKey];
      if (field) field.addEventListener("change", syncRunDraftFromUI);
    });
    if (runs.sourceFiles) {
      runs.sourceFiles.addEventListener("change", () => {
        updateRunSourceHint();
        setMessage(runs.createMessage, "Добавлены файлы для новой заявки.");
      });
    }
    refreshRuns().catch(() => {});
    updateRunSourceHint();
  }

  if (warningBox && state.warning) {
    warningBox.textContent = state.warning;
  }

  if (page === "home") {
    initHome();
  } else if (page === "runs") {
    initRuns();
  }

  if (gitBox) {
    refreshGit().catch(() => {});
  }

  window.addEventListener("focus", () => {
    refreshGit().catch(() => {});
    if (page === "runs") {
      refreshRuns(true).catch(() => {});
    }
  });
})();
