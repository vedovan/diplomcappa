
# Документация: Автоматическое встраивание видео

## Назначение
`embed_video_in_text` — пользовательский фильтр Django, который автоматически превращает ссылки на **YouTube**, **Google Drive**, **RuTube** и **ВКонтакте‑Видео** в адаптивные `<iframe>`‑блоки.  
Фильтр упрощает размещение видео в текстах новостей, тем курсов и условиях задач: автору достаточно вставить URL‑ссылку, при необходимости добавив тег выравнивания.

## Расположение
```
templatetags/embed_video.py
```

## Структура модуля

* **Импорт модулей**
  ```python
  from django import template
  from django.utils.safestring import mark_safe
  import re
  ```
* **Регистрация фильтра**
  ```python
  register = template.Library()
  ```
* **Определение фильтра**
  ```python
  @register.filter
  def embed_video_in_text(text):
      ...
  ```

### Логика работы
1. Фильтр ищет в тексте ссылки четырёх видеоплатформ при помощи регулярных выражений.
2. Если перед ссылкой стоит тег  
   ```
   [video-left]   [video-right]   [video-center]
   ```  
   выбранное значение влияет на выравнивание блока. Без тега применяется `center`.
3. Каждая подходящая ссылка заменяется на HTML‑фрагмент
   ```html
   <div class="video-wrapper video-center">
       <iframe class="video-center" src="…" allowfullscreen></iframe>
   </div>
   ```
4. `mark_safe()` гарантирует, что сгенерированный HTML не будет экранирован.

---

## Изменённые шаблоны
`training/parts/content_text.html`
```
    {{ obj.text|embed_video_in_text|safe }}
```
`news/card_vertical.html`  и  `news/card_horizontal.html`
```
    {{ item.text|embed_video_in_text|safe }}
```
`tasks/templates/template.html`
```
    {{ task.text|embed_video_in_text|safe }}
```

---

## CSS (static/css/style29.css)
```css
.video-wrapper{position:relative;width:100%;max-width:640px;aspect-ratio:16/9;}
.video-wrapper.video-left {float:left;  margin:1em 1.5em 1em 0;}
.video-wrapper.video-right{float:right; margin:1em 0 1em 1.5em;}
.video-wrapper.video-center{margin:2em auto; float:none;}
.video-wrapper iframe      {position:absolute;top:0;left:0;width:100%;height:100%;border:none;}
```

---

## Пример использования

```
[video-left] https://youtu.be/dQw4w9WgXcQ
[video-right] https://vk.com/video12345_67890
https://rutube.ru/video/abc123456/
https://drive.google.com/file/d/1abcDEFghIJKlmNOP/view
```

---
