# Kribu

High-performance Sholo Guti AI engine.

## Structure

- **`engine/`**: Pure C++ library handling game logic and search.
- **`bindings/`**: C++ to Python integration using `nanobind`.
- **`python/`**: High-level wrapper, data generation, and machine learning code.

## Commands

Ensure you have `uv` and `cmake` installed.

```bash
# Setup dependencies and pre-download CPM
make setup

# Build the C++ extension in debug/development mode
make build

# OR for release build
make release

# Run the simulation (uses the compiled binary)
make run

# Run all tests
make test

# Format and Lint
make format
make lint

# Clean build artifacts
make clean
```

### Hot Build (Auto-rebuild on file changes)

If you are actively developing the C++ engine or bindings, you can use the hot-build command to automatically rebuild the project whenever you save a C++ header or source file:

```bash
# Start the file watcher (requires 'entr' installed on your system)
make hot-build
```
