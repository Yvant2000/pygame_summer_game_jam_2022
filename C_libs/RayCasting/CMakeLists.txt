cmake_minimum_required(VERSION 3.19)
project(Filter)

set(CMAKE_CXX_STANDARD 14)

add_executable(Filter
        casting.cpp)


find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(Filter ${PYTHON_LIBRARIES})

find_package(Python3 3.7 COMPONENTS Interpreter NumPy REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(Filter ${PYTHON_LIBRARIES} Python3::NumPy)