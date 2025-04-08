import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipapp


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Generate Python executable zip archive for each entry point from a wheel package."
    )
    parser.add_argument("wheel", help="")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(),
        help="The output directory where Python executable zip archives are generated.",
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

        args.output.mkdir(parents=True, exist_ok=True)

        # TODO Filter entry points using *.whl/*.dist-info/entry_points.txt

        bin_dir = Path(target_dir, "bin")
        if bin_dir.is_dir():
            for entrypoint_file in bin_dir.iterdir():
                if entrypoint_file.is_file():
                    shutil.copy(entrypoint_file, Path(target_dir, "__main__.py"))
                    zipapp.create_archive(
                        target_dir,
                        target=args.output.joinpath(entrypoint_file.name + ".pyz"),
                        interpreter=args.python,
                        compressed=args.compress,
                    )
