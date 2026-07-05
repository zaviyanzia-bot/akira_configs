// ==========================================================================
// NEXUS AUTOMATOR — DYNAMIC INTERACTION & SIMULATOR LOGIC
// ==========================================================================

// --- DEFAULT SEED PROMPTS ---
const DEFAULT_PROMPTS = [
  "Rusty Omega-Style Seamaster Watch Full Restoration | Object Type: Stainless steel dive watch | Before Condition: Thick orange rust on bezel, cracked crystal, frozen crown, green corrosion on bracelet, dial stained with mud | Restoration Process: Push bracelet pins, open caseback, ultrasonic clean dial, rust remover dip for case, new crystal press fit, replace crown gaskets, polish steel, install new quartz movement | Final After Look: Mirror polish steel case, deep black dial, clean lume markers, new sapphire crystal, brushed bracelet | Final Text Scene: Crown winds, second hand sweeps, bezel clicks once around | Why It Can Go Viral: Luxury dive watch + dead-to-working sweep - high Tier-1 watch community retention + ASMR ticking",
  "Parent POV, raw iPhone 17 Pro Max back camera, vertical 9:16, pediatric eye clinic in Dallas, Texas, daytime festive lighting. 0-2s: 6-month-old baby in mother's arms on crinkling exam paper, squinting confused at blurred shapes, mom whispering 'hi baby, mommy's here' nervously. Handheld shake, exposure flicker. 2-5s: Blurred pediatric nurse hands gently slide tiny prescription glasses onto baby's face, soft click, baby freezes, breath catches. 5-8s: Blurred pediatric nurse hands adjust frame.",
  "Father POV, raw iPhone 17 Pro Max back camera, vertical 9:16, playground setup, kids playing slide, cinematic warm colors, bokeh lens flare.",
  "Mother POV, raw iPhone 17 Pro Max back camera, vertical 9:16, baking class with kids, flour dust in air, slow motion hand whisking cake batter.",
  "Parent POV, raw iPhone 17 Pro Max back camera, vertical 9:16, living room, toddlers stacking wooden blocks, building collapse, laughing out loud.",
  "Father POV, raw iPhone 17 Pro Max back camera, vertical 9:16, backyard lawn, teaching boy to cycle without training wheels, dynamic camera pan.",
  "Mother POV, raw iPhone 17 Pro Max back camera, vertical 9:16, kitchen, toddler tasting lemon for the first time, funny facial expression.",
  "Parent POV, raw iPhone 17 Pro Max back camera, vertical 9:16, doctor office, toddler receiving sticker, smiling happily.",
  "Father POV, raw iPhone 17 Pro Max back camera, vertical 9:16, park picnic, child running after bubbles, grass lawn.",
  "Mother POV, raw iPhone 17 Pro Max back camera, vertical 9:16, beach sunset, child building sandcastle, golden hour backlighting.",
  "Parent POV, raw iPhone 17 Pro Max back camera, vertical 9:16, baby bath time, splashing bubbles, rubber duck toy, warm cozy bathroom."
];

// --- APP STATE ---
const state = {
  prompts: [...DEFAULT_PROMPTS],
  isGenerating: true, // Started by default to match screenshot state!
  concurrentConnections: 1,
  batchSize: 30,
  logSequence: 76,    // Starts at log index 076 from screenshot
  stats: {
    total: 11,
    queued: 4,
    generating: 6,
    done: 1,
    failed: 0,
    skipped: 0
  },
  // Initialize queue exactly matching screenshot
  queue: [
    { id: 1, prompt: DEFAULT_PROMPTS[0], status: 'GENERATING', action: 'Processing...', progressStep: 3 },
    { id: 2, prompt: DEFAULT_PROMPTS[1], status: 'DOWNLOADING', action: 'Cleaning watermark...', progressStep: 2 },
    { id: 3, prompt: DEFAULT_PROMPTS[2], status: 'GENERATING', action: 'Processing...', progressStep: 1 },
    { id: 4, prompt: DEFAULT_PROMPTS[3], status: 'GENERATING', action: 'Processing...', progressStep: 0 },
    { id: 5, prompt: DEFAULT_PROMPTS[4], status: 'GENERATING', action: 'Processing...', progressStep: 0 },
    { id: 6, prompt: DEFAULT_PROMPTS[5], status: 'GENERATING', action: 'Processing...', progressStep: 0 },
    { id: 7, prompt: DEFAULT_PROMPTS[6], status: 'GENERATING', action: 'Processing...', progressStep: 0 },
    { id: 8, prompt: DEFAULT_PROMPTS[7], status: 'QUEUED', action: 'Waiting in queue...', progressStep: 0 },
    { id: 9, prompt: DEFAULT_PROMPTS[8], status: 'QUEUED', action: 'Waiting in queue...', progressStep: 0 },
    { id: 10, prompt: DEFAULT_PROMPTS[9], status: 'QUEUED', action: 'Waiting in queue...', progressStep: 0 },
    { id: 11, prompt: DEFAULT_PROMPTS[10], status: 'QUEUED', action: 'Waiting in queue...', progressStep: 0 }
  ],
  logs: [
    // Pre-populating identical logs to match screenshot
    { index: '070', time: '16:55:37', type: 'SUCCESS', message: 'Row 2: Video is ready for download.' },
    { index: '071', time: '16:55:38', type: 'INFO', message: 'Row 3: Processing video request (attempt 13/250)...' },
    { index: '072', time: '16:55:38', type: 'INFO', message: 'Row 1: Processing video request (attempt 28/250)...' },
    { index: '073', time: '16:55:38', type: 'INFO', message: 'Row 6: Processing video request (attempt 10/250)...' },
    { index: '074', time: '16:55:42', type: 'INFO', message: 'Row 7: Processing video request (attempt 7/250)...' },
    { index: '075', time: '16:55:45', type: 'INFO', message: 'Row 2: [+] Removing watermark...' },
    { index: '076', time: '16:55:45', type: 'INFO', message: 'Row 2: [+] Watermark detected at: x=586, y=1231, w=128, h=48' }
  ],
  simulationTimer: null,
  activeConnectionsCount: 6
};

// --- DOM ELEMENTS ---
const elements = {
  promptsTextarea: document.getElementById('prompts-input'),
  promptsCountBadge: document.getElementById('prompts-count-badge'),
  btnStartStop: document.getElementById('btn-start-stop'),
  btnImportTxt: document.getElementById('btn-import-txt'),
  btnImportCsv: document.getElementById('btn-import-csv'),
  btnClearPrompts: document.getElementById('btn-clear-prompts'),
  btnAddQueue: document.getElementById('btn-add-queue'),
  fileInputTxt: document.getElementById('file-input-txt'),
  fileInputCsv: document.getElementById('file-input-csv'),
  
  // Settings
  settingModel: document.getElementById('setting-model'),
  settingDuration: document.getElementById('setting-duration'),
  settingRatio: document.getElementById('setting-ratio'),
  settingBatch: document.getElementById('setting-batch'),
  settingConcurrent: document.getElementById('setting-concurrent'),

  // Stats
  statTotal: document.getElementById('stat-total-val'),
  statQueued: document.getElementById('stat-queued-val'),
  statGenerating: document.getElementById('stat-generating-val'),
  statDone: document.getElementById('stat-done-val'),
  statFailed: document.getElementById('stat-failed-val'),
  statSkipped: document.getElementById('stat-skipped-val'),
  progressText: document.getElementById('progress-text'),
  progressBarFill: document.getElementById('progress-bar-fill'),

  // Table
  queueTableBody: document.getElementById('queue-table-body'),
  
  // Console
  consoleTerminal: document.getElementById('console-terminal'),
  consoleSearch: document.getElementById('console-search'),
  btnClearLogs: document.getElementById('btn-clear-logs'),
  btnCopyLogs: document.getElementById('btn-copy-logs'),
  btnDownloadLogs: document.getElementById('btn-download-logs'),
  
  // Top nav action triggers
  btnRefresh: document.getElementById('btn-refresh'),
  btnSupport: document.getElementById('btn-support'),
  btnTheme: document.getElementById('btn-theme'),
  btnNotification: document.getElementById('btn-notification')
};

// ==========================================================================
// INITIALIZATION
// ==========================================================================
window.addEventListener('DOMContentLoaded', () => {
  // Populate prompts workspace
  elements.promptsTextarea.value = state.prompts.join('\n');
  elements.promptsCountBadge.textContent = `${state.prompts.length} PROMPTS`;

  // Setup Event Listeners
  elements.promptsTextarea.addEventListener('input', updatePromptCount);
  elements.btnStartStop.addEventListener('click', toggleGeneration);
  
  // Prompts operations
  elements.btnImportTxt.addEventListener('click', () => elements.fileInputTxt.click());
  elements.btnImportCsv.addEventListener('click', () => elements.fileInputCsv.click());
  elements.btnAddQueue.addEventListener('click', addPromptsToQueue);
  elements.btnClearPrompts.addEventListener('click', clearPrompts);
  
  elements.fileInputTxt.addEventListener('change', handleTxtImport);
  elements.fileInputCsv.addEventListener('change', handleCsvImport);

  // Console operations
  elements.btnClearLogs.addEventListener('click', clearConsole);
  elements.btnCopyLogs.addEventListener('click', copyConsoleLogs);
  elements.btnDownloadLogs.addEventListener('click', downloadConsoleLogs);
  elements.consoleSearch.addEventListener('input', filterConsoleLogs);

  // Top Nav Actions
  elements.btnRefresh.addEventListener('click', refreshDashboard);
  elements.btnSupport.addEventListener('click', () => showToast('💬 Redirecting to WhatsApp Support...', 'info'));
  elements.btnTheme.addEventListener('click', toggleTheme);
  elements.btnNotification.addEventListener('click', () => showToast('🔔 No new notifications.', 'info'));

  // Autoscroll terminal on load
  elements.consoleTerminal.scrollTop = elements.consoleTerminal.scrollHeight;

  // Since we start in active state (STOP GENERATION mode), launch the timer loop
  renderQueueTable();
  state.simulationTimer = setInterval(runSimulationStep, 2500);
});

// ==========================================================================
// PROMPT HANDLERS
// ==========================================================================
function updatePromptCount() {
  const text = elements.promptsTextarea.value.trim();
  if (text === '') {
    state.prompts = [];
  } else {
    state.prompts = text.split('\n').filter(line => line.trim() !== '');
  }
  elements.promptsCountBadge.textContent = `${state.prompts.length} PROMPTS`;
}

function clearPrompts() {
  elements.promptsTextarea.value = '';
  updatePromptCount();
  showToast('🗑️ Prompts cleared.', 'info');
}

function handleTxtImport(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(evt) {
    const content = evt.target.result;
    elements.promptsTextarea.value = content;
    updatePromptCount();
    showToast(`📄 Imported prompts from ${file.name}`, 'success');
  };
  reader.readAsText(file);
}

function handleCsvImport(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(evt) {
    const content = evt.target.result;
    const lines = content.split(/\r?\n/)
      .map(line => line.replace(/^["']|["']$/g, '').trim())
      .filter(line => line !== '');
      
    elements.promptsTextarea.value = lines.join('\n');
    updatePromptCount();
    showToast(`📊 Imported CSV prompts from ${file.name}`, 'success');
  };
  reader.readAsText(file);
}

// ==========================================================================
// TOAST & CONSOLE LOGS
// ==========================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slide-in 0.25s reverse forwards';
    setTimeout(() => {
      container.removeChild(toast);
    }, 250);
  }, 3000);
}

function logToConsole(type, message) {
  state.logSequence++;
  const paddedSeq = String(state.logSequence).padStart(3, '0');
  const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
  const line = document.createElement('div');
  
  let typeClass = 'info-line';
  if (type === 'SUCCESS') typeClass = 'success-line';
  else if (type === 'SYSTEM') typeClass = 'system-line';
  else if (type === 'WARNING') typeClass = 'warning-line';
  else if (type === 'ERROR') typeClass = 'error-line';
  
  line.className = `log-line ${typeClass}`;
  
  if (type === 'SYSTEM') {
    line.innerHTML = `${paddedSeq} [SYSTEM] ${message}`;
  } else {
    line.innerHTML = `${paddedSeq} [${time}] <span class="log-type">${type}</span> ${message}`;
  }
  
  elements.consoleTerminal.appendChild(line);
  elements.consoleTerminal.scrollTop = elements.consoleTerminal.scrollHeight;
  
  state.logs.push({ index: paddedSeq, time, type, message });
}

function clearConsole() {
  elements.consoleTerminal.innerHTML = '';
  state.logs = [];
  logToConsole('SYSTEM', 'Log history cleared.');
}

function copyConsoleLogs() {
  const text = state.logs.map(l => `${l.index} [${l.time}] ${l.type} - ${l.message}`).join('\n');
  navigator.clipboard.writeText(text)
    .then(() => showToast('📋 Logs copied to clipboard.', 'success'))
    .catch(() => showToast('❌ Failed to copy logs.', 'error'));
}

function downloadConsoleLogs() {
  if (state.logs.length === 0) {
    showToast('⚠️ No logs to export.', 'error');
    return;
  }
  const text = state.logs.map(l => `${l.index} [${l.time}] ${l.type} - ${l.message}`).join('\n');
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `nexus_logs_${new Date().toISOString().split('T')[0]}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('💾 Log file downloaded.', 'success');
}

function filterConsoleLogs() {
  const query = elements.consoleSearch.value.toLowerCase().trim();
  const logLines = elements.consoleTerminal.querySelectorAll('.log-line');
  
  logLines.forEach(line => {
    if (line.textContent.toLowerCase().includes(query)) {
      line.style.display = 'block';
    } else {
      line.style.display = 'none';
    }
  });
}

// ==========================================================================
// THEME & REFRESH HANDLERS
// ==========================================================================
function toggleTheme() {
  const currentBg = getComputedStyle(document.documentElement).getPropertyValue('--bg-app').trim();
  if (currentBg === '#06070a') {
    document.documentElement.style.setProperty('--bg-app', '#1e293b');
    document.documentElement.style.setProperty('--bg-card', '#0f172a');
    document.documentElement.style.setProperty('--bg-sidebar', '#0f172a');
    showToast('🌓 Light theme active (mockup mode)', 'info');
  } else {
    document.documentElement.style.setProperty('--bg-app', '#06070a');
    document.documentElement.style.setProperty('--bg-card', '#0c0e17');
    document.documentElement.style.setProperty('--bg-sidebar', '#090a0f');
    showToast('🌑 Dark theme active', 'info');
  }
}

function refreshDashboard() {
  if (state.isGenerating) {
    toggleGeneration();
  }
  
  state.prompts = [...DEFAULT_PROMPTS];
  elements.promptsTextarea.value = state.prompts.join('\n');
  updatePromptCount();
  
  elements.queueTableBody.innerHTML = `
    <tr class="empty-row">
      <td colspan="4">No active video generations. Enter prompts on the right and click Start.</td>
    </tr>
  `;
  
  state.stats = { total: 0, queued: 0, generating: 0, done: 0, failed: 0, skipped: 0 };
  updateStatsUI();
  clearConsole();
  showToast('🔄 Interface reset successfully.', 'success');
}

// ==========================================================================
// SIMULATOR ENGINE
// ==========================================================================
function toggleGeneration() {
  if (state.isGenerating) {
    // STOP active running states
    state.isGenerating = false;
    clearInterval(state.simulationTimer);
    
    state.queue.forEach(item => {
      if (item.status === 'GENERATING' || item.status === 'DOWNLOADING') {
        item.status = 'FAILED';
        item.action = 'Generation aborted by user.';
        updateTableRow(item);
      }
    });

    logToConsole('WARNING', 'Generation process was force stopped by user.');
    showToast('🛑 Generation stopped.', 'error');
    
    elements.btnStartStop.className = 'btn-action start-btn';
    elements.btnStartStop.querySelector('.btn-text').textContent = 'START GENERATION';
    
    toggleInputs(false);
    recomputeFinalStats();
  } else {
    // START new run
    if (state.prompts.length === 0) {
      showToast('⚠️ No prompts loaded to process!', 'error');
      return;
    }

    state.isGenerating = true;
    toggleInputs(true);
    
    state.concurrentConnections = 1; // Match default connections
    state.batchSize = 30;

    logToConsole('SYSTEM', `Starting batch generation sequence. Connections: 1, Max Batch: ${state.batchSize}`);
    
    state.stats = {
      total: state.prompts.length,
      queued: state.prompts.length,
      generating: 0,
      done: 0,
      failed: 0,
      skipped: 0
    };
    updateStatsUI();

    state.queue = state.prompts.map((prompt, idx) => {
      return {
        id: idx + 1,
        prompt: prompt,
        status: 'QUEUED',
        action: 'Waiting in queue...',
        progressStep: 0
      };
    });
    
    renderQueueTable();

    elements.btnStartStop.className = 'btn-action stop-btn';
    elements.btnStartStop.querySelector('.btn-text').textContent = 'STOP GENERATION';
    
    showToast('🚀 Batch generation sequence started!', 'success');

    state.activeConnectionsCount = 0;
    state.simulationTimer = setInterval(runSimulationStep, 2500); // Step tick
  }
}

function toggleInputs(disabled) {
  elements.promptsTextarea.disabled = disabled;
  elements.settingModel.disabled = disabled;
  elements.settingDuration.disabled = disabled;
  elements.settingRatio.disabled = disabled;
  elements.settingBatch.disabled = disabled;
  elements.settingConcurrent.disabled = disabled;
  elements.btnImportTxt.disabled = disabled;
  elements.btnImportCsv.disabled = disabled;
  elements.btnClearPrompts.disabled = disabled;
  if (elements.btnAddQueue) {
    elements.btnAddQueue.disabled = disabled;
  }
}

function renderQueueTable() {
  elements.queueTableBody.innerHTML = '';
  
  if (state.queue.length === 0) {
    elements.queueTableBody.innerHTML = `
      <tr class="empty-row">
        <td colspan="4">No active video generations. Enter prompts on the right and click Start.</td>
      </tr>
    `;
    return;
  }
  
  state.queue.forEach(item => {
    const tr = document.createElement('tr');
    tr.id = `queue-row-${item.id}`;
    
    let badgeClass = 'status-queued';
    if (item.status === 'GENERATING') badgeClass = 'status-generating';
    else if (item.status === 'DOWNLOADING') badgeClass = 'status-downloading';
    else if (item.status === 'DONE') badgeClass = 'status-success';
    else if (item.status === 'FAILED') badgeClass = 'status-failed';
    
    tr.innerHTML = `
      <td class="col-num">${item.id}</td>
      <td class="col-prompt" title="${item.prompt}">${item.prompt.substring(0, 42)}...</td>
      <td class="col-status">
        <span class="q-status-badge ${badgeClass}">${item.status === 'DONE' ? 'SUCCESS' : item.status}</span>
      </td>
      <td class="col-action" style="display: flex; justify-content: space-between; align-items: center;">
        <span class="action-text">${item.action}</span>
        <button class="delete-row-btn" data-id="${item.id}" title="Delete Row">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </td>
    `;
    
    elements.queueTableBody.appendChild(tr);
  });
  
  // Attach event listeners to all delete buttons
  elements.queueTableBody.querySelectorAll('.delete-row-btn').forEach(btn => {
    btn.addEventListener('click', handleDeleteRow);
  });
}

function updateTableRow(item) {
  const tr = document.getElementById(`queue-row-${item.id}`);
  if (!tr) return;
  
  const tdStatus = tr.querySelector('.col-status');
  const tdAction = tr.querySelector('.col-action');
  
  let badgeClass = 'status-queued';
  if (item.status === 'GENERATING') badgeClass = 'status-generating';
  else if (item.status === 'DOWNLOADING') badgeClass = 'status-downloading';
  else if (item.status === 'DONE') badgeClass = 'status-success';
  else if (item.status === 'FAILED') badgeClass = 'status-failed';
  
  tdStatus.innerHTML = `<span class="q-status-badge ${badgeClass}">${item.status === 'DONE' ? 'SUCCESS' : item.status}</span>`;
  
  const actionTextSpan = tdAction.querySelector('.action-text');
  if (actionTextSpan) {
    actionTextSpan.textContent = item.action;
  } else {
    tdAction.textContent = item.action; // Fallback
  }
}

function handleDeleteRow(e) {
  const btn = e.currentTarget;
  const id = parseInt(btn.getAttribute('data-id'));
  
  const idx = state.queue.findIndex(item => item.id === id);
  if (idx === -1) return;
  
  const item = state.queue[idx];
  state.queue.splice(idx, 1);
  
  state.stats.total--;
  if (item.status === 'QUEUED') {
    state.stats.queued--;
  } else if (item.status === 'GENERATING' || item.status === 'DOWNLOADING') {
    state.stats.generating--;
  } else if (item.status === 'DONE') {
    state.stats.done--;
  } else if (item.status === 'FAILED') {
    state.stats.failed--;
  }
  
  renderQueueTable();
  updateStatsUI();
  
  showToast(`🗑️ Prompt deleted from queue.`, 'info');
  logToConsole('SYSTEM', `Removed row #${id} from the generation queue.`);
}

function addPromptsToQueue() {
  const text = elements.promptsTextarea.value.trim();
  if (!text) {
    showToast('⚠️ Please enter some prompts first.', 'error');
    return;
  }
  
  const newPrompts = text.split('\n').map(p => p.trim()).filter(p => p !== '');
  if (newPrompts.length === 0) {
    showToast('⚠️ No valid prompts found.', 'error');
    return;
  }
  
  let nextId = state.queue.length > 0 ? Math.max(...state.queue.map(q => q.id)) + 1 : 1;
  
  newPrompts.forEach(prompt => {
    state.queue.push({
      id: nextId++,
      prompt: prompt,
      status: 'QUEUED',
      action: 'Waiting in queue...',
      progressStep: 0
    });
    
    state.stats.total++;
    state.stats.queued++;
  });
  
  renderQueueTable();
  updateStatsUI();
  
  elements.promptsTextarea.value = '';
  updatePromptCount();
  
  showToast(`🚀 Added ${newPrompts.length} prompt(s) to queue.`, 'success');
  logToConsole('SYSTEM', `Added ${newPrompts.length} prompts to the generation queue.`);
}

function updateStatsUI() {
  elements.statTotal.textContent = state.stats.total;
  elements.statQueued.textContent = state.stats.queued;
  elements.statGenerating.textContent = state.stats.generating;
  elements.statDone.textContent = state.stats.done;
  elements.statFailed.textContent = state.stats.failed;
  elements.statSkipped.textContent = state.stats.skipped;
  
  const processed = state.stats.done + state.stats.failed;
  const pct = state.stats.total > 0 ? Math.round((processed / state.stats.total) * 100) : 0;
  
  elements.progressText.textContent = `${processed}/${state.stats.total} done (${pct}%)`;
  elements.progressBarFill.style.width = `${pct}%`;
}

function recomputeFinalStats() {
  state.stats.queued = state.queue.filter(i => i.status === 'QUEUED').length;
  state.stats.generating = state.queue.filter(i => i.status === 'GENERATING' || i.status === 'DOWNLOADING').length;
  state.stats.done = state.queue.filter(i => i.status === 'DONE').length;
  state.stats.failed = state.queue.filter(i => i.status === 'FAILED').length;
  updateStatsUI();
}

// SIMULATOR LOOP TICK
function runSimulationStep() {
  let activeGeneratingItems = state.queue.filter(item => item.status === 'GENERATING' || item.status === 'DOWNLOADING');
  state.activeConnectionsCount = activeGeneratingItems.length;

  activeGeneratingItems.forEach(item => {
    item.progressStep++;
    
    if (item.status === 'GENERATING') {
      if (item.progressStep === 1) {
        logToConsole('INFO', `Row ${item.id}: Processing video request (attempt ${Math.floor(Math.random()*15)+5}/250)...`);
        item.action = "Processing...";
      } else if (item.progressStep === 3) {
        logToConsole('INFO', `Row ${item.id}: Compiling frames and audio layers...`);
        item.action = "Compiling video...";
      } else if (item.progressStep === 5) {
        item.status = 'DOWNLOADING';
        item.progressStep = 0;
        logToConsole('INFO', `Row ${item.id}: [+] Removing watermark...`);
        item.action = "Cleaning watermark...";
        state.stats.generating = state.queue.filter(i => i.status === 'GENERATING' || i.status === 'DOWNLOADING').length;
      }
    } 
    else if (item.status === 'DOWNLOADING') {
      if (item.progressStep === 1) {
        const x = Math.floor(Math.random() * 50) + 550;
        const y = Math.floor(Math.random() * 50) + 1200;
        logToConsole('INFO', `Row ${item.id}: [+] Watermark detected at: x=${x}, y=${y}, w=128, h=48`);
        item.action = "Watermark cleaned.";
      } else if (item.progressStep === 2) {
        const failedRandom = Math.random() < 0.05;
        if (failedRandom) {
          item.status = 'FAILED';
          item.action = "Failed: API server dropped connection.";
          logToConsole('ERROR', `Row ${item.id}: API error during file download.`);
          state.stats.failed++;
        } else {
          item.status = 'DONE';
          item.action = "Video generated successfully.";
          logToConsole('SUCCESS', `Row ${item.id}: Video is ready for download.`);
          state.stats.done++;
        }
        state.stats.generating--;
        updateStatsUI();
      }
    }
    
    updateTableRow(item);
  });

  // Refill connections based on concurrency rate
  let queuedItems = state.queue.filter(item => item.status === 'QUEUED');
  
  if (queuedItems.length === 0 && activeGeneratingItems.length === 0) {
    logToConsole('SUCCESS', 'All video generations in the batch completed.');
    showToast('🎉 All videos processed!', 'success');
    
    state.isGenerating = false;
    clearInterval(state.simulationTimer);
    
    elements.btnStartStop.className = 'btn-action start-btn';
    elements.btnStartStop.querySelector('.btn-text').textContent = 'START GENERATION';
    toggleInputs(false);
    return;
  }

  // Refill slots
  while (state.activeConnectionsCount < 6 && queuedItems.length > 0) {
    const nextItem = queuedItems.shift();
    nextItem.status = 'GENERATING';
    nextItem.progressStep = 0;
    nextItem.action = 'Processing...';
    
    state.stats.queued--;
    state.stats.generating++;
    state.activeConnectionsCount++;
    
    updateTableRow(nextItem);
    updateStatsUI();
  }
}
