cmake_saver is a Python script to save developers time when working with CMake list files by automating _some_ formatting.

# Motivation
While there are many highly configurable autoformatters for C/C++/Python and other commonly used languages, the list of CMake formatters is short ([cmake-format](https://github.com/cheshirekow/cmake_format), [cmake-tidy](https://github.com/MaciejPatro/cmake-tidy)) and insufficient for some use cases. While capable, they completely overhaul the input CMake lists and lack some key configuration options like ["leave newlines alone"](https://github.com/cheshirekow/cmake_format/issues/246).

cmake_saver takes a different approach: automatically address the most common pain points when reviewing and merging CMake lists and _leave everything else alone_.

# Capability
- **Remove trailing whitespace.**
Trailing whitespace is visual noise for those with "Render whitespace" enabled and a waste of disk space for everyone.
- _(Planned)_ **Apply tabs or spaces throughout.**
There are good reasons for tabs, and good reasons for spaces. There's no good reason for mixing them within a file. Pick one and apply it throughout to avoid visual noise when editing, reading, or reviewing list files in different edtors.
- (_Planned)_ **Alphabetize vertical lists.**
For lists where order doesn't matter, vertical lists of individual entries that abide by a sorting rule are easiest to review and merge. All sorting rules are somewhat arbitrary, but sorting in alphabetical order is automatically enforceable.

# Design Goals
- **Fully cross-platform.** CMake is a cross-platform build tool, so any CMake list file formatter should be, too.
- **Full test coverage.**
- **No dependencies other than Python.** Supports maximum portability and usability.
- **Works with all versions of python.** Some developers only have access to Python 2.7.
- **No install required.** Deployable and usable as a single plain text `cmake_saver.py` script.

# Use Cases
- Developer(s) edit the CMake list files within a directory tree in a way that may have introduced a mix of tabs and spaces. While reviewing the files, a developer wishes to know whether the observed inconsistent indentation is intentional or just an artifact of differing underlying whitespace characters and display settings. The developer runs cmake_saver on all of the CMake list files in a local copy of the directory tree to standardize on either tabs or spaces throughout by changing files in place. At this point, the developer can adjust indentation to achieve the desired look with confidence that the relative indentation will show up correctly in all code file viewers.

# Requirements
1. cmake_saver shall be executable as a python script via `python cmake_saver.py`
2. cmake_saver shall be executable as a python module via `python -m cmake_saver`
3. cmake_saver, when executed with the `-h` argument, shall print a usage string
4. cmake_saver, when executed with the `-d` argument, shall remove all trailing whitespace characters (`[ \t]`) from all CMake list files (`CMakeLists.txt` and `*.cmake`) in the input directory
5. cmake_saver, when executed with no arguments, shall behave like it was executed with `-d` pointing to the current working directory
6. cmake_saver, when executed with the `-r` argument, shall recurse into and operate on all files in all* directories under the input directory
7. *cmake_saver shall not recurse into version control or cache directories