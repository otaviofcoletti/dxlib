# C extensions for dxlib
# Author: Rafael Zimmer
# ----------------------
cmake_minimum_required(VERSION 3.14)

project(dxlib_test C)

# Set the C standard to use
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_subdirectory(core)
enable_testing()

add_executable(test_portfolio tests/test_portfolio.c)

# Link the test executable to the library (if you have one)
target_link_libraries(test_portfolio PRIVATE dxlib)

# Add the test to CTest so that it can run
add_test(NAME CExtensionTest COMMAND test_portfolio)