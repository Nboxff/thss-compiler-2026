cmake_minimum_required(VERSION 3.10)
project(pa2 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(ANTLR_BUILD_CPP_TESTS OFF CACHE BOOL "Build ANTLR runtime tests" FORCE)

add_subdirectory(third_party/antlr4-runtime)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/antlr4-runtime/runtime/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

file(GLOB SRC_FILES
    src/*.cpp
)

add_executable(toml_formatter ${SRC_FILES})

target_link_libraries(toml_formatter antlr4_static)
