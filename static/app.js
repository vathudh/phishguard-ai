const form = document.querySelector('#scanForm');
const resultPanel = document.querySelector('#resultPanel');
const formMessage = document.querySelector('#formMessage');
const historyList = document.querySelector('#historyList');

const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));

function showMessage(message, type = '') {
  formMessage.textContent = message;
  formMessage.className = `form-message ${type}`;
}

function renderResult(result) {
  const indicatorHtml = result.indicators.map(item => `<li class="indicator ${item.level}"><span></span><div><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.detail)}</p></div></li>`).join('');
  const urlHtml = result.urls.length ? result.urls.map(url => `<div class="url-item"><div><strong>${escapeHtml(url.domain)}</strong><small>${escapeHtml(url.url)}</small></div><span class="url-risk ${url.risk >= 35 ? 'danger' : url.risk >= 15 ? 'warning' : ''}">${url.risk}% risk</span><p>${url.signals.map(escapeHtml).join(' · ')}</p></div>`).join('') : '<p class="muted">No URLs found in this email.</p>';
  resultPanel.className = 'panel result-panel';
  resultPanel.innerHTML = `<div class="panel-heading"><div><p class="eyebrow">SCAN RESULT</p><h2>${escapeHtml(result.verdict)}</h2></div><span class="verdict-badge ${result.severity}">${escapeHtml(result.severity)} risk</span></div><div class="score-layout"><div class="score-ring ${result.severity}" style="--score:${result.risk_score}"><div><strong>${result.risk_score}</strong><small>/100 risk</small></div></div><div><p class="recommendation">${escapeHtml(result.recommendation)}</p><div class="metric-row"><span>Model confidence <b>${result.model_confidence}%</b></span><span>Phishing likelihood <b>${result.phishing_probability}%</b></span></div></div></div><div class="result-section"><h3>Why this was flagged</h3><ul class="indicator-list">${indicatorHtml}</ul></div><div class="result-section"><h3>URL intelligence</h3>${urlHtml}</div><div class="feedback"><span>Was this result correct?</span><button data-feedback="phishing" data-id="${result.scan_id}">Yes, phishing</button><button data-feedback="safe" data-id="${result.scan_id}">No, safe</button></div>`;
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}

async function scanEmail(payload) {
  showMessage('Analyzing message signals...', 'loading');
  const result = await requestJson('/api/scan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  renderResult(result);
  showMessage('Scan saved securely on this device.', 'success');
  loadHistory();
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  try { await scanEmail({ subject: document.querySelector('#subject').value, sender: document.querySelector('#sender').value, email_text: document.querySelector('#emailText').value }); }
  catch (error) { showMessage(error.message, 'error'); }
});

document.querySelector('#demoButton').addEventListener('click', () => {
  document.querySelector('#subject').value = 'Urgent: Your account requires immediate verification';
  document.querySelector('#sender').value = 'Security Team <alert.verify@gmail.com>';
  document.querySelector('#emailText').value = 'URGENT! We detected suspicious activity on your Microsoft account. Verify your password immediately at http://198.51.100.12/microsoft-login to avoid account suspension within 24 hours.';
  showMessage('Demo email loaded. Run the scan when ready.');
});

document.querySelector('#emlFile').addEventListener('change', async event => {
  const file = event.target.files[0];
  if (!file) return;
  const body = new FormData(); body.append('email_file', file);
  try { showMessage('Reading .eml file...', 'loading'); const result = await requestJson('/api/upload-eml', { method: 'POST', body }); renderResult(result); showMessage('Email file scanned and saved.', 'success'); loadHistory(); }
  catch (error) { showMessage(error.message, 'error'); }
  event.target.value = '';
});

resultPanel.addEventListener('click', async event => {
  const button = event.target.closest('[data-feedback]');
  if (!button) return;
  try { await requestJson(`/api/scans/${button.dataset.id}/feedback`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ feedback: button.dataset.feedback }) }); button.parentElement.innerHTML = '<span class="feedback-thanks">Thank you. Feedback saved locally.</span>'; loadHistory(); }
  catch (error) { showMessage(error.message, 'error'); }
});

async function loadHistory() {
  const items = await requestJson('/api/history');
  document.querySelector('#historyCount').textContent = items.length;
  historyList.innerHTML = items.length ? items.map(item => `<article class="history-item"><span class="history-verdict ${item.verdict.toLowerCase().replace(' ', '-')}">${escapeHtml(item.verdict)}</span><div><strong>${escapeHtml(item.subject || 'Untitled email')}</strong><p>${escapeHtml(item.sender || item.email_preview)}</p></div><div class="history-score"><b>${item.risk_score}</b><small>risk score</small></div><time>${new Date(item.created_at).toLocaleString()}</time></article>`).join('') : '<p class="muted">No scans saved yet.</p>';
}

document.querySelector('#exportButton').addEventListener('click', () => { window.location.assign('/api/export'); });
loadHistory().catch(() => { historyList.innerHTML = '<p class="muted">History is temporarily unavailable.</p>'; });
