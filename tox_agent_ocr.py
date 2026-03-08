#!/usr/bin/env python3
"""
qTox Agent v0.1 - Полная версия с обратной связью
"""

import pyautogui
import time
import subprocess
import os
import logging
import re
from PIL import Image
import pytesseract

# ========== КООРДИНАТЫ ==========
# Область для чтения сообщений
CHAT_AREA = {
    'x': 1321,
    'y': 151,
    'width': 564,
    'height': 212
}

# Область для ввода ответов (поле ввода)
INPUT_AREA = {
    'x': 1328,
    'y': 373,
    'width': 493,
    'height': 53
}

COMMAND_PREFIX = "!cmd"
CHECK_INTERVAL = 2

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('tox_agent.log'),
        logging.StreamHandler()
    ]
)

# ========== БИБЛИОТЕКА КОМАНД ==========

COMMANDS = {
    # Информация о системе
    'status': 'uname -a; echo "=== CPU ==="; top -bn1 | grep "Cpu(s)"; echo "=== MEMORY ==="; free -h; echo "=== DISK ==="; df -h',
    'uptime': 'uptime',
    'cpu': 'top -bn1 | grep "Cpu(s)"',
    'mem': 'free -h',
    'disk': 'df -h',
    'processes': 'ps aux --sort=-%cpu | head -15',
    
    # Сеть
    'ip': "ip a | grep inet | grep -v inet6 | awk '{print $2}'",
    'ports': 'ss -tulpn | head -20',
    'connections': 'ss -tunp | head -15',
    'ping': 'ping -c 4 {}',
    
    # Файлы
    'ls': 'ls -la {}',
    'cat': 'cat {}',
    'find': 'find /home -name "{}" 2>/dev/null | head -10',
    
    # Прочее
    'weather': 'curl -s "wttr.in/Минск?format=%t+%c+%w" || echo "Нет связи"',
    'time': 'date "+%Y-%m-%d %H:%M:%S"',
    'help': 'справка'
}

def execute_command(cmd_name, args=""):
    """Выполняет команду по имени"""
    
    if cmd_name == "help":
        return help_text()
    
    if cmd_name not in COMMANDS:
        return f"Неизвестная команда: {cmd_name}\nДоступные: {', '.join(COMMANDS.keys())}"
    
    command = COMMANDS[cmd_name]
    
    # Подставляем аргументы, если команда их требует
    if "{}" in command:
        if not args:
            return f"Команда {cmd_name} требует аргумент (например: !cmd {cmd_name} значение)"
        command = command.format(args)
    
    logging.info(f"Выполняю: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout if result.stdout else ""
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        return output if output else "Команда выполнена, вывод пуст"
    except subprocess.TimeoutExpired:
        return "Ошибка: команда выполнялась слишком долго (>30 сек)"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def help_text():
    """Формирует справку"""
    text = "📋 Доступные команды:\n\n"
    commands_list = [
        ('status', 'Полная информация о системе'),
        ('uptime', 'Время работы'),
        ('cpu', 'Загрузка процессора'),
        ('mem', 'Использование памяти'),
        ('disk', 'Место на дисках'),
        ('processes', 'Топ процессов'),
        ('ip', 'IP-адреса'),
        ('ports', 'Открытые порты'),
        ('connections', 'Сетевые соединения'),
        ('ping <host>', 'Проверить доступность'),
        ('ls <путь>', 'Список файлов'),
        ('cat <файл>', 'Показать файл'),
        ('find <имя>', 'Поиск файлов'),
        ('weather', 'Погода'),
        ('time', 'Текущее время'),
        ('help', 'Эта справка'),
    ]
    for cmd, desc in commands_list:
        text += f"  !cmd {cmd:<15} - {desc}\n"
    return text

# ========== ФУНКЦИИ РАБОТЫ С ЭКРАНОМ ==========

def get_screen_area(x, y, width, height):
    """Снимок области экрана"""
    try:
        return pyautogui.screenshot(region=(x, y, width, height))
    except Exception as e:
        logging.error(f"Ошибка снимка: {e}")
        return None

def text_from_image(image):
    """OCR с агрессивной очисткой и поиском команд"""
    try:
        # Увеличиваем изображение для лучшего распознавания
        width, height = image.size
        image = image.resize((width*2, height*2), Image.Resampling.LANCZOS)
        
        # Конвертируем в оттенки серого
        gray = image.convert('L')
        
        # Увеличиваем контраст
        threshold = 120
        bw = gray.point(lambda x: 0 if x < threshold else 255, '1')
        
        # Распознаём текст
        text = pytesseract.image_to_string(
            bw, 
            lang='rus+eng',
            config='--psm 6'
        )
        
        # Очищаем, но сохраняем потенциальные команды
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            # Если строка содержит !cmd, обрабатываем бережно
            if '!cmd' in line.lower():
                # Сохраняем !cmd и то, что после него
                parts = line.lower().split('!cmd')
                if len(parts) > 1:
                    cmd = '!cmd' + parts[1]
                    # Очищаем только явный мусор
                    cmd = re.sub(r'[«»„“]', '', cmd)
                    clean_lines.append(cmd)
            else:
                # Обычные строки чистим сильнее
                clean = re.sub(r'[^\w\s]', '', line)
                clean = re.sub(r'\s+', ' ', clean).strip()
                if clean and len(clean) > 2:
                    clean_lines.append(clean)
        
        result = '\n'.join(clean_lines)
        logging.info(f"OCR очищен: {result[:100]}...")
        return result
        
    except Exception as e:
        logging.error(f"Ошибка OCR: {e}")
        return ""

# ========== ФУНКЦИИ ОТПРАВКИ ОТВЕТА ==========

def send_to_chat(text):
    """Печатает текст в поле ввода и отправляет"""
    try:
        logging.info("🖱️ Отправка ответа...")
        
        # Координаты центра поля ввода
        x = INPUT_AREA['x'] + INPUT_AREA['width'] // 2
        y = INPUT_AREA['y'] + INPUT_AREA['height'] // 2
        
        # Кликаем в поле ввода
        pyautogui.click(x, y)
        time.sleep(0.3)
        
        # Очищаем поле (на всякий случай)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # Разбиваем длинный текст на части
        max_len = 400
        chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
        
        for i, chunk in enumerate(chunks):
            # Печатаем часть текста
            pyautogui.write(chunk, interval=0.05)
            time.sleep(0.1)
            
            # Если это не последняя часть, добавляем маркер продолжения
            if i < len(chunks) - 1:
                pyautogui.write(" (продолжение следует...)")
                pyautogui.press('enter')
                time.sleep(0.5)
            else:
                pyautogui.press('enter')
        
        logging.info(f"✅ Отправлено {len(chunks)} частей")
        return True
        
    except Exception as e:
        logging.error(f"❌ Ошибка отправки: {e}")
        return False

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ИСТОРИЕЙ ==========

def save_last_text(text):
    """Сохраняет последний распознанный текст"""
    with open('last_chat.txt', 'w') as f:
        f.write(text)

def load_last_text():
    """Загружает последний распознанный текст"""
    try:
        with open('last_chat.txt', 'r') as f:
            return f.read()
    except:
        return ""

def is_new_message(old_text, new_text):
    """Проверяет, есть ли новые сообщения"""
    if not new_text:
        return False
    if not old_text:
        return True
    
    old_lines = set(line.strip() for line in old_text.split('\n') if line.strip())
    new_lines = set(line.strip() for line in new_text.split('\n') if line.strip())
    
    return len(new_lines - old_lines) > 0

def get_new_messages(old_text, new_text):
    """Умное выделение команд из шумного текста"""
    if not new_text:
        return []
    
    # Разбиваем на строки и чистим
    new_lines = []
    for line in new_text.split('\n'):
        # Убираем лишние символы, но сохраняем ! и буквы
        clean = re.sub(r'[^\w\s!]', '', line)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean and len(clean) > 3:  # не пустые и не слишком короткие
            new_lines.append(clean)
    
    if not new_lines:
        return []
    
    old_lines = []
    if old_text:
        for line in old_text.split('\n'):
            clean = re.sub(r'[^\w\s!]', '', line)
            clean = re.sub(r'\s+', ' ', clean).strip()
            if clean:
                old_lines.append(clean)
    
    # Ищем новые строки, которых не было
    result = []
    for line in new_lines:
        if line not in old_lines:
            # Проверяем, похоже ли это на команду (содержит !cmd)
            if '!cmd' in line.lower():
                result.append(line)
            # Или просто новое сообщение (для отладки)
            elif line and not any(word in line.lower() for word in ['typing', 'пишет']):
                result.append(line)
    
    return result

# ========== ГЛАВНЫЙ ЦИКЛ ==========

def main():
    logging.info("="*60)
    logging.info("🔥 qTox Agent v2.2 - Полная версия")
    logging.info("="*60)
    logging.info(f"Область чтения: x={CHAT_AREA['x']}, y={CHAT_AREA['y']}, w={CHAT_AREA['width']}, h={CHAT_AREA['height']}")
    logging.info(f"Область ввода: x={INPUT_AREA['x']}, y={INPUT_AREA['y']}, w={INPUT_AREA['width']}, h={INPUT_AREA['height']}")
    logging.info(f"Префикс команд: {COMMAND_PREFIX}")
    logging.info("="*60)
    
    # Задержка, чтобы пользователь успел переключиться на qTox
    logging.info("⏳ Запуск через 5 секунд... Переключитесь на окно qTox!")
    time.sleep(5)
    
    # Отправляем приветствие
    send_to_chat("🤖 Агент запущен и готов к работе! Отправьте !cmd help для списка команд.")
    
    last_text = load_last_text()
    logging.info(f"Загружено предыдущее состояние, {len(last_text)} символов")
    
    try:
        while True:
            # 1. Читаем область чата
            screen = get_screen_area(
                CHAT_AREA['x'],
                CHAT_AREA['y'],
                CHAT_AREA['width'],
                CHAT_AREA['height']
            )
            
            if screen:
                current_text = text_from_image(screen)
                
                if current_text and is_new_message(last_text, current_text):
                    new_msgs = get_new_messages(last_text, current_text)
                    
                    for msg in new_msgs:
                        logging.info(f"📨 Получено: {msg[:80]}...")
                        
                        # Проверяем, является ли сообщение командой
                        if msg.startswith(COMMAND_PREFIX):
                            # Разбираем команду и аргументы
                            full_cmd = msg[len(COMMAND_PREFIX):].strip()
                            parts = full_cmd.split(maxsplit=1)
                            cmd_name = parts[0].lower()
                            args = parts[1] if len(parts) > 1 else ""
                            
                            logging.info(f"⚡ Обнаружена команда: {cmd_name}")
                            
                            # Выполняем команду
                            result = execute_command(cmd_name, args)
                            
                            # Отправляем результат
                            response = f"🤖 Результат команды {cmd_name}:\n\n{result}"
                            send_to_chat(response)
                    
                    # Сохраняем текущее состояние
                    save_last_text(current_text)
                    last_text = current_text
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logging.info("🛑 Программа остановлена пользователем")
        send_to_chat("🤖 Агент остановлен")
    except Exception as e:
        logging.error(f"💥 Критическая ошибка: {e}")
        send_to_chat(f"😱 Ошибка: {str(e)[:200]}")

if __name__ == "__main__":
    main()
