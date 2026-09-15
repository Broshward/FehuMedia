#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def convert_yuv_to_jpg(input_path, output_path, resolution, pix_fmt, current_idx, total_files):
    """
    Converts a single raw YUV422 file to JPEG using ffmpeg via shell string command.
    Preserves original timestamps.
    """
    escaped_input = f'"{input_path}"'
    escaped_output = f'"{output_path}"'
    
    # Convert FehuMedia format "Width:Height" to ffmpeg format "WidthxHeight"
    ffmpeg_res = resolution.replace(':', 'x')
    
    progress = int((current_idx / total_files) * 100)
    progress_str = f"[{progress}%]"

    print(f"-> {os.path.basename(input_path)} {progress_str} converting...")

    # Construct the command as a single string matching project conventions
    cmd = f'ffmpeg -v error -f rawvideo -pix_fmt {pix_fmt} -s {ffmpeg_res} -i {escaped_input} -y {escaped_output}'

    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Copy original mtime and atime to the new JPG file
        stat_info = os.stat(input_path)
        os.utime(output_path, (stat_info.st_atime, stat_info.st_mtime))
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Error converting {input_path}: {e.stderr.decode().strip()}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="FehuMedia: Convert raw YUV422 images to JPG (SpaceFM %F compatible)."
    )
    parser.add_argument("files", nargs="+", help="One or more raw YUV422 files to convert.")
    parser.add_argument(
        "-r", "--resolution", 
        help="Resolution of the raw image in Width:Height format (e.g., 1920:1080)."
    )
    parser.add_argument(
        "--fmt", 
        default="yuv422p", 
        choices=["yuv422p", "yuyv422", "uyvy422"], 
        help="Specific YUV422 pixel format layout. Default is 'yuv422p'."
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory for converted JPG files. Default is the current working directory."
    )
    parser.add_argument(
        "--ask-difficult-questions", 
        action="store_true", 
        help="Enable interactive prompt mode for resolution, pixel format, and output directory."
    )

    args = parser.parse_args()

    # Filter valid files
    valid_files = [f for f in args.files if os.path.exists(f)]
    if not valid_files:
        print("[!] No valid files found for conversion.", file=sys.stderr)
        sys.exit(1)

    # Initial values from command line arguments
    resolution = args.resolution
    pix_fmt = args.fmt
    target_dir = args.out_dir if args.out_dir else os.getcwd()

    # Interactive Mode (Ask Difficult Questions)
    if args.ask_difficult_questions:
        print(f"\n[?] Entering Interactive Configuration Mode for {len(valid_files)} files:")
        
        # 1. Ask for resolution
        default_res = resolution if resolution else "1920:1080"
        res_input = input(f"Enter image resolution [default: {default_res}]: ").strip()
        if res_input:
            resolution = res_input
        else:
            resolution = default_res

        # 2. Ask for pixel format layout
        fmt_input = input(f"Enter pixel format (yuv422p, yuyv422, uyvy422) [default: {pix_fmt}]: ").strip().lower()
        if fmt_input:
            if fmt_input in ["yuv422p", "yuyv422", "uyvy422"]:
                pix_fmt = fmt_input
            else:
                print(f"[!] Invalid format selected. Falling back to default: {pix_fmt}")

        # 3. Ask for output directory
        dir_input = input(f"Enter output directory path [default: {target_dir}]: ").strip()
        if dir_input:
            # Clean quotes if folder was dragged and dropped into terminal
            target_dir = dir_input.strip("'\"")

    # Fallback validation check if not running interactive mode and argument was missing
    if not resolution:
        print("[!] Error: Resolution is required. Provide it via --resolution or use --ask-difficult-questions.", file=sys.stderr)
        sys.exit(1)

    if ':' not in resolution:
        print("[!] Error: Resolution must be in Width:Height format (e.g., 1920:1080).", file=sys.stderr)
        sys.exit(1)

    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)

    print(f"\nSelected files for YUV422 conversion: {len(valid_files)}")
    print(f"Target profile: Resolution={resolution}, Format={pix_fmt}")
    print(f"Output directory: {target_dir}\n")
    
    success_count = 0
    total_files = len(valid_files)

    for idx, file_path in enumerate(valid_files, start=1):
        # Extract filename without path and change extension to .jpg
        filename_only = os.path.basename(file_path)
        base_name, _ = os.path.splitext(filename_only)
        out_name = f"{base_name}.jpg"
        
        # Build absolute path inside the target directory
        out_path = os.path.join(target_dir, out_name)

        # Safety check if input and output paths clash
        if os.path.abspath(out_path) == os.path.abspath(file_path):
            out_path = os.path.join(target_dir, f"{filename_only}.jpg")

        if convert_yuv_to_jpg(file_path, out_path, resolution, pix_fmt, idx, total_files):
            success_count += 1

    print(f"\n[✓] Conversion finished. Successfully converted: {success_count} out of {len(valid_files)}.")

if __name__ == "__main__":
    main()
