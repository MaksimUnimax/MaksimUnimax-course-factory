(() => {
  const state = window.__CF_STATE__ || {};
  const page = state.page || document.body.dataset.page || "home";
  const agents = state.agents || [];
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
    goal: document.getElementById("run-goal"),
    targetAudience: document.getElementById("run-target-audience"),
    sourceFiles: document.getElementById("run-source-files"),
    createButton: document.getElementById("create-run-button"),
    createMessage: document.getElementById("run-create-message"),
    detailId: document.getElementById("run-detail-id"),
    detailAgent: document.getElementById("run-detail-agent"),
    detailStatus: document.getElementById("run-detail-status"),
    detailGoal: document.getElementById("run-detail-goal"),
    detailAudience: document.getElementById("run-detail-audience"),
    detailSources: document.getElementById("run-detail-sources"),
    requestView: document.getElementById("run-request-view"),
    statusView: document.getElementById("run-status-view"),
    inputFiles: document.getElementById("run-input-files"),
    outputEmpty: document.getElementById("run-output-empty"),
    outputFiles: document.getElementById("run-output-files"),
    fileLabel: document.getElementById("run-file-label"),
    fileView: document.getElementById("run-file-view"),
  };

  let selectedAgent = null;
  let selectedFile = null;
  let selectedRunId = null;
  let selectedRunFileKey = null;

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
    const data = await response.json();
    if (!response.ok) {
      const error = new Error(data.error || `HTTP ${response.status}`);
      error.response = response;
      error.data = data;
      throw error;
    }
    return data;
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
      runs.fileView.value = data.error || "Не удалось прочитать файл";
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
    runs.detailGoal.textContent = detail.status_json?.goal || "-";
    runs.detailAudience.textContent = detail.status_json?.target_audience || "-";
    runs.detailSources.textContent = (detail.status_json?.source_files || []).join(", ") || "-";
    runs.requestView.value = detail.run_request_md || "";
    runs.statusView.value = formatJson(detail.status_json || {});
    renderRunFiles(runs.inputFiles, detail.run_id, "input", detail.input_files || [], "Входных файлов пока нет.");
    renderRunFiles(runs.outputFiles, detail.run_id, "output", detail.output_files || [], "Результата ещё нет. Выполните отдельный Codex-run для этой заявки.");
    if (runs.outputEmpty) {
      runs.outputEmpty.style.display = (detail.output_files || []).length ? "none" : "block";
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
    const data = await fetchJson(`/api/runs/detail?run_id=${encodeURIComponent(runId)}`).catch((error) => ({ ok: false, error: error.message, data: error.data }));
    if (!data.ok) {
      setMessage(runs.createMessage, data.error || "Не удалось прочитать запуск", "error");
      return;
    }
    renderRunDetail(data);
    if (!options.skipFirstOutput && (data.output_files || []).length) {
      const first = data.output_files[0];
      await loadRunFile(runId, "output", first);
    }
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
      runs.list.innerHTML = `<div class="small">${escapeHtml(data.error || "Не удалось получить список запусков")}</div>`;
      return;
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
  }

  async function createRun() {
    if (!runs.agentSelect) return;
    const agent = runs.agentSelect.value.trim();
    const goal = runs.goal.value.trim();
    const targetAudience = runs.targetAudience.value.trim();
    const files = runs.sourceFiles.files;
    if (!agent) {
      setMessage(runs.createMessage, "Сначала выберите агента.", "error");
      return;
    }
    if (!goal) {
      setMessage(runs.createMessage, "Укажите цель запуска.", "error");
      return;
    }
    if (!targetAudience) {
      setMessage(runs.createMessage, "Укажите целевую аудиторию.", "error");
      return;
    }
    if (!files || !files.length) {
      setMessage(runs.createMessage, "Добавьте хотя бы один markdown-файл.", "error");
      return;
    }

    const form = new FormData();
    form.append("agent", agent);
    form.append("goal", goal);
    form.append("target_audience", targetAudience);
    Array.from(files).forEach((file) => {
      form.append("files[]", file, file.name);
    });

    setMessage(runs.createMessage, "Создание заявки на запуск...");
    const response = await fetch("/api/runs/create", {
      method: "POST",
      body: form,
    });
    const data = await response.json();
    if (!response.ok) {
      setMessage(runs.createMessage, data.error || "Не удалось создать заявку", "error");
      return;
    }
    setMessage(runs.createMessage, `Создан запуск ${data.run_id} со статусом ${data.status}.`);
    runs.goal.value = "";
    runs.targetAudience.value = "";
    runs.sourceFiles.value = "";
    await refreshRuns(false);
    await loadRunDetail(data.run_id);
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
    if (runs.createButton) runs.createButton.addEventListener("click", createRun);
    if (runs.sourceFiles) {
      runs.sourceFiles.addEventListener("change", () => {
        if (!runs.goal.value.trim()) {
          setMessage(runs.createMessage, "Добавлены файлы для новой заявки.");
        }
      });
    }
    refreshRuns().catch(() => {});
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
