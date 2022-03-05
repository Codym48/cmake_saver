cmake_saver is a Python script to save developers time when working with CMake list files by automating _some_ formatting.

# Motivation
While there are many highly configurable autoformatters for C/C++/Python and other commonly used languages, the list of CMake formatters is short ([cmake-format](https://github.com/cheshirekow/cmake_format), [cmake-tidy](https://github.com/MaciejPatro/cmake-tidy)) and insufficient for some use cases. While capable, they completely overhaul the input CMake lists and lack some key configuration options like ["leave newlines alone"](https://github.com/cheshirekow/cmake_format/issues/246).

cmake_saver takes a different approach: automatically address the most common pain points when reviewing and merging CMake lists and _leave everything else alone_.

# Capability
- _(Planned)_ **Apply tabs or spaces throughout.**
There are good reasons for tabs, and good reasons for spaces. There's no good reason for mixing them within a file. Pick one and apply it throughout to avoid visual noise when editing, reading, or reviewing list files in different edtors.
- (_Planned)_ **Alphabetize vertical lists.**
For lists where order doesn't matter, vertical lists of individual entries that abide by a sorting rule are easiest to review and merge. All sorting rules are somewhat arbitrary, but sorting in alphabetical order is automatically enforceable.
