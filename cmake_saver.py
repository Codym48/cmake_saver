import argparse
import os
import re
import sys

EXCLUDE_DIRS = [".git", ".svn", ".pytest_cache", "__pycache__"]


def iter_cmake_files(directory, recursive = False):
    """Generate an iterable of CMake files on which to operate."""
    for dirpath, dirnames, filenames in os.walk(os.path.normpath(directory)):
        dirnames[:] = [d for d in dirnames if (recursive and d not in EXCLUDE_DIRS)]
        for filename in filenames:
            if "CMakeLists.txt" == filename or filename.endswith(".cmake"):
                yield os.path.normpath(os.path.join(dirpath, filename))


def inspect_cmake_file(filename, fix = False):
    """Inspect CMake file. If improperly formatted either fix in place, or print filename and return 1."""
    with open(filename, "r") as f:
        text = f.read()
    trailing_whitespace_re = re.compile("[ \t]+$", re.MULTILINE)
    new_text = trailing_whitespace_re.sub("", text)
    if new_text != text:
        if fix:
            with open(filename, "w+") as f:
                f.write(new_text)
        else:
            print(filename)
            return 1
    return 0


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        default = os.path.curdir,
        help = "directory to search for CMake list files",
        )
    parser.add_argument(
        "-f",
        "--fix",
        action = "store_true",
        help = "fix CMake list files in place",
        )
    parser.add_argument(
        "-r",
        "--recursive",
        action = "store_true",
        help = "recurse into all subdirectories of input directory",
        )
    return parser.parse_args(args)


def main(args):
    """Either list and return a count of all improperly formatted CMake files or fix them in place."""
    input = parse_args(args)
    bad_file_count = 0
    for filename in iter_cmake_files(input.directory, input.recursive):
        bad_file_count += inspect_cmake_file(filename, input.fix)
    return bad_file_count


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
