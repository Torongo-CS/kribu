# Kribu Engine

This directory contains the core C++ library. It has no dependencies on Python or nanobind. All Sholo Guti logic, including the 80-bit board representation using `__int128_t` and branchless Minimax/MCTS logic, goes here.

## Structure

- `include/kribu/`: Public header files.
- `src/`: Implementation files.
- `tests/`: Unit tests written using `Catch2`.
