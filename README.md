# Kribu

High-performance Sholo Guti AI engine.

## Structure

- **`engine/`**: Pure C++ library handling game logic and search.
- **`bindings/`**: C++ to Python integration using `nanobind`.
- **`python/`**: High-level wrapper, data generation, and machine learning code.

## Setup & Building

Ensure you have `uv` and `cmake` installed.

```bash
# Setup dependencies and pre-download CPM
make setup

# Build with all cores and run the dummy example
make run

# Run all tests
make test-cpp
make test-python

# Format and Lint
make format
make lint

# Clean everything (including ignored binaries)
make clean
```
