#include <doctest/doctest.h>
#include "lib1/lib1.h"
#include <cstdlib>

using namespace TestProject;

TEST_SUITE(TP_TEST_SUITE) {
  TEST_CASE("do_something") {
    CHECK(true);
  }
}
