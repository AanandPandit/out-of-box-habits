#pragma once

#include <vector>
#include <string>

namespace FastUtils {

    // Example heavy computation: Find primes up to N
    std::vector<int> find_primes(int limit);

    // Example string processing: Matrix rain effect generator (returns a frame)
    std::string generate_matrix_rain(int width, int height, int frame_count);

    // Example math: Fast fibonacci
    long long fast_fibonacci(int n);
}
