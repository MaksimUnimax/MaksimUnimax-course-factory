(() => {
  const state = window.__CF_STATE__ || {};
  const agents = state.agents || [];
  const gitBox = document.getElementById("git-status");
  const agentList = document.getElementById("agent-list");
  const fileList = document.getElementById("file-list");
  const editor = document.getElementById("editor");
  const currentAgent = document.getElementById("current-agent");
  const currentFile = document.getElementById("current-file");
  const filePath = document.getElementById("file-path");
  const fileMtime = document.getElementById("file-mtime");
  const filenameInput = document.getElementById("filename");
  const uploadFilenameInput = document.getElementById("upload-filename");
  const uploadInput = document.getElementById("upload-input");
  const messageBox = document.getElementById("message");
  const saveButton = document.getElementById("save-button");
  const uploadButton = document.getElementById("upload-button");
  const refreshButton = document.getElementById("refresh-button");

  let selectedAgent = null;
  let selectedFile = null;

  function setMessage(text, tone = "info") {
    messageBox.textContent = text;
    messageBox.dataset.tone = tone;
  }

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function renderAgentCards() {
    agentList.innerHTML = "";
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
      agentList.appendChild(card);
    });
  }

  function renderFileList(agentName) {
    const agent = agents.find((item) => item.name === agentName);
    fileList.innerHTML = "";
    if (!agent) {
      fileList.innerHTML = '<div class="small">Выберите агента.</div>';
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
      row.addEventListener("click", () => loadFile(agentName, file.name));
      fileList.appendChild(row);
    });
    if (!agent.files || agent.files.length === 0) {
      fileList.innerHTML = '<div class="small">В этой папке пока нет markdown-файлов.</div>';
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

  async function loadFile(agent, filename) {
    selectedAgent = agent;
    selectedFile = filename;
    currentAgent.textContent = agent;
    currentFile.textContent = filename;
    filenameInput.value = filename;
    uploadFilenameInput.value = filename;
    highlightSelection();
    setMessage(`Загрузка ${agent}/${filename}...`);

    const response = await fetch(`/api/file?agent=${encodeURIComponent(agent)}&filename=${encodeURIComponent(filename)}`);
    const data = await response.json();
    if (!response.ok) {
      setMessage(data.error || "Не удалось прочитать файл", "error");
      return;
    }
    editor.value = data.content || "";
    filePath.textContent = data.relative_path || "";
    fileMtime.textContent = data.filename ? `Файл: ${data.filename}` : "";
    setMessage(`Открыт ${data.relative_path}`);
    highlightSelection();
  }

  function selectAgent(agent) {
    selectedAgent = agent;
    const current = agents.find((item) => item.name === agent);
    currentAgent.textContent = agent;
    currentFile.textContent = "";
    filePath.textContent = current ? current.relative_path : "";
    fileMtime.textContent = "";
    renderFileList(agent);
    highlightSelection();
    const firstFile = current && current.files && current.files[0];
    if (firstFile) {
      loadFile(agent, firstFile.name);
    } else {
      selectedFile = null;
      editor.value = "";
      filenameInput.value = "";
      uploadFilenameInput.value = "";
      setMessage(`Агент ${agent} выбран, но markdown-файлы не найдены.`);
    }
  }

  async function saveCurrentFile() {
    if (!selectedAgent) {
      setMessage("Сначала выберите агента.", "error");
      return;
    }
    const filename = filenameInput.value.trim();
    if (!filename) {
      setMessage("Укажите имя markdown-файла.", "error");
      return;
    }
    setMessage("Сохранение локально...");
    const response = await fetch("/api/save", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        agent: selectedAgent,
        filename,
        content: editor.value,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      setMessage(data.error || "Не удалось сохранить файл", "error");
      return;
    }
    setMessage(`Локально сохранено: ${data.relative_path}. Commit/push выполняются отдельным Codex-run.`);
    refreshGit();
    renderStateAfterWrite();
  }

  async function uploadMarkdown() {
    if (!selectedAgent) {
      setMessage("Сначала выберите агента.", "error");
      return;
    }
    const file = uploadInput.files && uploadInput.files[0];
    if (!file && !editor.value.trim()) {
      setMessage("Выберите markdown-файл или заполните редактор перед загрузкой.", "error");
      return;
    }
    const filename = uploadFilenameInput.value.trim() || (file ? file.name : "");
    if (!filename) {
      setMessage("Укажите имя markdown-файла.", "error");
      return;
    }

    let content = editor.value;
    if (file) {
      content = await file.text();
    }

    setMessage("Загрузка markdown локально...");
    const response = await fetch("/api/upload", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        agent: selectedAgent,
        filename,
        content,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      setMessage(data.error || "Не удалось загрузить файл", "error");
      return;
    }
    setMessage(`Локально загружено: ${data.relative_path}. Commit/push выполняются отдельным Codex-run.`);
    refreshGit();
    renderStateAfterWrite();
  }

  async function refreshGit() {
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
    const fileName = filenameInput.value.trim();
    if (!fileName) return;
    const match = (agent.files || []).find((item) => item.name === fileName);
    if (!match) {
      agent.files = agent.files || [];
      agent.files.push({
        name: fileName,
        relative_path: `skills/${selectedAgent}/${fileName}`,
        mtime: new Date().toISOString().slice(0, 19).replace("T", " "),
        size: editor.value.length,
      });
    }
    renderFileList(selectedAgent);
    highlightSelection();
  }

  saveButton.addEventListener("click", saveCurrentFile);
  uploadButton.addEventListener("click", uploadMarkdown);
  refreshButton.addEventListener("click", refreshGit);
  uploadInput.addEventListener("change", () => {
    if (uploadInput.files && uploadInput.files[0]) {
      uploadFilenameInput.value = uploadInput.files[0].name;
    }
  });

  renderAgentCards();
  refreshGit();
  if (agents.length) {
    selectAgent(agents[0].name);
  } else {
    setMessage("Нет доступных agent-директорий.", "error");
  }

  window.addEventListener("focus", refreshGit);
})();
