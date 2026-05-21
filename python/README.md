# Kribu Python Package

This directory contains the high-level Python code. It orchestrates the C++ engine (via the compiled `kribu_ext` module) to run simulations, generate training data, and train PyTorch neural networks.

## Structure

- `src/kribu/`: The Python package source.
- `tests/`: Pytest test suite to verify Python-side logic and bindings.
