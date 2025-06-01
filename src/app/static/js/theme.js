document.addEventListener('DOMContentLoaded', function () {
    const themeBtn = document.getElementById('theme-toggle');
    const root = document.documentElement;

    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'dark') {
        root.classList.add('dark-mode');
        themeBtn?.classList.add('moon');
    } else {
        themeBtn?.classList.add('sun');
    }

    themeBtn?.addEventListener('click', function () {
        const isDark = root.classList.toggle('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        themeBtn.classList.toggle('moon', isDark);
        themeBtn.classList.toggle('sun', !isDark);
    });
});