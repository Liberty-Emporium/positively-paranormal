// ─── Positively Paranormal — Main App ──────────────────────

// Auto-dismiss messages
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.message').forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity .5s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });
});

// Device motion permission for iOS 13+
async function requestMotionPermission() {
    if (typeof DeviceOrientationEvent !== 'undefined' &&
        typeof DeviceOrientationEvent.requestPermission === 'function') {
        try {
            const perm = await DeviceOrientationEvent.requestPermission();
            return perm === 'granted';
        } catch { return false; }
    }
    return true; // Android or desktop — no permission needed
}

// Audio context helper
function getAudioContext() {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    return ctx;
}