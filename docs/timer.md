
# Таймер выполнения заданий

## Зачем нужен

* фиксирует **реальное время** работы студента над заданием;
* учитывает паузы — студент может сохранить черновик и вернуться позже;
* определяет, было ли решение «слишком быстрым» (`needs_manual_check`);
* выводит накопленное время и вопросительный знак **только преподавателю**.

---

## 1. Где хранятся настройки

| Файл | Фрагмент | Что добавлено |
|------|----------|--------------|
| `app/tasks/models/task.py` | поле `min_duration` (`DurationField`) | Минимальное время, за которое *допустимо* решить задачу (по умолчанию 1 мин). |
| `app/tasks/models/solution.py` | `time_spent` (`FloatField`) <br>`needs_manual_check` (`BooleanField`) | Суммарное время решения и флаг «быстро». |
| `app/tasks/models/draft.py` | `time_spent` (`FloatField`) | Накопитель времени для черновиков. |

---

## 2. Клиент: старт и накопление таймера

### 2.1. Инициализация (шаблон `editor.html` → `static/js/editor2.js`)
```javascript
let start = Date.now();  // начало сессии
let base  = 0;           // накоплено в прошлых заходах

window.getSessionSeconds = () => Math.floor((Date.now() - start) / 1000);
window.getElapsedSeconds = () => base + getSessionSeconds();
window.setBaseTime       = sec => { base = sec; start = Date.now(); };
window.resetTimer        = () => { base += getSessionSeconds(); start = Date.now(); };
```
*При повторном открытии задачи сервер передаёт накопленное время (`elapsed_seconds`), и скрипт вызывает `setBaseTime()`.*

> `setBaseTime()` вызывается из шаблона `editor.html`, если студент до этого уже сохранял черновик — таким образом время суммируется.

### 2.2. Сохранение черновика (`editor2.js`)
```javascript
const elapsed = (typeof getSessionSeconds === 'function') ? getSessionSeconds() : 0;

$.ajax({
  url: '/api/tasks/<id>/draft/',
  method: 'POST',
  data: JSON.stringify({ code: content, elapsed }),
  ...
});
```
Только разница текущей сессии («сколько наросло») уходит на сервер.

### 2.3. Отправка решения (`editor2.js`)
Аналогично добавляет `elapsed` в `create_solution`.

---

## 3. Сервер: суммирование и проверка минимального времени

### 3.1. Черновик  
`app/tasks/api/views/draft.py`
```python
draft.time_spent = F('time_spent') + elapsed
draft.save(update_fields=['time_spent'])
```

### 3.2. Финальное решение  
`app/tasks/api/views/base.py → BaseTaskItemViewSet.create_solution`
```python
total_time = draft_time + elapsed
min_time   = task.min_duration.total_seconds() or 60

solution.time_spent         = total_time
solution.needs_manual_check = total_time < min_time
```
> **Логика:** если решение быcтрее порога — проставляем `needs_manual_check`, но всё равно считаем его «успешным».

---

## 4. Показ времени и «?» преподавателю

### 4.1. Статистика группы  
`src/app/groups/services/group_statistics.py`
```python
cell['execution_time']    = int(solution.time_spent or 0)
cell['needs_manual_check'] = solution.needs_manual_check
```

### 4.2. JS‑таблица (`static/js/group_course24.js`)
```javascript
if (isTeacher && data.execution_time > 0) {
  td.title += `\nВремя: ${format(data.execution_time)}`;
}
if (isTeacher && data.needs_manual_check && !underReview) {
  cell.textContent = '?';
  td.classList.add('s-orange');   // оранжевая ячейка
}
```
*`isTeacher` приходит из API (`resp.is_teacher`) — студенты этих данных не видят.*

> **Важно:** если решение ещё на проверке (`underReview = true`), то знак вопроса `?` не ставится — даже при быстром выполнении.

### 4.3. Шаблон решения для преподавателя  
`src/app/templates/tasks/solution/template.html`
```django
{% if object.time_spent %}
  <p><strong>Время:</strong> {{ object.time_spent|duration_hm }}</p>
{% endif %}
{% if object.needs_manual_check %}
  <p class="text-warning">❓ Решение получено слишком быстро, требуется проверка.</p>
{% endif %}
```
*Фильтр `duration_hm` определён в `app/tasks/templatetags/time_filters.py`.*

---

## 5. CSS (`static/css/style29.css`)
```css
.s-orange { background-color:#f4863c !important; }
```
В тёмной теме аналогично.
```css
html.dark-mode body .s-orange { background-color: #9c7d20 !important; }
```
---

## 6. Утилита для форматирования времени

Файл `time_filters.py` реализует фильтр:

```python
from django import template

register = template.Library()

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
Этот фильтр используется:

   - в шаблоне решения задачи (template.html),
   - и может применяться для отображения `solution.time_spent` в любом другом месте.

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

