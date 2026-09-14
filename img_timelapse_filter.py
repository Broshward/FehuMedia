#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
from datetime import datetime

def get_file_datetime(file_path):
    """
    Получает дату и время создания/изменения файла.
    Для RAW-файлов надежнее использовать mtime, так как чтение EXIF 
    из проприетарных RAW (CR2, NEF, ARW) требует сторонних тяжелых библиотек.
    """
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"[!] Error reading time for {file_path}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(
        description=(
            "FehuMedia Timelapse Filter Tool\n\n"
            "Groups timelapse images by day and extracts the N-th frame from the "
            "beginning or end of each day into a separate folder."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("source_dir", help="Directory containing the RAW files")
    parser.add_argument("output_dir", help="Directory where selected frames will be copied")
    parser.add_argument("-n", "--index", type=int, default=1, help="Frame index (1-based). Default is 1.")
    parser.add_argument(
        "-p", "--position", 
        choices=["start", "end"], 
        default="start", 
        help="Take N-th frame from the 'start' (morning) or 'end' (evening) of the day. Default is 'start'."
    )

    args = parser.parse_args()

    if not os.path.isdir(args.source_dir):
        print(f"[!] Source directory not found: {args.source_dir}", file=sys.stderr)
        sys.exit(1)

    if args.index < 1:
        print("[!] Index must be 1 or greater.", file=sys.stderr)
        sys.exit(1)

    # Шаг 1: Сканируем файлы и группируем их по дням
    print(f"[i] Scanning directory: {args.source_dir}...")
    days_dict = {} # Структура: { "YYYY-MM-DD": [ (path, datetime_obj), ... ] }

    # Поддерживаемые расширения (можно дополнить вашими RAW-форматами)
    raw_extensions = ('.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.rw2', '.jpg', '.jpeg', '.raw')

    for entry in os.scandir(args.source_dir):
        if entry.is_file() and entry.name.lower().endswith(raw_extensions):
            dt = get_file_datetime(entry.path)
            if dt:
                day_key = dt.strftime("%Y-%m-%d")
                if day_key not in days_dict:
                    days_dict[day_key] = []
                days_dict[day_key].append((entry.path, dt))

    if not days_dict:
        print("[!] No matching image files found.", file=sys.stderr)
        sys.exit(1)

    print(f"[i] Found images spread across {len(days_dict)} individual days.")

    # Создаем целевую папку, если её нет
    os.makedirs(args.output_dir, exist_ok=True)

    # Шаг 2: Фильтруем и копируем N-й кадр для каждого дня
    copied_count = 0
    total_days = len(days_dict)
    
    # Сортируем дни хронологически
    sorted_days = sorted(days_dict.keys())

    print(f"[i] Extracting frame #{args.index} from the {args.position} of each day...")

    for day_key in sorted_days:
        # Сортируем кадры внутри одного дня по времени съемки
        frames = sorted(days_dict[day_key], key=lambda x: x[1])
        total_frames_in_day = len(frames)

        # Выбираем нужный кадр в зависимости от позиции
        target_frame = None
        if args.position == "start":
            # С начала дня (1-й кадр имеет индекс 0 в массиве)
            target_idx = args.index - 1
            if target_idx < total_frames_in_day:
                target_frame = frames[target_idx]
        else:
            # С конца дня (1-й с конца имеет индекс -1 в массиве)
            target_idx = -args.index
            if abs(target_idx) <= total_frames_in_day:
                target_frame = frames[target_idx]

        if target_frame:
            file_path, file_dt = target_frame
            file_name = os.path.name = os.path.basename(file_path)
            
            # Конструируем новое имя файла, чтобы они красиво сортировались по датам в новой папке
            # Пример: 2026-05-12_14-30-00_IMG_0001.CR2
            time_prefix = file_dt.strftime("%Y%m%d_%H%M%S_")
            new_file_name = f"{time_prefix}{file_name}"
            dest_path = os.path.join(args.output_dir, new_file_name)

            try:
                # copy2 сохраняет оригинальное время файла (mtime)
                shutil.copy2(file_path, dest_path)
                print(f"  [✓] {day_key}: Extracted {file_name} (Total frames today: {total_frames_in_day})")
                copied_count += 1
            except Exception as e:
                print(f"  [!] {day_key}: Failed to copy {file_name}: {e}", file=sys.stderr)
        else:
            print(f"  [i] {day_key}: Skipped (Only has {total_frames_in_day} frames, cannot get #{args.index})")

    print(f"\n[✓] Filtering complete. Copied {copied_count} files to '{args.output_dir}'.")

if __name__ == "__main__":
    main()
