#include "fast_utils.h"
#include <algorithm>
#include <cmath>
#include <random>
#include <sstream>


namespace FastUtils {

std::vector<int> find_primes(int limit) {
  if (limit < 2)
    return {};
  std::vector<bool> is_prime(limit + 1, true);
  is_prime[0] = is_prime[1] = false;
  for (int p = 2; p * p <= limit; p++) {
    if (is_prime[p]) {
      for (int i = p * p; i <= limit; i += p)
        is_prime[i] = false;
    }
  }
  std::vector<int> primes;
  for (int p = 2; p <= limit; p++) {
    if (is_prime[p])
      primes.push_back(p);
  }
  return primes;
}

std::string generate_matrix_rain(int width, int height, int frame_count) {
  static const char chars[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*";
  static std::mt19937 rng(
      frame_count); // Deterministic based on frame for stability
  std::uniform_int_distribution<int> dist(0, sizeof(chars) - 2);

  std::stringstream ss;
  for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
      if (rng() % 10 > 7) { // Sparse rain
        ss << chars[dist(rng)];
      } else {
        ss << " ";
      }
    }
    ss << "\n";
  }
  return ss.str();
}

long long fast_fibonacci(int n) {
  if (n <= 1)
    return n;
  long long a = 0, b = 1;
  for (int i = 2; i <= n; ++i) {
    long long temp = a + b;
    a = b;
    b = temp;
  }
  return b;
}
} // namespace FastUtils

// PyBind11 Binding Code
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(hacker_utils, m) {
  m.doc() = "Fast C++ utilities for HackerOS";

  m.def("find_primes", &FastUtils::find_primes,
        "Find all prime numbers up to a limit");
  m.def("generate_matrix_rain", &FastUtils::generate_matrix_rain,
        "Generate a frame of matrix rain");
  m.def("fast_fibonacci", &FastUtils::fast_fibonacci,
        "Calculate nth Fibonacci number efficiently");
}
