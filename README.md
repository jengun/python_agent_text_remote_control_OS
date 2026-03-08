🤖 Tox Agent / Tox Assistant

RU:
Многофункциональный помощник для управления компьютером через мессенджер qTox (и другие, через настройку). Работает на Linux и Windows.

EN:
A multifunctional assistant for computer control via qTox messenger (and others, with configuration). Works on Linux and Windows.
✨ Возможности / Features

RU:

    ✅ Чтение сообщений из qTox через OCR (распознавание текста с экрана) — не требует API, не ломает шифрование

    ✅ Выполнение системных команд прямо из чата: !cmd status, !cmd time, !cmd run <команда>

    ✅ Автоматический ответ в тот же чат (обратная связь)

    ✅ Работает на Linux (Mint, Ubuntu, etc.) и Windows (через адаптацию под UI Automation)

    ✅ Динамическая настройка области захвата экрана под любой интерфейс

    ✅ Полная автономность: никаких внешних серверов, всё на вашем устройстве

EN:

    ✅ Reads messages from qTox via OCR (screen text recognition) — no API required, doesn't break encryption

    ✅ Executes system commands directly from chat: !cmd status, !cmd time, !cmd run <command>

    ✅ Automatically replies in the same chat (feedback loop)

    ✅ Works on Linux (Mint, Ubuntu, etc.) and Windows (via UI Automation adaptation)

    ✅ Dynamic screen area configuration — adapts to any UI

    ✅ Fully offline: no external servers, everything runs on your device

🖥️ Поддерживаемые команды / Available commands

RU:

    !cmd status — информация о системе (CPU, RAM, диск)

    !cmd time — текущее время

    !cmd uptime — время работы системы

    !cmd cpu — загрузка процессора

    !cmd mem — использование памяти

    !cmd disk — свободное место на дисках

    !cmd processes — список процессов

    !cmd ip — IP-адреса

    !cmd ports — открытые порты

    !cmd ping <host> — проверить доступность хоста

    !cmd ls <путь> — список файлов

    !cmd cat <файл> — просмотр файла

    !cmd find <имя> — поиск файлов

    !cmd weather — погода (по умолчанию Минск)

    !cmd run <команда> — выполнить любую команду (осторожно!)

    !cmd help — справка

EN:

    !cmd status — system info (CPU, RAM, disk)

    !cmd time — current time

    !cmd uptime — system uptime

    !cmd cpu — CPU load

    !cmd mem — memory usage

    !cmd disk — disk space

    !cmd processes — process list

    !cmd ip — IP addresses

    !cmd ports — open ports

    !cmd ping <host> — ping a host

    !cmd ls <path> — list files

    !cmd cat <file> — view file

    !cmd find <name> — search files

    !cmd weather — weather (Minsk by default)

    !cmd run <command> — execute any command (use with caution!)

    !cmd help — help

🚀 Быстрый старт / Quick start

RU:

    Установите Python 3, установите зависимости из requirements.txt

    Запустите qTox, откройте чат

    Отредактируйте в скрипте координаты области чата и поля ввода (получите их через xdotool на Linux или через pyautogui.position())

    Запустите агента: python tox_agent.py

    Отправьте из qTox !cmd help

EN:

    Install Python 3, install dependencies from requirements.txt

    Launch qTox, open a chat

    Edit the script to set correct coordinates for chat area and input field (get them via xdotool on Linux or pyautogui.position() on Windows)

    Run the agent: python tox_agent.py

    Send !cmd help from qTox

⚠️ Статус проекта / Project status

RU:
Проект находится в активной разработке. Версия 0.01 — proof of concept. Основной функционал работает, но интерфейс настройки и установщики пока в планах. Тестируется на Linux Mint и Windows 10. Приветствуются баг-репорты и идеи!

EN:
Project is under active development. Version 0.01 is a proof of concept. Core functionality works, but configuration interface and installers are planned. Tested on Linux Mint and Windows 10. Bug reports and ideas are welcome!
📦 Зависимости / Dependencies

    Python 3.6+

    pyautogui

    pytesseract

    PIL (Pillow)

    pynput

    Tesseract OCR (установить отдельно / install separately)
