import argparse
import configparser
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipapp
import zipfile


MAIN_TEMPLATE = """\
# -*- coding: utf-8 -*-
import pathlib
import runpy
import shutil
import tempfile
import zipfile

with zipfile.ZipFile(pathlib.Path(__file__).parent) as zip:
    with tempfile.TemporaryDirectory() as tmp:
        zip.extractall(tmp)
        shutil.copyfile(
            pathlib.Path(tmp, "{entrypoint}"), pathlib.Path(tmp, "__main__.py")
        )
        runpy.run_path(tmp, run_name="__main__")
"""


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Generate Python executable zip archive for each entry point from wheel packages (requires pip module)."
    )
    parser.add_argument(
        "-w",
        "--wheels",
        nargs="*",
        default=[],
        help="Install given wheels to the Python executable zip archive and use only entry points from [WHEEL].dist-info/entry_points.txt.",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=pathlib.Path,
        default=pathlib.Path("bin"),
        help="The output directory where Python executable zip archives (.pyz) are generated (default is ./bin).",
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
    parser.add_argument(
        "-x",
        "--auto-extract",
        action="store_true",
        help="The Python executable zip archive will be extracted into a temporary directory and run on the file system to allow execution of binary packages including a C extension.",
    )
    parser.add_argument(
        "pip_args",
        nargs="*",
        help="Extra pip install arguments.",
    )

    args = parser.parse_args(args)

    with tempfile.TemporaryDirectory() as target_dir:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--target",
                target_dir,
            ]
            + args.pip_args
            + args.wheels,
            check=True,
        )

        args.outdir.mkdir(parents=True, exist_ok=True)

        entry_points = set()
        for wheel in args.wheels:
            with zipfile.ZipFile(wheel) as wheel_zip:
                for dist_info_dir in zipfile.Path(wheel_zip).iterdir():
                    if dist_info_dir.is_dir() and dist_info_dir.name.endswith(
                        ".dist-info"
                    ):
                        entry_points_txt = dist_info_dir.joinpath("entry_points.txt")
                        if entry_points_txt.is_file():
                            entry_points_config = configparser.ConfigParser()
                            entry_points_config.read_string(
                                entry_points_txt.read_text()
                            )
                            for section in ["console_scripts", "gui_scripts"]:
                                if entry_points_config.has_section(section):
                                    entry_points.update(
                                        entry_points_config.options(section)
                                    )
                        break

        bin_dir = pathlib.Path(target_dir, "bin")
        if bin_dir.is_dir():
            for entrypoint_file in bin_dir.iterdir():
                if entrypoint_file.is_file() and (
                    entrypoint_file.name in entry_points or not args.wheels
                ):
                    main_path = pathlib.Path(target_dir, "__main__.py")
                    if args.binaries:
                        with open(main_path, "w", encoding="utf-8") as main_file:
                            main_file.write(
                                MAIN_TEMPLATE.format(
                                    entrypoint=entrypoint_file.relative_to(target_dir)
                                )
                            )
                    else:
                        shutil.copyfile(entrypoint_file, main_path)
                    zipapp.create_archive(
                        target_dir,
                        target=args.outdir.joinpath(entrypoint_file.name + ".pyz"),
                        interpreter=args.python,
                        compressed=args.compress,
                    )
