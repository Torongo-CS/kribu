#include "kribu/math.hpp"

#include <cstdint>

namespace kribu {
bool is_prime(uint64_t n) {
  if (n <= 3) {
    return n > 1;
  }

  if (n % 2 == 0 || n % 3 == 0) {
    return false;
  }

  // NOLINTNEXTLINE(readability-magic-numbers)
  for (uint64_t i = 5; i * i <= n; i += 6) {
    if (n % i == 0 || n % (i + 2) == 0) {
      return false;
    }
  }

  return true;
}
}  // namespace kribu
