import argparse
import os
import re
import sys

EXCLUDE_DIRS = [".git", ".svn", ".pytest_cache", "__pycache__"]


def iter_cmake_files(toplevel):
    """Generate an iterable of CMake files on which to operate."""
    for dirpath, dirnames, filenames in os.walk(os.path.normpath(toplevel)):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if "CMakeLists.txt" == filename or filename.endswith(".cmake"):
                yield os.path.normpath(os.path.join(dirpath, filename))


def inspect_cmake_file(filename):
    """Inspect CMake file for improper formatting, fix and overwrite file."""
    with open(filename, "r") as f:
        text = f.read()
    trailing_whitespace_re = re.compile("[ \t]+$", re.MULTILINE)
    text = trailing_whitespace_re.sub("", text)
    with open(filename, "w+") as f:
        f.write(text)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        default = os.path.curdir,
        help = "Directory to search for CMake list files",
        )
    return parser.parse_args(args)


def main(args):
    """Fix all CMake list files in place in current directory."""
    input = parse_args(args)
    for filename in iter_cmake_files(input.directory):
        inspect_cmake_file(filename)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
