.PHONY: setup build test test-cpp test-python clean format lint run

# Detect number of processors for parallel execution
NPROC := $(shell nproc)

export CC := clang
export CXX := clang++

setup:
	uv sync
	uv run cmake -B build -S .
	# Link compile_commands.json to root for IDE support (VS Code / CLion)
	ln -sf build/compile_commands.json .
	uv run pre-commit install

build:
	uv run cmake -B build -S .
	uv run cmake --build build -j$(NPROC)

test: test-cpp test-python

test-cpp: build
	./build/engine/kribu_engine_tests

test-python:
	PYTHONPATH=python/src uv run pytest python/tests/

run: build
	PYTHONPATH=python/src uv run python python/src/kribu/main.py

format:
	uv run ruff format python/
	find engine bindings -name "*.cpp" -o -name "*.hpp" | xargs -P $(NPROC) uv run clang-format -i
	find . -maxdepth 3 \( -name "CMakeLists.txt" -o -name "*.cmake" \) -not -path "*/build/*" -not -path "*/.venv/*" | xargs -P $(NPROC) uv run cmake-format -i
	find . -maxdepth 2 -name "*.md" -not -path "*/.venv/*" | xargs -P $(NPROC) uv run mdformat

lint:
	uv run ruff check python/
	find engine bindings -name "*.cpp" | xargs -P $(NPROC) clang-tidy -p build/ --quiet || true

clean:
	git clean -Xdf
