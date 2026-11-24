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
            "FehuMedia Timelapse Filter Tool (Smart Day Detection)\n\n"
            "Groups timelapse images into logical days based on shooting gaps (nights)\n"
            "and extracts specific frames by index or relative time.\n"
            "Perfect for cameras with incorrect or drifted internal clocks."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("inputs", nargs="+", help="One or more image files or directories.")
    parser.add_argument("-o", "--out-dir", help="Output directory.")
    parser.add_argument("-n", "--index", type=int, help="Frame index (1-based) from start/end of the day.")
    parser.add_argument("--position", choices=["start", "end"], help="Take frame from 'start' or 'end'.")
    parser.add_argument("-t", "--time-hour", type=int, help="Target logical hour (0-23) relative to day start.")
    parser.add_argument("--tolerance", type=int, help="Maximum deviation in minutes for time matching.")
    parser.add_argument("-p", "--prefix", action="store_true", default=None, help="Enable smart 'YYYYMMDD_HHMMSS_' renaming.")
    parser.add_argument("--gap-hours", type=float, help="Gap in hours between frames to consider it a night.")
    parser.add_argument("--ask-difficult-questions", action="store_true", help="Enable interactive mode.")

    args = parser.parse_args()

    # Сбор всех файлов
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
        print("[!] No valid image files found.", file=sys.stderr)
        sys.exit(1)

    # Инициализация значений: приоритет аргументам, иначе дефолты
    gap_hours = args.gap_hours if args.gap_hours is not None else 3.0
    
    # Определение режима по умолчанию
    if args.time_hour is not None:
        filter_mode = "hour"
    elif args.index is not None:
        filter_mode = "index"
    else:
        filter_mode = "index"

    index = args.index if args.index is not None else 1
    position = args.position if args.position is not None else "start"
    time_hour = args.time_hour if args.time_hour is not None else 12
    tolerance = args.tolerance if args.tolerance is not None else 30
    use_prefix = args.prefix if args.prefix is not None else False

    first_input = args.inputs[0].rstrip('/')
    target_dir = args.out_dir if args.out_dir else f"{first_input}_filter"

    # Интерактивный режим (Трудные вопросы) с проверкой заданных опций
    if args.ask_difficult_questions:
        print(f"\n[?] Entering Interactive Configuration Mode:")
        
        # 0. Вопрос про ночную паузу (только если не задан --gap-hours)
        if args.gap_hours is None:
            gap_input = input(f"Enter night gap in hours (detect days by camera inactivity) [default: {gap_hours}]: ").strip()
            if gap_input:
                try: gap_hours = float(gap_input)
                except ValueError: print(f"  [!] Invalid value. Using default: {gap_hours}")

        # 1. Выбор режима фильтрации (только если не заданы жестко -t или -n)
        if args.time_hour is None and args.index is None:
            mode_input = input(f"Select filter mode (index / hour) [default: {filter_mode}]: ").strip().lower()
            if mode_input in ["index", "hour"]:
                filter_mode = mode_input

        # Спрашиваем параметры конкретного режима, если они не были переданы аргументами
        if filter_mode == "index":
            time_hour = None  # В режиме индекса сбрасываем часы
            if args.index is None:
                idx_input = input(f"  Enter frame index (1-based) [default: {index}]: ").strip()
                if idx_input:
                    try: index = int(idx_input)
                    except ValueError: print(f"  [!] Invalid number. Using default: {index}")
            if args.position is None:
                pos_input = input(f"  Enter position (start / end) [default: {position}]: ").strip().lower()
                if pos_input in ["start", "end"]: position = pos_input
        else:
            index = None  # В режиме часов сбрасываем индекс
            if args.time_hour is None:
                hour_input = input(f"  Enter target logical hour (0-23) [default: {time_hour}]: ").strip()
                if hour_input:
                    try: time_hour = int(hour_input)
                    except ValueError: print(f"  [!] Invalid hour. Using default: {time_hour}")
            if args.tolerance is None:
                tol_input = input(f"  Enter tolerance in minutes [default: {tolerance}]: ").strip()
                if tol_input:
                    try: tolerance = int(tol_input)
                    except ValueError: print(f"  [!] Invalid tolerance. Using default: {tolerance}")

        # 2. Вопрос про префикс переименования (только если флаг -p не указан явно)
        if args.prefix is None:
            pref_input = input(f"Enable smart date_time prefix? [y/N]: ").strip().lower()
            use_prefix = pref_input == 'y'

        # 3. Вопрос про выходную директорию (только если не задан -o)
        if args.out_dir is None:
            dir_input = input(f"Enter output directory path [default: {target_dir}]: ").strip()
            if dir_input: target_dir = dir_input.strip("'\"")

    # Финальная валидация на случай взаимоисключающих аргументов из CLI без интерактива
    if args.index is not None and args.time_hour is not None:
        print("[!] Error: Cannot use both --index (-n) and --time-hour (-t) filters at the same time.", file=sys.stderr)
        sys.exit(1)

    if index is not None and index < 1:
        print("[!] Index must be 1 or greater.", file=sys.stderr)
        sys.exit(1)

    if time_hour is not None and not (0 <= time_hour <= 23):
        print("[!] Time hour must be between 0 and 23.", file=sys.stderr)
        sys.exit(1)

    # Шаг 1: Извлекаем даты и сортируем ВЕСЬ поток хронологически
    print(f"\n[i] Reading timestamps for {len(input_paths)} files...")
    all_frames = []
    for path in input_paths:
        dt = get_file_datetime(path)
        if dt:
            all_frames.append((path, dt))
    
    all_frames.sort(key=lambda x: x)

    # Шаг 2: Разбиваем на логические дни на основе пауз (ночей)
    print(f"[i] Detecting logical days (Night gap threshold: {gap_hours} hours)...")
    logical_days = []
    
    if all_frames:
        current_day = [all_frames[0]]
        for i in range(1, len(all_frames)):
            prev_path, prev_dt = all_frames[i-1]
            curr_path, curr_dt = all_frames[i]
            
            if (curr_dt - prev_dt) > timedelta(hours=gap_hours):
                logical_days.append(current_day)
                current_day = [all_frames[i]]
            else:
                current_day.append(all_frames[i])
        logical_days.append(current_day)

    print(f"[i] Successfully identified {len(logical_days)} logical days of camera activity.")
    os.makedirs(target_dir, exist_ok=True)

    print(f"Output directory: {target_dir}")
    if index is not None:
        print(f"Filter profile: Frame #{index} from the '{position}' of each day.\n")
    else:
        print(f"Filter profile: Closest frame to {time_hour:02d}:00 logical offset (Tolerance: {tolerance} min).\n")

    # Шаг 3: Фильтрация внутри каждого логического дня
    copied_count = 0
    
    for day_idx, day_frames in enumerate(logical_days, start=1):
        total_frames = len(day_frames)
        first_frame_dt = day_frames[0][1]
        day_label = f"Day {day_idx:02d} ({first_frame_dt.strftime('%Y-%m-%d')})"
        
        target_frame = None

        if index is not None:
            if position == "start":
                t_idx = index - 1
                if t_idx < total_frames: target_frame = day_frames[t_idx]
            else:
                t_idx = -index
                if abs(t_idx) <= total_frames: target_frame = day_frames[t_idx]
        
        elif time_hour is not None:
            day_start_dt = day_frames[0][1]
            target_dt = day_start_dt + timedelta(hours=time_hour)
            
            best_frame = None
            min_diff = timedelta.max

            for file_path, file_dt in day_frames:
                diff = abs(file_dt - target_dt)
                if diff < min_diff:
                    min_diff = diff
                    best_frame = (file_path, file_dt)

            if best_frame and min_diff <= timedelta(minutes=tolerance):
                target_frame = best_frame

        # Копирование выбранного кадра
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
                status = f"offset +{time_hour}h" if time_hour is not None else f"index #{index}"
                print(f" [✓] {day_label}: Extracted {orig_name} ({status}, total frames: {total_frames})")
                copied_count += 1
            except Exception as e:
                print(f" [!] {day_label}: Failed to copy {orig_name}: {e}", file=sys.stderr)
        else:
            if index is not None:
                print(f" [i] {day_label}: Skipped (Only has {total_frames} frames)")
            else:
                print(f" [i] {day_label}: Skipped (No frame around layout offset +{time_hour}h within tolerance)")
                print(f"\n[✓] Filtering complete. Copied {copied_count} files to '{target_dir}'.")

if __name__ == "main":
    main()
