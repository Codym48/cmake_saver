import cmake_saver
import os
import re
import shutil
import subprocess
import unittest

CMAKE_FILES = [
    os.path.normpath("example_project/CMakeLists.txt"),
    os.path.normpath("example_project/dir1/CMakeLists.txt"),
    os.path.normpath("example_project/dir2/my_helpers.cmake"),
    ]

TRAILING_WHITESPACE_RE = re.compile("[ \t]+$", re.MULTILINE)

FNULL = open(os.devnull, 'w')


class TestFunctionsThatModifyFiles(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Copy cmake_saver.py into a subdirectory to prove we can call it there."""
        os.makedirs('tmp/sub/dir')
        shutil.copy('cmake_saver.py', 'tmp/sub/dir/cmake_saver.py')

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
        shutil.rmtree('tmp')

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

    def test_inspect_cmake_file(self):
        """Verify this function inspects and fixes the single input file."""
        filename = CMAKE_FILES[0]
        cmake_saver.inspect_cmake_file(filename)
        self.assert_fixed([filename])
        self.assert_unchanged(CMAKE_FILES[1:])

    def test_main_default(self):
        """Verify main fixes all CMake files recursively from the current working directory."""
        self.assertEqual(cmake_saver.main([]), 0)
        self.assert_fixed(CMAKE_FILES)

    def test_main_input_subdirectory(self):
        """Verify main fixes all CMake files within the input subdirectory."""
        self.assertEqual(cmake_saver.main(['-d', 'example_project/dir2']), 0)
        self.assert_fixed([CMAKE_FILES[-1]])
        self.assert_unchanged(CMAKE_FILES[:-1])

    def test_call_file_from_superdirectory(self):
        ret_code = subprocess.call('python tmp/sub/dir/cmake_saver.py', shell = True)
        self.assertEqual(ret_code, 0)
        self.assert_fixed(CMAKE_FILES)

    def test_call_file_from_superdirectory_input_subdirectory(self):
        ret_code = subprocess.call('python tmp/sub/dir/cmake_saver.py -d example_project/dir1', shell = True)
        self.assertEqual(ret_code, 0)
        self.assert_fixed([CMAKE_FILES[1]])
        self.assert_unchanged(CMAKE_FILES[0::2])

    def test_call_file_from_different_current_directory(self):
        os.chdir('example_project')
        ret_code = subprocess.call('python ../tmp/sub/dir/cmake_saver.py -d dir2', shell = True)
        os.chdir('..')
        self.assertEqual(ret_code, 0)
        self.assert_fixed([CMAKE_FILES[-1]])
        self.assert_unchanged(CMAKE_FILES[:-1])


class TestFunctionsThatDontModifyFiles(unittest.TestCase):
    def test_iter_cmake_files(self):
        """Verify this function finds all known CMake files."""
        files = [f for f in cmake_saver.iter_cmake_files(os.path.curdir)]
        self.assertEqual(sorted(files), CMAKE_FILES)

    def test_parse_args_default_to_curdir(self):
        input = cmake_saver.parse_args([])
        self.assertEqual(input.directory, os.path.curdir)


class TestUserInterface(unittest.TestCase):
    def test_call_file_input_directory(self):
        ret_code = subprocess.call('python cmake_saver.py -d doesnotexist', shell = True)
        self.assertEqual(ret_code, 0)

    def test_call_file_input_help(self):
        ret_code = subprocess.call('python cmake_saver.py -h', stdout = FNULL, shell = True)
        self.assertEqual(ret_code, 0)

    def test_call_module_input_directory(self):
        ret_code = subprocess.call('python -m cmake_saver -d doesnotexist', shell = True)
        self.assertEqual(ret_code, 0)

    def test_call_module_input_help(self):
        ret_code = subprocess.call('python -m cmake_saver -h', stdout = FNULL, shell = True)
        self.assertEqual(ret_code, 0)


if __name__ == "__main__":
    unittest.main()
