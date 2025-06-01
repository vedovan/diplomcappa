
# Таблица статистики курса: динамический фильтр, пересчёт баллов и оптимизации

## 1. Назначение и общий поток данных

Страница **`group_course.html`** показывает прогресс участников по всем заданиям курса.  
После доработок таблица умеет:

* **Фильтровать темы** — интерактивная панель скрывает/показывает столбцы заданий.
* **Пересчитывать** количество решённых задач и баллов «на лету».
* **Обновляться Live‑AJAX’ом** без перезагрузки.
* **Оптимизировать UI** — минимальные reflow, синхронизированный скролл.

Поток данных

```
GroupViewSet.statistics (Django) ─► GroupStatisticsService.get_course_statistics()
                                      │
                                      ▼
                                 JSON‑ответ
                                      │
                                      ▼
                        group_course24.js → updateTable() → DOM
```

---

## 2. Backend

### 2.1. `GroupStatisticsService.get_course_statistics`
`src/app/groups/services/group_statistics.py`

* Проверяет роль пользователя.
* Возвращает JSON:

```json
{
  "tasks_max_points": { "17": 5, "18": 4, "19": 10 },
  "stats": {
    "4": {               // user_id
      "17": {
        "score": 5,
        "is_solved": true,
        "execution_time": 42,
        "needs_manual_check": false,
        "score_method": "tests",
        "testing_score": 100,
        "review_status": "checked"
      }
    }
  },
  "is_teacher": true
}
```

* `execution_time` и `needs_manual_check` появляются только для **первой** успешной попытки.
* Результат кэшируется по `version_hash`, чтобы не нагружать БД.

### 2.2. Представление
`src/app/groups/api/views.py`

```python
class GroupViewSet(...):
    @action(methods=("GET",), detail=True)
    def statistics(self, request, *args, **kwargs):
        group = self.get_object()
        slz = StatisticsRequestSerializer(data=request.GET)
        slz.is_valid(raise_exception=True)

        data = GroupStatisticsService.get_course_statistics(
            group=group,
            course_id=slz.validated_data["course_id"],
            user=request.user
        )
        return Response(data)
```

---

## 3. Шаблон `group_course.html`

* Таблица изначально содержит только `<thead>` и строки пользователей в `<tbody>`.
* `data-api-url` у контейнера передаётся в JS.
* `<tfoot class="totals-row">` — строка «Всего» (баллы пересчитываются JS’ом).
* Пустой блок *topic‑filter* заполняет JavaScript.

---

## 4. Frontend – `static/js/group_course24.js`

### 4.1. Главное

```javascript
const tasksMaxPoints = resp.tasks_max_points;
const tasksMap       = { ...tasksMaxPoints }; // рабочая копия
```

| Переменная | Смысл |
|------------|-------|
| `tasksMap` | копия `tasksMaxPoints` для актуального подсчёта |
| `selectedTopics` | `Set` id‑тем, которые скрыты |
| `isTeacher` | роль пользователя |

### 4.2. Загрузка

```javascript
function loadStatistics() {
  showLoader();
  $.ajax({ url: API_URL, headers: AUTH_HEADER })
      .done(updateTable)
      .always(hideLoader);
}
```

### 4.3. `updateTable(resp)`

1. Парсит JSON; кэш не заводится — данные берутся прямо из `resp.stats`.
2. Создаёт `DocumentFragment`, заполняя `<tr>` пользователя.
3. Каждая ячейка получает текст (`✔`, `✖`, `?`, число), класс (`.s-green`, …) и `data-score`.
4. Считает решено / баллы и заполняет крайние колонки строки.
5. Вставляет фрагмент одним `appendChild` → минимальный reflow.
6. Вызывает `ensureTableStructure()` — добавляет пустые `<td>`, если появились новые задачи.
7. `buildTopicFilter()` (один раз), `applyTopicFilter()`, `syncFakeScrollbar()`.

### 4.4. Фильтр тем

```javascript
function buildTopicFilter() { /* строит чекбоксы, поиск */ }

function applyTopicFilter() {
  const showAll = selectedTopics.size === 0 || selectedTopics.has('all');
  // Toggle display у <th>/<td>
  recalcTotals();
  syncFakeScrollbar();
}
```

### 4.5. Пересчёт итогов

```javascript
function recalcTotals() {
  // проход по видимым td[data-score]
}
```

### 4.6. Синхронизация скролла

```javascript
function syncFakeScrollbar() {
  fakeTable.style.width = table.scrollWidth + 'px';
}
window.addEventListener('resize', () => {
  if (!resizePending) {
    resizePending = true;
    setTimeout(() => { syncFakeScrollbar(); resizePending = false; }, 100);
  }
});
```

---

## 5. Стили – `static/css/style29.css`

| Класс | Назначение |
|-------|------------|
| `.s-green`  | успешное решение |
| `.s-red`    | ошибка тестов |
| `.s-yellow` | частичные тесты |
| `.s-cyan`   | «на проверке» |
| `.s-orange` | слишком быстро (`?`) |
| `.topic-filter` | панель выбора тем |
| `.course__fake-table` | верхний синхронный скролл |

---

## 6. Оптимизации

1. **`DocumentFragment`** — массовое добавление строк без множества reflow.
2. **EnsureTableStructure()** — поддерживает одинаковую длину `<tr>` и `<thead>`.
3. **Throttling** на `resize` / `scroll` (`RESIZE_DELAY = 100 мс`).
4. **Ленивая инициализация** фильтра тем.

---

## 7. Полный список изменённых файлов

```
src/app/groups/templates/group_course.html
src/app/groups/services/group_statistics.py
src/app/groups/api/views.py          # метод statistics в GroupViewSet
src/static/js/group_course24.js
src/static/css/style29.css
```
