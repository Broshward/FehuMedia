#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
from datetime import datetime, timedelta

def get_file_datetime(file_path):
    """
    Gets the modification date and time of the file.
    """
    try:
        timestamp = os.stat(file_path).st_mtime
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"[!] Error reading time for {file_path}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(
        description=(
            "FehuMedia Timelapse Filter Tool\n\n"
            "Groups timelapse images by day and extracts specific frames by index or target hour.\n"
            "Accepts multiple files and directories as input (SpaceFM %F compatible)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "inputs", 
        nargs="+", 
        help="One or more image files or directories containing images."
    )
    parser.add_argument(
        "-o", "--out-dir",
        help="Output directory. Default is the first input path with '_filter' suffix."
    )
    parser.add_argument(
        "-n", "--index", 
        type=int, 
        help="Frame index (1-based) from the start or end of the day."
    )
    parser.add_argument(
        "--position", 
        choices=["start", "end"], 
        default="start", 
        help="Take N-th frame from the 'start' (morning) or 'end' (evening) of the day. Default is 'start'."
    )
    parser.add_argument(
        "-t", "--time-hour", 
        type=int, 
        help="Target hour of the day (0-23) to extract (e.g., 12 or 18)."
    )
    parser.add_argument(
        "--tolerance", 
        type=int, 
        default=30, 
        help="Maximum allowed deviation in minutes from the target hour. Default is 30."
    )
    parser.add_argument(
        "-p", "--prefix", 
        action="store_true", 
        help="Enable smart renaming. Adds '%Y%m%d_%H%M%S_' prefix to the destination filename."
    )
    parser.add_argument(
        "--ask-difficult-questions", 
        action="store_true", 
        help="Enable interactive prompt mode for configuration."
    )

    args = parser.parse_args()

    # Сбор всех файлов из переданных аргументов (файлы напрямую + рекурсивно из папок)
    raw_extensions = ('.cr2', '.cr3', '.nef', '.arw', '.raw', '.dng', '.orf', '.rw2', '.jpg', '.jpeg')
    input_paths = []
    
    for item in args.inputs:
        if os.path.isfile(item) and item.lower().endswith(raw_extensions):
            input_paths.append(item)
        elif os.path.isdir(item):
            for root, _, files in os.walk(item):
                for f in files:
                    if f.lower().endswith(raw_extensions):
                        input_paths.append(os.path.join(root, f))

    if not input_paths:
        print("[!] No valid image files found in the provided inputs.", file=sys.stderr)
        sys.exit(1)

    # Значения по умолчанию для интерактива
    filter_mode = "hour" if args.time_hour is not None else "index"
    index = args.index if args.index is not None else 1
    position = args.position
    time_hour = args.time_hour if args.time_hour is not None else 12
    tolerance = args.tolerance
    use_prefix = args.prefix

    # Автоматическое определение выходной папки по умолчанию
    first_input = args.inputs[0].rstrip('/')
    default_out_dir = args.out_dir if args.out_dir else f"{first_input}_filter"
    target_dir = default_out_dir

    # Интерактивный режим (Трудные вопросы)
    if args.ask_difficult_questions:
        print(f"\n[?] Entering Interactive Configuration Mode for gathered files:")
        
        # 1. Выбор режима фильтрации
        mode_input = input(f"Select filter mode (index / hour) [default: {filter_mode}]: ").strip().lower()
        if mode_input in ["index", "hour"]:
            filter_mode = mode_input

        if filter_mode == "index":
            # Вопросы для режима индекса
            idx_input = input(f"  Enter frame index (1-based) [default: {index}]: ").strip()
            if idx_input:
                try:
                    index = int(idx_input)
                except ValueError:
                    print(f"  [!] Invalid number. Using default: {index}")
            
            pos_input = input(f"  Enter position (start / end) [default: {position}]: ").strip().lower()
            if pos_input in ["start", "end"]:
                position = pos_input
            time_hour = None  # Сбрасываем второй режим
        else:
            # Вопросы для режима часов
            hour_input = input(f"  Enter target hour (0-23) [default: {time_hour}]: ").strip()
            if hour_input:
                try:
                    time_hour = int(hour_input)
                except ValueError:
                    print(f"  [!] Invalid hour. Using default: {time_hour}")
            
            tol_input = input(f"  Enter tolerance in minutes [default: {tolerance}]: ").strip()
            if tol_input:
                try:
                    tolerance = int(tol_input)
                except ValueError:
                    print(f"  [!] Invalid tolerance. Using default: {tolerance}")
            index = None  # Сбрасываем первый режим

        # 2. Вопрос про префикс переименования
        pref_default = "y" if use_prefix else "n"
        pref_input = input(f"Enable smart date_time prefix? [y/N]: ").strip().lower()
        use_prefix = pref_input == 'y'

        # 3. Вопрос про выходную директорию
        dir_input = input(f"Enter output directory path [default: {target_dir}]: ").strip()
        if dir_input:
            target_dir = dir_input.strip("'\"")

    # Валидация параметров после интерактива/аргументов
    if index is None and time_hour is None:
        # Если запустили без флагов и без интерактива, ставим по умолчанию первый кадр дня
        index = 1

    if index is not None and index < 1:
        print("[!] Index must be 1 or greater.", file=sys.stderr)
        sys.exit(1)

    if time_hour is not None and not (0 <= time_hour <= 23):
        print("[!] Time hour must be between 0 and 23.", file=sys.stderr)
        sys.exit(1)

    # Шаг 1: Группировка по дням
    print(f"\n[i] Analyzing {len(input_paths)} files...")
    days_dict = {}

    for path in input_paths:
        dt = get_file_datetime(path)
        if dt:
            day_key = dt.strftime("%Y-%m-%d")
            if day_key not in days_dict:
                days_dict[day_key] = []
            days_dict[day_key].append((path, dt))

    print(f"[i] Found images spread across {len(days_dict)} individual days.")
    os.makedirs(target_dir, exist_ok=True)

    print(f"Output directory: {target_dir}")
    if index is not None:
        print(f"Filter profile: Frame #{index} from the '{position}' of each day.\n")
    else:
        print(f"Filter profile: Closest frame to {time_hour:02d}:00 (Tolerance: {tolerance} min).\n")

    # Шаг 2: Фильтрация и копирование
    copied_count = 0
    sorted_days = sorted(days_dict.keys())

    for day_key in sorted_days:
        frames = sorted(days_dict[day_key], key=lambda x: x[1])
        total_frames_in_day = len(frames)
        target_frame = None

        if index is not None:
            if position == "start":
                target_idx = index - 1
                if target_idx < total_frames_in_day:
                    target_frame = frames[target_idx]
            else:
                target_idx = -index
                if abs(target_idx) <= total_frames_in_day:
                    target_frame = frames[target_idx]
        
        elif time_hour is not None:
            year, month, day = map(int, day_key.split('-'))
            target_dt = datetime(year, month, day, time_hour, 0, 0)
            
            best_frame = None
            min_diff = timedelta.max

            for file_path, file_dt in frames:
                diff = abs(file_dt - target_dt)
                if diff < min_diff:
                    min_diff = diff
                    best_frame = (file_path, file_dt)

            if best_frame and min_diff <= timedelta(minutes=tolerance):
                target_frame = best_frame

        # Копирование результата
        if target_frame:
            file_path, file_dt = target_frame
            orig_name = os.path.basename(file_path)
            
            if use_prefix:
                time_prefix = file_dt.strftime("%Y%m%d_%H%M%S_")
                new_file_name = f"{time_prefix}{orig_name}"
            else:
                new_file_name = orig_name

            dest_path = os.path.join(target_dir, new_file_name)

            try:
                shutil.copy2(file_path, dest_path)
                status_msg = f"at {file_dt.strftime('%H:%M:%S')}" if time_hour is not None else f"index #{index}"
                print(f"  [✓] {day_key}: Extracted {orig_name} ({status_msg})")
                copied_count += 1
            except Exception as e:
                print(f"  [!] {day_key}: Failed to copy {orig_name}: {e}", file=sys.stderr)
        else:
            if index is not None:
                print(f"  [i] {day_key}: Skipped (Only has {total_frames_in_day} frames)")
            else:
                print(f"  [i] {day_key}: Skipped (No frames shot near {time_hour:02d}:00 within tolerance)")

    print(f"\n[✓] Filtering complete. Copied {copied_count} files to '{target_dir}'.")

if __name__ == "__main__":
    main()
