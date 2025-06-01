
# Документация: поддержка тёмной темы

## Назначение
Добавлен режим «тёмная тема», который переключает цветовую схему приложения без перезагрузки страницы.  
Состояние сохраняется в `localStorage`, поэтому выбор запоминается между сеансами.

---

## Задействованные файлы

| Файл | Назначение |
|------|-----------|
| `templates/base.html` | Начальное применение класса `dark-mode`, кнопка‑иконка и подключение скрипта |
| `static/js/theme.js`  | Логика переключения темы и сохранения выбора |
| `static/css/style29.css` | Все CSS‑переопределения для тёмной темы |

---

## 1. Изменения в `base.html`

### Авто‑применение сохранённой темы
```html
<script>
(function () {
  try {
    if (localStorage.getItem('theme') === 'dark') {
      document.documentElement.classList.add('dark-mode');
    }
  } catch (e) {}
})();
</script>
```

### Кнопка переключения
```html
<button id="theme-toggle"
        class="profile__bar-theme-icon"
        title="Сменить тему">
</button>
```

### Подключение скрипта
```django
{% load static %}
<script src="{% static 'js/theme.js' %}"></script>
```

---

## 2. Скрипт `theme.js`

```javascript
document.addEventListener('DOMContentLoaded', () => {
  const btn  = document.getElementById('theme-toggle');
  const root = document.documentElement;

  // выставляем стартовую иконку
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {
    root.classList.add('dark-mode');
    btn.classList.add('moon');
  } else {
    btn.classList.add('sun');
  }

  // обработчик клика
  btn?.addEventListener('click', () => {
    const isDark = root.classList.toggle('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    btn.classList.toggle('moon', isDark);
    btn.classList.toggle('sun', !isDark);
  });
});
```

**Что делает скрипт**

1. При загрузке страницы проверяет сохранённое значение в `localStorage`.
2. Ставит соответствующую иконку (`sun.svg` / `moon.svg`) и класс `dark-mode`.
3. По нажатию toggle `dark-mode`, меняет иконку и сохраняет выбор.

---

## 3. Стили в `style29.css`

### Кнопка‑иконка
```css
.profile__bar-theme-icon {
  display: inline-block;
  width: 35px;
  height: 35px;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 22px 22px;
  border: none;
  background-color: transparent;
  cursor: pointer;
}

.profile__bar-theme-icon.sun  { background-image: url('./img/sun.svg');  }
.profile__bar-theme-icon.moon { background-image: url('./img/moon.svg'); }
```

### Базовые цвета (для всего тела страницы)
```css
html.dark-mode body {
  background-color: #121212;
  color: #e0e0e0;
}
```

### Примеры целевых переопределений

```css
/* Заголовки */
html.dark-mode body h1,
html.dark-mode body h2,
html.dark-mode body h3,
html.dark-mode body h4,
html.dark-mode body h5,
html.dark-mode body h6 {
  color: #f0f0f0;
}

/* Таблицы */
html.dark-mode table,
html.dark-mode th,
html.dark-mode td {
  background-color: #1a1a1a;
  border-color: #333;
}

/* Карточки и панели */
html.dark-mode .white,
html.dark-mode .header__menu,
html.dark-mode .sidebar {
  background-color: #1f1f1f;
}

/* Строки‑статусы */
html.dark-mode tr.success { background: #234d2b; }
html.dark-mode tr.unluck  { background: #612828; }
```

> **Важно.** Все переопределения находятся в `style29.css` после комментария  
> `/* === DARK MODE: базовые цвета и тексты === */`.  
> При добавлении новых компонентов используйте тот же селектор‑префикс  
> `html.dark-mode …`, чтобы изменения применялись только в тёмной теме.

---

## 4. Расширение функциональности

1. **Новые элементы интерфейса** — добавляйте CSS‑правила под блоком DARK MODE, не трогая светлую тему.  
2. **Иконки темы** — замените файлы `sun.svg` / `moon.svg` в каталоге `static/img/`.  
3. **Сброс темы** — чтобы сбросить выбор, удалите ключ `theme` в `localStorage` через инструменты разработчика.

---
