#!/usr/bin/env python3
"""
Восстановление проекта из JSON-экспорта диалога Qwen.

Скрипт парсит JSON-файл диалога, извлекает все файлы с их путями и содержимым,
создает структуру папок и файлов в текущей директории, затем проверяет целостность.

Использование:
    python restore_project.py [путь_к_json]
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

DEFAULT_JSON_PATH = "chat-export-1782395371788.json"
BASE_DIR = Path(".")

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

def log(msg: str, color: str = ""):
    print(f"{color}{msg}{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# ПАРСИНГ JSON
# ═══════════════════════════════════════════════════════════════

def load_chat_history(json_path: str) -> List[dict]:
    """Загружает JSON-файл и извлекает все сообщения ассистента."""
    path = Path(json_path)
    if not path.exists():
        log(f"❌ Файл не найден: {json_path}", Colors.RED)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # JSON может быть списком или объектом
    messages = []
    
    if isinstance(data, list):
        # Формат: список чатов
        for item in data:
            if isinstance(item, dict) and "chat" in item:
                chat = item["chat"]
                if "history" in chat and "messages" in chat["history"]:
                    messages.extend(chat["history"]["messages"].values())
    elif isinstance(data, dict):
        # Формат: один чат
        if "chat" in data and "history" in data["chat"]:
            messages = list(data["chat"]["history"]["messages"].values())
        elif "messages" in data:
            messages = list(data["messages"].values())

    log(f"📂 Загружено {len(messages)} сообщений из {json_path}", Colors.CYAN)
    return messages


def extract_files_from_messages(messages: List[dict]) -> Dict[str, str]:
    """
    Извлекает файлы из сообщений ассистента.
    
    Ищет в content_list объекты с phase="answer", затем парсит:
    #### `путь/к/файлу`
    ```язык
    содержимое
    ```
    """
    files = {}
    
    # Паттерн для заголовка файла: #### `путь/к/файлу`
    file_header_pattern = re.compile(
        r"####\s+`([^`]+)`\s*\n",
        re.MULTILINE
    )
    
    # Паттерн для блока кода
    code_block_pattern = re.compile(
        r"```(?:\w+)?\s*\n(.*?)```",
        re.DOTALL
    )

    for msg in messages:
        # Проверяем роль ассистента
        if msg.get("role") != "assistant":
            continue
        
        # Извлекаем контент из content_list
        content_list = msg.get("content_list", [])
        if not content_list:
            # Fallback: проверяем поле content
            content = msg.get("content", "")
            if content:
                content_list = [{"content": content, "phase": "answer"}]
        
        for item in content_list:
            # Ищем только фазу "answer" (основной ответ)
            if item.get("phase") != "answer":
                continue
            
            content = item.get("content", "")
            if not content:
                continue
            
            # Находим все заголовки файлов
            for match in file_header_pattern.finditer(content):
                file_path = match.group(1).strip()
                start_pos = match.end()
                
                # Ищем блок кода после заголовка
                remaining = content[start_pos:]
                code_match = code_block_pattern.search(remaining)
                
                if code_match:
                    file_content = code_match.group(1)
                    
                    # Убираем один уровень отступов, если он есть
                    lines = file_content.split("\n")
                    if lines and lines[0].strip() == "":
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "":
                        lines = lines[:-1]
                    
                    # Проверяем общий отступ
                    if lines:
                        min_indent = min(
                            (len(line) - len(line.lstrip()) for line in lines if line.strip()),
                            default=0
                        )
                        if min_indent > 0:
                            lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]
                    
                    file_content = "\n".join(lines)
                    
                    # Сохраняем (перезаписываем если уже есть - берем последнюю версию)
                    files[file_path] = file_content

    log(f"📄 Найдено {len(files)} уникальных файлов", Colors.GREEN)
    return files


# ═══════════════════════════════════════════════════════════════
# СОЗДАНИЕ ФАЙЛОВ
# ═══════════════════════════════════════════════════════════════

def create_files(files: Dict[str, str]) -> Tuple[int, int, List[str]]:
    """Создает файлы на диске."""
    created = 0
    errors = 0
    error_list = []

    log("\n" + "=" * 60, Colors.BLUE)
    log(" СОЗДАНИЕ ФАЙЛОВ", Colors.BLUE)
    log("=" * 60, Colors.BLUE)

    # Сортируем: сначала корневые файлы, потом по алфавиту
    sorted_files = sorted(files.keys(), key=lambda p: (p.count("/"), p))

    for file_path in sorted_files:
        content = files[file_path]
        full_path = BASE_DIR / file_path

        try:
            # Создаем директории
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Записываем файл
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            size = full_path.stat().st_size
            log(f"  ✓ {file_path} ({size:,} байт)", Colors.GREEN)
            created += 1

        except Exception as e:
            log(f"  ✗ {file_path}: {e}", Colors.RED)
            errors += 1
            error_list.append(f"{file_path}: {e}")

    return created, errors, error_list


# ═══════════════════════════════════════════════════════════════
# ПРОВЕРКА ФАЙЛОВ
# ═══════════════════════════════════════════════════════════════

def verify_files(files: Dict[str, str]) -> Tuple[int, int, List[str]]:
    """Проверяет целостность созданных файлов."""
    verified = 0
    errors = 0
    error_list = []

    log("\n" + "=" * 60, Colors.BLUE)
    log("🔍 ПРОВЕРКА ФАЙЛОВ", Colors.BLUE)
    log("=" * 60, Colors.BLUE)

    for file_path, expected_content in files.items():
        full_path = BASE_DIR / file_path

        # 1. Проверка существования
        if not full_path.exists():
            log(f"  ✗ {file_path}: ФАЙЛ НЕ СУЩЕСТВУЕТ", Colors.RED)
            errors += 1
            error_list.append(f"{file_path}: не существует")
            continue

        # 2. Проверка размера
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                actual_content = f.read()
        except Exception as e:
            log(f"  ✗ {file_path}: ОШИБКА ЧТЕНИЯ - {e}", Colors.RED)
            errors += 1
            error_list.append(f"{file_path}: ошибка чтения")
            continue

        # 3. Проверка содержимого
        if actual_content == expected_content:
            size = len(actual_content.encode("utf-8"))
            lines = actual_content.count("\n") + 1
            log(f"  ✓ {file_path} ({size:,} байт, {lines} строк) — OK", Colors.GREEN)
            verified += 1
        else:
            # Подсчет различий
            expected_lines = expected_content.split("\n")
            actual_lines = actual_content.split("\n")
            diff_count = sum(
                1 for i in range(min(len(expected_lines), len(actual_lines)))
                if expected_lines[i] != actual_lines[i]
            )
            diff_count += abs(len(expected_lines) - len(actual_lines))

            log(f"  ⚠ {file_path}: РАСХОЖДЕНИЕ ({diff_count} строк)", Colors.YELLOW)
            errors += 1
            error_list.append(f"{file_path}: содержимое не совпадает ({diff_count} строк)")

    return verified, errors, error_list


# ═══════════════════════════════════════════════════════════════
# СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

def print_statistics(files: Dict[str, str], created: int, verified: int, errors: int):
    """Выводит итоговую статистику."""
    log("\n" + "=" * 60, Colors.CYAN)
    log("📊 СТАТИСТИКА", Colors.CYAN)
    log("=" * 60, Colors.CYAN)

    # Группировка по типу
    by_extension = defaultdict(int)
    by_directory = defaultdict(int)
    total_size = 0

    for file_path, content in files.items():
        ext = Path(file_path).suffix or "(без расширения)"
        by_extension[ext] += 1

        parts = Path(file_path).parts
        top_dir = parts[0] if len(parts) > 1 else "(корень)"
        by_directory[top_dir] += 1

        total_size += len(content.encode("utf-8"))

    log(f"\n{Colors.BOLD}Всего файлов:{Colors.END} {len(files)}", Colors.CYAN)
    log(f"{Colors.BOLD}Создано:{Colors.END} {created}", Colors.GREEN)
    log(f"{Colors.BOLD}Проверено:{Colors.END} {verified}", Colors.GREEN)
    log(f"{Colors.BOLD}Ошибок:{Colors.END} {errors}", Colors.RED if errors else Colors.GREEN)
    log(f"{Colors.BOLD}Общий размер:{Colors.END} {total_size:,} байт ({total_size / 1024:.1f} KB)", Colors.CYAN)

    log(f"\n{Colors.BOLD}📁 По директориям:{Colors.END}", Colors.CYAN)
    for dir_name, count in sorted(by_directory.items(), key=lambda x: -x[1]):
        log(f"  • {dir_name}: {count} файлов", Colors.CYAN)

    log(f"\n{Colors.BOLD}📄 По типам файлов:{Colors.END}", Colors.CYAN)
    for ext, count in sorted(by_extension.items(), key=lambda x: -x[1])[:10]:
        log(f"  • {ext}: {count}", Colors.CYAN)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    log("\n" + "=" * 60, Colors.BOLD)
    log("🚀 ВОССТАНОВЛЕНИЕ ПРОЕКТА ИЗ ДИАЛОГА", Colors.BOLD)
    log("=" * 60, Colors.BOLD)

    # Путь к JSON
    json_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JSON_PATH
    log(f"\n📂 JSON файл: {json_path}", Colors.CYAN)
    log(f"📁 Целевая директория: {BASE_DIR.absolute()}", Colors.CYAN)

    # 1. Загрузка и парсинг
    messages = load_chat_history(json_path)
    files = extract_files_from_messages(messages)

    if not files:
        log("\n❌ Файлы не найдены в диалоге!", Colors.RED)
        log("\n💡 Возможные причины:", Colors.YELLOW)
        log("  • JSON-файл имеет другую структуру", Colors.YELLOW)
        log("  • Файлы не были прикреплены к сообщениям", Colors.YELLOW)
        log("  • Формат заголовков файлов отличается от #### `путь`", Colors.YELLOW)
        
        # Выводим структуру первого сообщения для отладки
        if messages:
            log("\n🔍 Структура первого сообщения:", Colors.YELLOW)
            first_msg = messages[0]
            log(f"  Keys: {list(first_msg.keys())}", Colors.YELLOW)
            if "content_list" in first_msg:
                log(f"  content_list length: {len(first_msg['content_list'])}", Colors.YELLOW)
                if first_msg['content_list']:
                    log(f"  First item keys: {list(first_msg['content_list'][0].keys())}", Colors.YELLOW)
        
        sys.exit(1)

    # 2. Создание файлов
    created, create_errors, create_error_list = create_files(files)

    # 3. Проверка файлов
    verified, verify_errors, verify_error_list = verify_files(files)

    # 4. Статистика
    print_statistics(files, created, verified, verify_errors)

    # 5. Итог
    log("\n" + "=" * 60, Colors.BOLD)
    if verify_errors == 0:
        log("✅ ВСЕ ФАЙЛЫ СОЗДАНЫ И ПРОВЕРЕНЫ УСПЕШНО!", Colors.GREEN)
    else:
        log(f"⚠️  ОБНАРУЖЕНО {verify_errors} ПРОБЛЕМ", Colors.YELLOW)
        log("\nСписок проблем:", Colors.YELLOW)
        for err in verify_error_list[:20]:
            log(f"  • {err}", Colors.YELLOW)
        if len(verify_error_list) > 20:
            log(f"  ... и еще {len(verify_error_list) - 20}", Colors.YELLOW)
    log("=" * 60, Colors.BOLD)

    return 0 if verify_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())