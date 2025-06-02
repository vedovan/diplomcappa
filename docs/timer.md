# Таймер выполнения заданий

## Зачем нужен

* фиксирует **реальное время** работы студента над заданием;
* суммирует паузы — если студент сохранил черновик и вернулся позже, время не теряется;
* автоматически помечает «молниеносные» решения флагом `needs_manual_check`;
* отображает накопленное время и знак вопроса **только преподавателю**.

---

## 1. Где хранятся настройки

| Файл | Фрагмент | Что добавлено |
|------|----------|--------------|
| `models/task.py` | `min_duration` (`DurationField`) | Минимально допустимое время решения (по‑умолчанию — 1 минута) |
| `models/draft.py` | `time_spent` (`FloatField`) | Суммарное время черновиков |
| `models/solution.py` | `started_at`, `time_spent`, `needs_manual_check` | Дата начала, итоговое время и флаг «быстро» |

---

## 2. Клиент: запуск и отправка времени

### 2.1 Получение времени перед сохранением (`editor2.js`)
```javascript
const elapsed = (typeof window.getSessionSeconds === 'function')
    ? window.getSessionSeconds()
    : 0;
```
Значение `elapsed` отправляется в черновик и финальное решение. Таймер считается встроенными функциями шаблона, определёнными через `editor.html`.

### 2.2 Обнуление таймера после отправки
```javascript
window.resetTimer && window.resetTimer();
```
После успешного сохранения или отправки решение, таймер сбрасывается.

---

## 3. Сервер: расчёт времени и проверка

### 3.1 Обработка черновика (`views/draft.py`)
```python
draft.time_spent = F('time_spent') + elapsed
draft.save(update_fields=['time_spent'])
```

### 3.2 Финальное решение (`views/base.py`)
```python
total_time = draft_time + elapsed
min_time = task.min_duration.total_seconds() or 60

solution.time_spent = total_time
solution.needs_manual_check = total_time < min_time
```

---

## 4. Отображение времени и «?» преподавателю

### 4.1 В сервисе статистики (`group_statistics.py`)
```python
cell["execution_time"] = int(solution.time_spent or 0)
cell["needs_manual_check"] = solution.needs_manual_check
```

### 4.2 В JS-таблице (`group_course24.js`)
```javascript
if (isTeacher && data.execution_time > 0) {
  td.title += `\nВремя: ${format(data.execution_time)}`;
}
if (isTeacher && data.needs_manual_check && !underReview) {
  cell.textContent = '?';
  td.classList.add('s-orange');
}
```

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

## 5. Стили (`style29.css`)
```css
.s-orange { background-color:#f4863c !important; }
html.dark-mode body .s-orange { background-color:#9c7d20 !important; }
```

---

## 6. Фильтр форматирования (`time_filters.py`)
```python
@register.filter
def duration_hm(value):
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return "—"
    return f"{seconds//60} мин {seconds%60:02d} сек"
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

