#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def convert_yuv_to_jpg(input_path, output_path, resolution, pix_fmt, jpeg_quality, current_idx, total_files):
    """
    Converts a single raw YUV422 file to JPEG using ffmpeg via shell string command.
    Includes explicit control over JPEG quality. Preserves original timestamps.
    """
    escaped_input = f'"{input_path}"'
    escaped_output = f'"{output_path}"'
    
    # Convert FehuMedia format "Width:Height" to ffmpeg format "WidthxHeight"
    ffmpeg_res = resolution.replace(':', 'x')
    
    progress = int((current_idx / total_files) * 100)
    progress_str = f"[{progress}%]"

    print(f"-> {os.path.basename(input_path)} {progress_str} converting...")

    # Construct the command with the -q:v parameter for quality control
    # -q:v 1-31 (1 is best quality, 31 is worst)
    cmd = f'ffmpeg -v error -f rawvideo -pix_fmt {pix_fmt} -s {ffmpeg_res} -i {escaped_input} -q:v {jpeg_quality} -y {escaped_output}'

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
        "-q", "--quality",
        type=int,
        default=2,
        help="JPEG quality scale (1-31), where 1 is highest fidelity/lowest compression. Default is 2."
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory for converted JPG files. Default is the current working directory."
    )
    parser.add_argument(
        "--ask-difficult-questions", 
        action="store_true", 
        help="Enable interactive prompt mode for configuration."
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
    jpeg_quality = args.quality
    target_dir = args.out_dir if args.out_dir else os.getcwd()

    # Interactive Mode (Ask Difficult Questions)
    if args.ask_difficult_questions:
        print(f"\n[?] Entering Interactive Configuration Mode for {len(valid_files)} files:")
        
        # 1. Ask for resolution (if not specified via CLI)
        if args.resolution is None:
            default_res = "1920:1080"
            res_input = input(f"Enter image resolution [default: {default_res}]: ").strip()
            resolution = res_input if res_input else default_res

        # 2. Ask for pixel format layout (if not specified via CLI)
        if args.fmt == parser.get_default("--fmt"): # check if it's default
            fmt_input = input(f"Enter pixel format (yuv422p, yuyv422, uyvy422) [default: {pix_fmt}]: ").strip().lower()
            if fmt_input in ["yuv422p", "yuyv422", "uyvy422"]:
                pix_fmt = fmt_input

        # 3. Ask for JPEG quality (if not modified via CLI)
        if args.quality == parser.get_default("--quality"):
            q_input = input(f"Enter JPEG quality scale (1-31, 1=best) [default: {jpeg_quality}]: ").strip()
            if q_input:
                try:
                    q_val = int(q_input)
                    if 1 <= q_val <= 31:
                        jpeg_quality = q_val
                    else:
                        print(f"  [!] Quality out of range. Using default: {jpeg_quality}")
                except ValueError:
                    print(f"  [!] Invalid number. Using default: {jpeg_quality}")

        # 4. Ask for output directory (if not specified via CLI)
        if args.out_dir is None:
            dir_input = input(f"Enter output directory path [default: {target_dir}]: ").strip()
            if dir_input:
                target_dir = dir_input.strip("'\"")

    # Fallback validation check
    if not resolution:
        print("[!] Error: Resolution is required. Provide it via --resolution or use --ask-difficult-questions.", file=sys.stderr)
        sys.exit(1)

    if ':' not in resolution:
        print("[!] Error: Resolution must be in Width:Height format (e.g., 1920:1080).", file=sys.stderr)
        sys.exit(1)

    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)

    print(f"\nSelected files for YUV422 conversion: {len(valid_files)}")
    print(f"Target profile: Resolution={resolution}, Format={pix_fmt}, JPEG Quality={jpeg_quality}")
    print(f"Output directory: {target_dir}\n")
    
    success_count = 0
    total_files = len(valid_files)

    for idx, file_path in enumerate(valid_files, start=1):
        filename_only = os.path.basename(file_path)
        base_name, _ = os.path.splitext(filename_only)
        out_name = f"{base_name}.jpg"
        out_path = os.path.join(target_dir, out_name)

        if os.path.abspath(out_path) == os.path.abspath(file_path):
            out_path = os.path.join(target_dir, f"{filename_only}.jpg")

        if convert_yuv_to_jpg(file_path, out_path, resolution, pix_fmt, jpeg_quality, idx, total_files):
            success_count += 1

    print(f"\n[✓] Conversion finished. Successfully converted: {success_count} out of {len(valid_files)}.")

if __name__ == "__main__":
    main()
