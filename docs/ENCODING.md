# Astro CLI - Помощник по кодировке

## Проблема с отображением Unicode символов в Windows

Если вы видите вместо красивых таблиц и символов что-то вроде:
```
Γöé╨│╨░╤Ç╨╝╨╛╨╜. ΓöéminorΓöé
```

## Решение

### Вариант 1: Установить кодировку в текущей сессии PowerShell

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
```

После этого запускайте команды как обычно:
```powershell
python main.py transit 1982-01-08 09:40 Saratov --max-orb 1
```

### Вариант 2: Установить UTF-8 через chcp (проще, но работает хуже с пайпами)

```powershell
chcp 65001
python main.py transit 1982-01-08 09:40 Saratov
```

### Вариант 3: Установить кодировку автоматически в профиле PowerShell

Добавьте в файл `$PROFILE` (обычно `~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`):

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
```

Это установит UTF-8 при каждом запуске PowerShell.

### Вариант 4: Использовать Windows Terminal (рекомендуется)

Windows Terminal (современная замена PowerShell) по умолчанию использует UTF-8 и корректно отображает все символы.

Скачать: https://aka.ms/terminal

## Проверка текущей кодировки

```powershell
# Проверить кодовую страницу консоли
chcp

# Проверить кодировку Python
python -c "import sys; print(sys.stdout.encoding)"

# Проверить кодировку PowerShell
$OutputEncoding
```

## Примеры правильного вывода

С правильной кодировкой вы должны видеть:

```
🌟 ТРАНЗИТЫ К НАТАЛЬНОЙ КАРТЕ (25)
┌───────────────┬────────────┬───────────────┬────────┬────────┬────────┐
│Транзит        │Аспект      │Натальная      │Орб     │Тип     │Категория│
├───────────────┼────────────┼───────────────┼────────┼────────┼────────┤
│Mercury        │△ trine     │North Node     │0.30°   │гармон. │major   │
│Proserpina     │⚺ semisextile│Neptune        │0.42°   │гармон. │minor   │
│Proserpina     │⚻ quincunx  │Moon           │0.43°   │напряж. │minor   │
└───────────────┴────────────┴───────────────┴────────┴────────┴────────┘
```

С символами:
- `┌ ┬ ┐ ├ ┼ ┤ └ ┴ ┘ │ ─` - Unicode box-drawing
- `☉ ☽ ☿ ♀ ♂ ♃ ♄` - планеты
- `☌ ☍ △ □ ✶ ⚻ ⚺` - аспекты
- `♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓` - знаки зодиака
- `🌟 📊 🌍 📅 📍` - эмодзи

## Альтернатива: отключить цвета и Unicode

Если не удается настроить кодировку, можно использовать упрощенный вывод:

```powershell
python main.py transit 1982-01-08 09:40 Saratov --no-color
```

Или использовать JSON формат:
```powershell
python main.py natal 1982-01-08 09:40 Saratov --format json
```
