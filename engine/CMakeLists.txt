add_library(kribu_engine src/math.cpp)
target_include_directories(kribu_engine PUBLIC include)

# Position independent code is required for linking into Python shared libraries
# (.so)
set_target_properties(kribu_engine PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Setup Catch2 tests using CPM
cpmaddpackage(
  NAME
  Catch2
  GITHUB_REPOSITORY
  catchorg/Catch2
  VERSION
  3.4.0
  GIT_SHALLOW
  1)
add_executable(kribu_engine_tests tests/test_math.cpp)
target_link_libraries(kribu_engine_tests PRIVATE kribu_engine
                                                 Catch2::Catch2WithMain)

# Include Catch2 test discovery so ctest can find them
list(APPEND CMAKE_MODULE_PATH ${Catch2_SOURCE_DIR}/extras)
include(Catch)
catch_discover_tests(kribu_engine_tests)
