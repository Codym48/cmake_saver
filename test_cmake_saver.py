import cmake_saver
import contextlib
# Pick a byte buffer in Python 2 and a unicode buffer in Python 3
# https://stackoverflow.com/a/34872005/2597078
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import os
import re
import shutil
import subprocess
import sys
import unittest

CMAKE_FILES = [
    os.path.normpath("example_project/CMakeLists.txt"),
    os.path.normpath("example_project/dir1/CMakeLists.txt"),
    os.path.normpath("example_project/dir2/my_helpers.cmake"),
    ]

TRAILING_WHITESPACE_RE = re.compile("[ \t]+$", re.MULTILINE)

FNULL = open(os.devnull, "w")


@contextlib.contextmanager
def redirect_stdout(target):
    # contextlib.redirect_stdout isn't available until Python 3.4,
    # so implement it here to support testing on Python 2.7
    # https://stackoverflow.com/a/44226422/2597078
    original = sys.stdout
    try:
        sys.stdout = target
        yield
    finally:
        sys.stdout = original


class TestFunctionsThatModifyFiles(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Copy cmake_saver.py into a subdirectory to prove we can call it there."""
        os.makedirs("tmp/sub/dir")
        shutil.copy("cmake_saver.py", "tmp/sub/dir/cmake_saver.py")

    def setUp(self):
        """Save the original text of all CMake list files to restore later."""
        self.original_text = {}
        for filename in CMAKE_FILES:
            with open(filename) as f:
                self.original_text[filename] = f.read()

    def tearDown(self):
        """Restore original CMake list file text to provide clean repository for future tests."""
        for filename in CMAKE_FILES:
            with open(filename, "w+") as f:
                f.write(self.original_text[filename])

    @classmethod
    def tearDownClass(self):
        """Remove the temporary copy of cmake_saver.py"""
        shutil.rmtree("tmp")

    def assert_fixed(self, files):
        """Assert that all input files have been inspected and fixed."""
        for filename in files:
            with open(filename) as f:
                new_text = f.read()
            self.assertIsNone(TRAILING_WHITESPACE_RE.search(new_text))

    def assert_unchanged(self, files):
        """Assert that all input files have been unchanged since setUp."""
        for filename in files:
            with open(filename) as f:
                self.assertEqual(f.read(), self.original_text[filename])

    def test_inspect_cmake_file_do_not_fix(self):
        """Verify this function inspects the single input file and discovers it is poorly formatted."""
        filename = CMAKE_FILES[0]
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(cmake_saver.inspect_cmake_file(filename, fix = False), 1)
        self.assertIn(filename, out.getvalue())
        self.assert_unchanged(CMAKE_FILES)

    def test_inspect_cmake_file_and_fix(self):
        """Verify this function inspects and fixes the single input file."""
        filename = CMAKE_FILES[0]
        self.assertEqual(cmake_saver.inspect_cmake_file(filename, fix = True), 0)
        self.assert_fixed([filename])
        self.assert_unchanged(CMAKE_FILES[1:])

    def test_main_default(self):
        """Verify main doesn't do anything since there are no CMake list files in the current working directory."""
        self.assertEqual(cmake_saver.main([]), 0)
        self.assert_unchanged(CMAKE_FILES)

    def test_main_recursive(self):
        """Verify main lists all poorly formatted CMake files recursively from the current working directory."""
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(cmake_saver.main(["-r"]), 3)
        for filename in CMAKE_FILES:
            self.assertIn(filename, out.getvalue())
        self.assert_unchanged(CMAKE_FILES)

    def test_main_recursive_fix(self):
        """Verify main fixes all CMake files recursively from the current working directory."""
        self.assertEqual(cmake_saver.main(["-r", "-f"]), 0)
        self.assert_fixed(CMAKE_FILES)

    def test_main_input_subdirectory(self):
        """Verify main fixes all CMake files within the input subdirectory."""
        self.assertEqual(cmake_saver.main(["-d", "example_project/dir2", "-f"]), 0)
        self.assert_fixed([CMAKE_FILES[-1]])
        self.assert_unchanged(CMAKE_FILES[:-1])

    def test_call_file_from_superdirectory_recursive(self):
        """Verify cmake_saver.py operates on the current directory even if it lives in a subdirectory."""
        returncode = subprocess.call("python tmp/sub/dir/cmake_saver.py -r -f", shell = True)
        self.assertEqual(returncode, 0)
        self.assert_fixed(CMAKE_FILES)

    def test_call_file_from_superdirectory_input_subdirectory(self):
        """Verify cmake_saver.py operates on the input directory even if it lives in a different subdirectory."""
        returncode = subprocess.call("python tmp/sub/dir/cmake_saver.py -d example_project/dir1 -f", shell = True)
        self.assertEqual(returncode, 0)
        self.assert_fixed([CMAKE_FILES[1]])
        self.assert_unchanged(CMAKE_FILES[0::2])

    def test_call_file_from_different_current_directory(self):
        """Verify cmake_saver.py operates on the input directory relative to the current working directory."""
        os.chdir("example_project")
        returncode = subprocess.call("python ../tmp/sub/dir/cmake_saver.py -d dir2 -f", shell = True)
        os.chdir("..")
        self.assertEqual(returncode, 0)
        self.assert_fixed([CMAKE_FILES[-1]])
        self.assert_unchanged(CMAKE_FILES[:-1])


class TestFunctionsThatDontModifyFiles(unittest.TestCase):
    def test_iter_cmake_files(self):
        """Verify this function finds no files when executed non-recursively."""
        files = [f for f in cmake_saver.iter_cmake_files(os.path.curdir, recursive = False)]
        self.assertEqual(files, [])

    def test_iter_cmake_files_recursive(self):
        """Verify this function finds all known CMake files when executed recursively."""
        files = [f for f in cmake_saver.iter_cmake_files(os.path.curdir, recursive = True)]
        self.assertEqual(sorted(files), CMAKE_FILES)

    def test_parse_args_defaults(self):
        input = cmake_saver.parse_args([])
        self.assertEqual(input.directory, os.path.curdir)
        self.assertFalse(input.fix)
        self.assertFalse(input.recursive)


class TestUserInterface(unittest.TestCase):
    def test_call_file_no_input(self):
        returncode = subprocess.call("python cmake_saver.py", shell = True)
        self.assertEqual(returncode, 0)

    def test_call_file_input_directory(self):
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            subprocess.check_output("python cmake_saver.py -d example_project", shell = True)
        self.assertEqual(cm.exception.returncode, 1)
        self.assertIn(CMAKE_FILES[0], cm.exception.output.decode())

    def test_call_file_input_fix(self):
        returncode = subprocess.call("python cmake_saver.py -f", shell = True)
        self.assertEqual(returncode, 0)

    def test_call_file_input_help(self):
        returncode = subprocess.call("python cmake_saver.py -h", stdout = FNULL, shell = True)
        self.assertEqual(returncode, 0)

    def test_call_file_input_recursive(self):
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            subprocess.check_output("python cmake_saver.py -r", shell = True)
        self.assertEqual(cm.exception.returncode, 3)
        for filename in CMAKE_FILES:
            self.assertIn(filename, cm.exception.output.decode())

    def test_call_module_no_input(self):
        returncode = subprocess.call("python -m cmake_saver", shell = True)
        self.assertEqual(returncode, 0)

    def test_call_module_input_directory(self):
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            subprocess.check_output("python -m cmake_saver -d example_project", shell = True)
        self.assertEqual(cm.exception.returncode, 1)
        self.assertIn(CMAKE_FILES[0], cm.exception.output.decode())

    def test_call_module_input_fix(self):
        returncode = subprocess.call("python -m cmake_saver -f", shell = True)
        self.assertEqual(returncode, 0)

    def test_call_module_input_help(self):
        returncode = subprocess.call("python -m cmake_saver -h", stdout = FNULL, shell = True)
        self.assertEqual(returncode, 0)

    def test_call_module_input_recursive(self):
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            subprocess.check_output("python -m cmake_saver -r", shell = True)
        self.assertEqual(cm.exception.returncode, 3)
        for filename in CMAKE_FILES:
            self.assertIn(filename, cm.exception.output.decode())


if __name__ == "__main__":
    unittest.main()
