cmake_minimum_required(VERSION 3.10)
project(hacker_utils)

set(CMAKE_CXX_STANDARD 14)

# Find Pybind11
find_package(pybind11 REQUIRED)

# Create the extension module
pybind11_add_module(hacker_utils fast_utils.cpp)

# Output directory for the compiled library (so Python can find it easily)
set_target_properties(hacker_utils PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../../src/core"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../../src/core"
)
