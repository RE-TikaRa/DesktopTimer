AOS.init({
    once: true,
    offset: 50,
    duration: 800,
});

const systemThemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
const THEME_MODE_KEY = 'themeMode';
const THEME_KEY = 'theme';

function setTheme(isDark) {
    document.documentElement.classList.toggle('dark', isDark);
}

function getThemeMode() {
    return localStorage.getItem(THEME_MODE_KEY) || 'system';
}

function getManualTheme() {
    return localStorage.getItem(THEME_KEY) || 'light';
}

function applySystemTheme() {
    if (getThemeMode() !== 'system') {
        return;
    }
    setTheme(systemThemeQuery.matches);
}

function applyManualTheme() {
    if (getThemeMode() !== 'manual') {
        return;
    }
    setTheme(getManualTheme() === 'dark');
}

function setThemeMode(mode) {
    localStorage.setItem(THEME_MODE_KEY, mode);
    if (mode === 'system') {
        applySystemTheme();
    } else {
        applyManualTheme();
    }
    updateModeButtons();
}

function toggleTheme() {
    if (getThemeMode() === 'system') {
        setThemeMode('manual');
    }
    const isDark = !document.documentElement.classList.contains('dark');
    setTheme(isDark);
    localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
}

function toggleThemeMode() {
    const nextMode = getThemeMode() === 'system' ? 'manual' : 'system';
    setThemeMode(nextMode);
}

function updateModeButtons() {
    const mode = getThemeMode();
    const label = mode === 'system' ? '系统' : '手动';
    const icon = mode === 'system' ? 'fa-desktop' : 'fa-hand-pointer';

    const buttons = [
        document.getElementById('theme-mode-toggle'),
        document.getElementById('mobile-theme-mode-toggle'),
    ];

    buttons.forEach((button) => {
        if (!button) {
            return;
        }
        const iconEl = button.querySelector('i');
        const textEl = button.querySelector('span');
        if (iconEl) {
            iconEl.classList.remove('fa-desktop', 'fa-hand-pointer');
            iconEl.classList.add(icon);
        }
        if (textEl) {
            textEl.textContent = label;
        }
    });
}

applySystemTheme();
applyManualTheme();
updateModeButtons();

if (systemThemeQuery.addEventListener) {
    systemThemeQuery.addEventListener('change', applySystemTheme);
} else if (systemThemeQuery.addListener) {
    systemThemeQuery.addListener(applySystemTheme);
}

const themeModeToggleBtn = document.getElementById('theme-mode-toggle');
const mobileThemeModeToggleBtn = document.getElementById('mobile-theme-mode-toggle');
const themeToggleBtn = document.getElementById('theme-toggle');
const mobileThemeToggleBtn = document.getElementById('mobile-theme-toggle');

if (themeModeToggleBtn) {
    themeModeToggleBtn.addEventListener('click', toggleThemeMode);
}
if (mobileThemeModeToggleBtn) {
    mobileThemeModeToggleBtn.addEventListener('click', toggleThemeMode);
}
if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
}
if (mobileThemeToggleBtn) {
    mobileThemeToggleBtn.addEventListener('click', toggleTheme);
}

const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
        const icon = mobileMenuBtn.querySelector('i');
        if (mobileMenu.classList.contains('hidden')) {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        } else {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        }
    });
}
