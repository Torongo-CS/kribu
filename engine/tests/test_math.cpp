#include <catch2/catch_test_macros.hpp>

#include "kribu/math.hpp"

TEST_CASE("Prime numbers are computed correctly", "[math]") {
  REQUIRE(kribu::is_prime(2));
  REQUIRE_FALSE(kribu::is_prime(4));
  REQUIRE(kribu::is_prime(17));
  REQUIRE_FALSE(kribu::is_prime(18));
}
