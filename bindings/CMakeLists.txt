# We find Python and nanobind to build the extension
find_package(
  Python 3.10
  COMPONENTS Interpreter Development.Module
  REQUIRED)

# Try to find nanobind from the current python environment
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(kribu_ext src/kribu_ext.cpp)

# Link against the core engine
target_link_libraries(kribu_ext PRIVATE kribu_engine)

# Copy the compiled .so object into the python package directory so it's
# immediately usable
add_custom_command(
  TARGET kribu_ext
  POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:kribu_ext>
          ${CMAKE_SOURCE_DIR}/python/src/kribu/)
