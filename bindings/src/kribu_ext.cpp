#include <nanobind/nanobind.h>

#include "kribu/math.hpp"

namespace nb = nanobind;

// NOLINTNEXTLINE(readability-identifier-length)
NB_MODULE(kribu_ext, module) {
  module.doc() = "Kribu Sholo Guti AI extension module";

  // Bind the dummy is_prime function to prove the toolchain works
  module.def("is_prime", &kribu::is_prime, "Check if a number is prime using the fast C++ engine.");
}
