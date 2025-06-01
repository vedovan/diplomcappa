(function () {
    let start = Date.now();
    let base  = 0;

    window.getSessionSeconds = () =>
        Math.floor((Date.now() - start) / 1000);

    window.getElapsedSeconds = () =>
        base + window.getSessionSeconds();

    window.resetTimer = () => {
        base += window.getSessionSeconds();
        start = Date.now();
    };

    window.setBaseTime = seconds => {
        base  = seconds;
        start = Date.now();
    };

    const timerEl = document.getElementById("timer");
    if (!timerEl) return;

    const initial = parseInt(timerEl.dataset.elapsed || "0", 10);
    if (!isNaN(initial)) base = initial;

    function format(sec) {
        const m = String(Math.floor(sec / 60)).padStart(2, "0");
        const s = String(sec % 60).padStart(2, "0");
        return `${m}:${s}`;
    }

    setInterval(() => {
        timerEl.textContent = format(window.getElapsedSeconds());
    }, 1000);
})();
