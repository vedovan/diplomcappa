# Таймер выполнения заданий (обновлённая документация)

## Зачем нужен

* фиксирует **реальное время** работы студента над заданием;
* учитывает паузы: можно сохранять черновик и продолжить позже;
* определяет, было ли решение слишком быстрым (`needs_manual_check`);
* отображает накопленное время и знак вопроса только **преподавателю**.

---

## 1. Где хранятся настройки

| Файл | Фрагмент | Что добавлено |
|------|----------|---------------|
| `models/task.py` | `min_duration` (`DurationField`) | Минимальное время выполнения (по умолчанию 1 минута) |
| `models/draft.py` | `time_spent` (`FloatField`) | Накопитель времени черновика |
| `models/solution.py` | `started_at`, `time_spent`, `needs_manual_check` | Полный тайминг решения |

---

## 2. Клиент: инициализация и учёт времени

### 2.1 Инициализация (в `editor.html` через `editor2.js`)
```js
let start = Date.now();
let base  = 0;

window.getSessionSeconds = () => Math.floor((Date.now() - start) / 1000);
window.getElapsedSeconds = () => base + getSessionSeconds();
window.setBaseTime = sec => { base = sec; start = Date.now(); };
window.resetTimer  = () => { base += getSessionSeconds(); start = Date.now(); };
```
При повторном открытии `elapsed_seconds` передаётся из Django и вызывает `setBaseTime()`.

---

### 2.2 Сохранение черновика
```js
const elapsed = typeof getSessionSeconds === 'function' ? getSessionSeconds() : 0;

$.ajax({
  url: '/api/tasks/<id>/draft/',
  method: 'POST',
  data: JSON.stringify({ code: content, elapsed }),
});
```
Накапливаются только секунды текущей сессии.

---

### 2.3 Отправка решения
Тот же механизм, только `elapsed` передаётся в `create_solution`. После успешной отправки вызывается `resetTimer()`.

---

## 3. Сервер: расчёт и логика проверки

### 3.1 Обработка черновика (`views/draft.py`)
```python
draft.time_spent = F('time_spent') + elapsed
draft.save(update_fields=['time_spent'])
```

---

### 3.2 Финальное решение (`views/base.py`)
```python
total_time = draft_time + elapsed
min_time = task.min_duration.total_seconds() or 60

solution.time_spent = total_time
solution.needs_manual_check = total_time < min_time
```
Если `total_time` меньше порога, выставляется флаг ручной проверки.

---

## 4. Отображение времени и отметки «?»

### 4.1 В статистике группы (`group_statistics.py`)
```python
cell["execution_time"] = int(solution.time_spent or 0)
cell["needs_manual_check"] = solution.needs_manual_check
```

---

### 4.2 В JS-таблице (`group_course24.js`)
```js
if (isTeacher && data.execution_time > 0) {
  td.title += `\nВремя: ${format(data.execution_time)}`;
}
if (isTeacher && data.needs_manual_check && !underReview) {
  cell.textContent = '?';
  td.classList.add('s-orange');
}
```
Знак вопроса скрывается, если решение ещё на проверке.

---

### 4.3 В шаблоне решения (`template.html`)
```django
{% if object.time_spent %}
  <p><strong>Время выполнения:</strong> {{ object.time_spent|duration_hm }}</p>
{% endif %}
{% if object.needs_manual_check %}
  <p class="text-warning">❓ Решение получено слишком быстро, требуется проверка.</p>
{% endif %}
```

---

## 5. Стилизация (`style29.css`)
```css
.s-orange { background-color: #f4863c !important; }
html.dark-mode body .s-orange { background-color: #9c7d20 !important; }
```

---

## 6. Фильтр отображения времени (`time_filters.py`)
```python
@register.filter
def duration_hm(value):
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return "—"
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes} мин {sec:02d} сек"
```

---

## 7. Полный список изменённых файлов

```
src/app/tasks/api/views/base.py
src/app/tasks/api/serializers/draft.py
src/app/tasks/api/serializers/taskitem.py
src/app/tasks/models/task.py
src/app/tasks/models/solution.py
src/app/tasks/models/draft.py
src/app/tasks/templatetags/time_filters.py
src/app/tasks/templatetags/tasks_tags.py
src/app/tasks/templates/taskitem/editor.html
src/app/tasks/templates/taskitem/parts/editor.html
src/app/tasks/templates/tasks/solution/template.html
src/app/groups/templates/group_course.html
src/app/groups/services/group_statistics.py
src/app/groups/api/views.py
src/app/tasks/api/views.py
src/static/js/editor2.js
src/static/js/group_course24.js
src/static/css/style29.css
src/app/tasks/models/entities.py
src/app/tasks/models/taskitem.py
```

---

