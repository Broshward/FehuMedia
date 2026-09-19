#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import shutil

def get_image_mean_brightness(image_path):
    """
    Returns the mean brightness of the image (from 0.0 to 1.0) using 'magick'.
    """
    escaped_path = f'"{image_path}"'
    cmd = f'magick {escaped_path} -colorspace Gray -format "%[fx:mean]" info:'
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return float(result.stdout.decode().strip())
    except Exception as e:
        print(f"[!] Failed to analyze brightness of {image_path}: {e}", file=sys.stderr)
        return None

def process_file(input_path, output_path, current_idx, total_files, reference_path=None):
    """
    Constructs the console command string and runs exposure adjustment.
    Displays current progress in percent. Fixes overwrite timestamp bug.
    """
    escaped_input = f'"{input_path}"'
    escaped_output = f'"{output_path}"'
    
    # Сразу сохраняем ОРИГИНАЛЬНОЕ время файла ДО запуска любых команд magick
    try:
        stat_info = os.stat(input_path)
        orig_timestamps = (stat_info.st_atime, stat_info.st_mtime)
    except Exception as e:
        print(f"[!] Error reading original timestamps for {input_path}: {e}", file=sys.stderr)
        return False
    
    # Calculate progress percentage
    progress = int((current_idx / total_files) * 100)
    progress_str = f"[{progress}%]"

    # Check if the current file is the reference itself
    if reference_path and os.path.abspath(input_path) == os.path.abspath(reference_path):
        if os.path.abspath(input_path) == os.path.abspath(output_path):
            # Overwrite mode: do nothing, it's already perfect
            return True
        else:
            # Subdirectory mode: safely copy the reference as-is to complete the batch
            print(f"-> {os.path.basename(input_path)} {progress_str}: [Reference file] Copying without changes")
            try:
                shutil.copy2(input_path, output_path)
                return True
            except Exception as e:
                print(f"[!] Error copying reference file: {e}", file=sys.stderr)
                return False

    if reference_path:
        ref_mean = get_image_mean_brightness(reference_path)
        img_mean = get_image_mean_brightness(input_path)
        
        if ref_mean is None or img_mean is None:
            print(f"[!] Skipping file {input_path} due to brightness analysis error.")
            return False
            
        if img_mean == 0: 
            img_mean = 0.001
            
        gamma_factor = ref_mean / img_mean
        print(f"-> {os.path.basename(input_path)} {progress_str}: Gamma {gamma_factor:.2f} (matching {os.path.basename(reference_path)})")
        
        cmd = f'magick {escaped_input} -normalize -gamma {gamma_factor} {escaped_output}'
    else:
        print(f"-> {os.path.basename(input_path)} {progress_str}")
        cmd = f'magick {escaped_input} -auto-level -auto-gamma {escaped_output}'

    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Применяем сохраненные заранее оригинальные метки времени к новому/перезаписанному файлу
        os.utime(output_path, orig_timestamps)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Error processing {input_path}: {e.stderr.decode().strip()}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description=(
            "FehuMedia Exposure Tool\n\n"
            "A batch utility designed to balance photo exposure either automatically "
            "or by matching a reference image. Fully integrated with SpaceFM (%F).\n\n"
            "Modes:\n"
            "  1. Automatic: Stretches dynamic range and balances midtones automatically.\n"
            "  2. Reference Match: Calculates gamma correction based on a target reference image.\n\n"
            "Features:\n"
            "  - Preserves original image timestamps (mtime/atime) even during in-place overwrite.\n"
            "  - Prompts before overwriting, allowing saving to a dedicated subdirectory.\n"
            "  - Cleans up drag-and-dropped paths automatically."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "files", 
        nargs="+", 
        help="One or more image files passed from SpaceFM or standard command line."
    )

    args = parser.parse_args()

    # Filter only existing files
    valid_files = [f for f in args.files if os.path.exists(f)]
    if not valid_files:
        print("[!] No valid files found for processing.", file=sys.stderr)
        sys.exit(1)

    print(f"Selected files for processing: {len(valid_files)}")

    # 1. Interactive reference image selection
    ref_path = input("Specify the path to the reference file [None]: ").strip()
    
    # Strip quotes (if file was dragged and dropped into the terminal)
    ref_path = ref_path.strip("'\"")

    if ref_path:
        if not os.path.exists(ref_path):
            print(f"[!] Specified reference file not found: {ref_path}", file=sys.stderr)
            sys.exit(1)
        print(f"[i] Reference selected: {os.path.basename(ref_path)}")
    else:
        ref_path = None
        print("[i] Mode: Automatic exposure balance (no reference)")

    # 2. Interactive save mode selection
    choice = input("Overwrite original files? [Y/n]: ").strip().lower()

    output_dir = None
    if choice == 'n':
        output_dir = os.path.join(os.getcwd(), "exposure_fixed")
        os.makedirs(output_dir, exist_ok=True)
        print(f"[i] Files will be saved to directory: {output_dir}")
    else:
        print("[i] Files will be overwritten (preserving original timestamps).")

    # 3. Batch processing loop for all %F files
    success_count = 0
    total_files = len(valid_files)
    
    for idx, file_path in enumerate(valid_files, start=1):
        if output_dir:
            out_path = os.path.join(output_dir, os.path.basename(file_path))
        else:
            out_path = file_path

        if process_file(file_path, out_path, idx, total_files, ref_path):
            success_count += 1

    print(f"\n[✓] Processing finished. Successfully processed: {success_count} out of {len(valid_files)}.")

if __name__ == "__main__":
    main()
