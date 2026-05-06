// ─── Drag & Drop ───────────────────────────
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileNameEl = document.getElementById('file-name');

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) {
    fileNameEl.textContent = '✓ ' + fileInput.files[0].name;
    fileNameEl.style.display = 'block';
  }
});

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files[0]) {
    fileInput.files = e.dataTransfer.files;
    fileNameEl.textContent = '✓ ' + e.dataTransfer.files[0].name;
    fileNameEl.style.display = 'block';
  }
});

// ─── Upload ────────────────────────────────
async function uploadFile() {
  const file = fileInput.files[0];
  const uploader = document.getElementById('uploader-name').value || 'Anonymous';

  if (!file) {
    showAlert('upload-alert', 'error', 'Please select a file first!');
    return;
  }

  document.getElementById('upload-progress').style.display = 'block';
  document.getElementById('upload-alert').style.display = 'none';
  animateProgress();

  const formData = new FormData();
  formData.append('file', file);
  formData.append('uploader', uploader);

  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();

    document.getElementById('upload-progress').style.display = 'none';
    if (data.success) {
      showAlert('upload-alert', 'success',
        `✓ "${file.name}" uploaded! Split into ${data.blocks} blocks. Size: ${formatBytes(data.size)}`);
      loadFiles();
    } else {
      showAlert('upload-alert', 'error', '✗ Error: ' + data.error);
    }
  } catch (err) {
    document.getElementById('upload-progress').style.display = 'none';
    showAlert('upload-alert', 'error', '✗ Upload failed: ' + err.message);
  }
}

function animateProgress() {
  const bar = document.getElementById('upload-bar');
  const status = document.getElementById('upload-status');
  const steps = [
    [20, 'Splitting file into 64MB blocks...'],
    [50, 'Encrypting blocks with AES-256...'],
    [80, 'Uploading to HDFS storage...'],
    [95, 'Saving metadata...']
  ];
  steps.forEach(([pct, msg], i) => {
    setTimeout(() => {
      bar.style.width = pct + '%';
      status.textContent = msg;
    }, i * 800);
  });
}

// ─── Download ──────────────────────────────
function downloadFile() {
  const fname = document.getElementById('download-filename').value.trim();
  if (!fname) {
    showAlert('download-alert', 'error', 'Please enter a filename!');
    return;
  }
  showAlert('download-alert', 'success', '⏳ Decrypting and downloading...');
  window.location.href = '/download/' + encodeURIComponent(fname);
  setTimeout(() => { document.getElementById('download-alert').style.display = 'none'; }, 3000);
}

// ─── File List ─────────────────────────────
async function loadFiles() {
  const tbody = document.getElementById('files-list');
  try {
    const res = await fetch('/files');
    const files = await res.json();

    document.getElementById('stat-files').textContent = files.length;
    const totalBlocks = files.reduce((s, f) => s + (f.blocks || 0), 0);
    document.getElementById('stat-blocks').textContent = totalBlocks;

    if (files.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="no-files">No files uploaded yet. Upload your first file above! 👆</td></tr>';
      return;
    }

    tbody.innerHTML = files.map(f => `
      <tr>
        <td>
          <span class="file-icon">${getIcon(f.filename)}</span>
          <strong>${f.filename}</strong>
        </td>
        <td style="color:var(--muted)">${f.uploader || 'Unknown'}</td>
        <td>${formatBytes(f.size)}</td>
        <td><span class="tag">${f.blocks} blocks</span></td>
        <td>
          <button class="dl-btn" onclick="quickDownload('${f.filename}')">📥 Download</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="5" class="no-files">Could not load files. Make sure server is running.</td></tr>';
  }
}

function quickDownload(fname) {
  document.getElementById('download-filename').value = fname;
  showAlert('download-alert', 'success', '⏳ Downloading: ' + fname);
  window.location.href = '/download/' + encodeURIComponent(fname);
}

// ─── Helpers ───────────────────────────────
function showAlert(id, type, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = 'alert alert-' + type;
  el.style.display = 'block';
}

function formatBytes(bytes) {
  if (!bytes) return 'Unknown';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

function getIcon(fname) {
  if (!fname) return '📄';
  const ext = fname.split('.').pop().toLowerCase();
  const icons = { pdf: '📕', doc: '📝', docx: '📝', ppt: '📊', pptx: '📊',
    xls: '📈', xlsx: '📈', zip: '📦', rar: '📦', mp4: '🎬',
    mp3: '🎵', jpg: '🖼', jpeg: '🖼', png: '🖼', txt: '📄', py: '🐍' };
  return icons[ext] || '📄';
}

window.onload = loadFiles;
