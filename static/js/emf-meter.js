// ─── EMF Meter ───────────────────────────────────────────────

const startBtn = document.getElementById('startMeterBtn');
const logBtn = document.getElementById('logReadingBtn');
const calibrateBtn = document.getElementById('calibrateBtn');
const emfValue = document.getElementById('emfValue');
const emfGauge = document.getElementById('emfGauge');
const chartCanvas = document.getElementById('emfChart');
const ctx = chartCanvas?.getContext('2d');

let isRunning = false;
let currentLevel = 0;
let readingsHistory = [];
let watchId = null;
let calibratedOffset = 0;
let calibrateBase = 0;

// ─── Start / Stop Meter ──────────────────────────────────
startBtn.addEventListener('click', async () => {
    if (isRunning) {
        stopMeter();
        return;
    }

    const perm = await requestMotionPermission();
    if (!perm) {
        alert('Motion sensor permission denied. EMF meter needs device orientation access.');
        return;
    }

    // Also try to get magnetometer via generic sensor API
    startMagnetometer();
    startBtn.textContent = '⏹️ Stop Meter';
    startBtn.classList.add('recording');
    isRunning = true;
    logBtn.disabled = false;
});

function stopMeter() {
    if (watchId !== null) {
        window.removeEventListener('deviceorientation', handleOrientation);
        watchId = null;
    }
    isRunning = false;
    startBtn.textContent = '📡 Start Meter';
    startBtn.classList.remove('recording');
    logBtn.disabled = true;
}

// ─── Magnetometer via DeviceOrientation ──────────────────
function startMagnetometer() {
    // DeviceOrientation gives alpha (compass heading) — not raw EMF,
    // but we simulate EMF by tracking fluctuations in the compass reading.
    // On many phones the magnetometer IS accessible through alpha.
    calibrateBase = 0;
    let samples = [];
    let calibrating = true;
    let calibrateCount = 0;

    // Also try the Generic Sensor API for Magnetometer (Chrome Android)
    if ('Magnetometer' in window) {
        try {
            const magnetometer = new Magnetometer({ frequency: 30 });
            magnetometer.addEventListener('reading', () => {
                const x = magnetometer.x || 0;
                const y = magnetometer.y || 0;
                const z = magnetometer.z || 0;
                const magnitude = Math.sqrt(x*x + y*y + z*z);
                processReading(magnitude / 100); // scale to mG-ish
            });
            magnetometer.start();
            return; // prefer this path
        } catch {}
    }

    // Fallback: track compass heading fluctuations
    watchId = window.addEventListener('deviceorientation', handleOrientation);
}

function handleOrientation(event) {
    const alpha = event.alpha || 0; // compass heading 0-360
    const gamma = event.gamma || 0;
    const beta = event.beta || 0;

    // Simulate EMF from sensor noise + fluctuations
    const baseFluctuation = Math.abs(alpha) / 36; // 0-10 scale
    const movementNoise = (Math.abs(gamma) + Math.abs(beta)) / 20;
    let reading = baseFluctuation + movementNoise * 0.5;

    processReading(reading);
}

function processReading(raw) {
    const level = Math.max(0, parseFloat((raw - calibratedOffset).toFixed(2)));
    currentLevel = level;
    emfValue.textContent = level.toFixed(2);

    // Update gauge color
    emfGauge.className = 'emf-gauge';
    if (level < 1.0) emfGauge.classList.add('low');
    else if (level < 3.0) emfGauge.classList.add('mid');
    else if (level < 5.0) emfGauge.classList.add('high');
    else emfGauge.classList.add('critical');

    // Update value color
    emfValue.style.color = getComputedStyle(document.documentElement)
        .getPropertyValue(`--emf-${level < 1.0 ? 'low' : level < 3.0 ? 'mid' : level < 5.0 ? 'high' : 'critical'}`).trim();

    // Update scale indicator
    const scaleEls = document.querySelectorAll('.emf-scale span');
    scaleEls.forEach(el => el.style.color = '');
    if (level < 2.5) scaleEls[0].style.color = '#44cc88';
    else if (level < 5.0) scaleEls[1].style.color = '#ffaa44';
    else if (level < 10.0) scaleEls[2].style.color = '#ff6644';
    else scaleEls[3].style.color = '#ff2244';
}

// ─── Calibrate ───────────────────────────────────────────
calibrateBtn.addEventListener('click', () => {
    calibratedOffset = currentLevel;
    calibrateBtn.textContent = '🎯 Calibrated!';
    setTimeout(() => { calibrateBtn.textContent = '🎯 Calibrate'; }, 2000);
});

// ─── Log Reading ─────────────────────────────────────────
logBtn.addEventListener('click', async () => {
    const location = document.getElementById('readingLocation')?.value || '';
    const notes = document.getElementById('readingNotes')?.value || '';

    readingsHistory.push(currentLevel);
    updateChart();

    const payload = {
        level: currentLevel,
        location,
        notes,
    };

    try {
        const resp = await fetch(window.EMF_CONFIG.saveUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
            body: JSON.stringify(payload),
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            const readingDiv = document.createElement('div');
            readingDiv.className = 'reading-card';
            readingDiv.innerHTML = `
                <span class="emf-level">${data.level.toFixed(2)} <small>mG</small></span>
                ${location ? `<p>${location}</p>` : ''}
                <p class="timestamp">Just now</p>
            `;
            document.getElementById('readingsList')?.appendChild(readingDiv);
        }
    } catch (err) {
        console.error('Failed to log reading:', err);
        alert('Failed to save reading.');
    }
});

// ─── Mini Chart ──────────────────────────────────────────
function updateChart() {
    if (!ctx || readingsHistory.length < 2) return;
    const w = chartCanvas.width, h = chartCanvas.height;
    ctx.clearRect(0, 0, w, h);

    const maxV = Math.max(10, ...readingsHistory);
    const step = w / Math.max(readingsHistory.length - 1, 1);

    ctx.beginPath();
    ctx.strokeStyle = '#6b4fff';
    ctx.lineWidth = 2;

    readingsHistory.forEach((val, i) => {
        const x = i * step;
        const y = h - (val / maxV) * h;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Fill under curve
    readingsHistory.forEach((val, i) => {
        const x = i * step;
        const y = h - (val / maxV) * h;
        ctx.lineTo(x, y);
    });
    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fillStyle = 'rgba(107, 79, 255, 0.1)';
    ctx.fill();
}

// ─── Load existing readings for chart ────────────────────
async function loadReadings() {
    try {
        const resp = await fetch(window.EMF_CONFIG.readingsUrl);
        const data = await resp.json();
        if (data.readings) {
            readingsHistory = data.readings.map(r => r.level).reverse();
            if (readingsHistory.length > 0) updateChart();
        }
    } catch {}
}
loadReadings();

function getCsrf() {
    const name = 'csrftoken';
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : '';
}