import argparse
import configparser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipapp
import zipfile


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Generate Python executable zip archive for each entry point from a wheel package."
    )
    parser.add_argument("wheel", help="")
    parser.add_argument(
        "-o",
        "--outdir",
        type=Path,
        default=Path("bin"),
        help="The output directory where Python executable zip archives are generated (default is ./bin).",
    )
    parser.add_argument(
        "-p",
        "--python",
        help='The name of the Python interpreter to use (default: no shebang line). Use "/usr/bin/env python3" to make the application directly executable on POSIX',
    )
    parser.add_argument(
        "-c",
        "--compress",
        action="store_true",
        help="Compress files with the deflate method. Files are stored uncompressed by default.",
    )

    args = parser.parse_args(args)

    with tempfile.TemporaryDirectory() as target_dir:
        subprocess.run([sys.executable, "-m", "pip", "install", "--target", target_dir, args.wheel], check=True)

        args.outdir.mkdir(parents=True, exist_ok=True)

        entry_points = set()
        with zipfile.ZipFile(args.wheel) as wheel_zip:
            for dist_info_dir in zipfile.Path(wheel_zip).iterdir():
                if dist_info_dir.is_dir() and dist_info_dir.name.endswith(".dist-info"):
                    entry_points_txt = dist_info_dir.joinpath("entry_points.txt")
                    if entry_points_txt.is_file():
                        entry_points_config = configparser.ConfigParser()
                        entry_points_config.read_string(entry_points_txt.read_text())
                        for section in ["console_scripts", "gui_scripts"]:
                            if entry_points_config.has_section(section):
                                entry_points.update(entry_points_config.options(section))
                    break

        bin_dir = Path(target_dir, "bin")
        if bin_dir.is_dir():
            for entrypoint_file in bin_dir.iterdir():
                if entrypoint_file.is_file() and entrypoint_file.name in entry_points:
                    shutil.copy(entrypoint_file, Path(target_dir, "__main__.py"))
                    zipapp.create_archive(
                        target_dir,
                        target=args.outdir.joinpath(entrypoint_file.name + ".pyz"),
                        interpreter=args.python,
                        compressed=args.compress,
                    )
