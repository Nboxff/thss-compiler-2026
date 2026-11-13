cmake_minimum_required(VERSION 3.10)
project(pa3 LANGUAGES CXX)

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

# ANTLR-generated lexer / parser / visitor, shared by both executables.
file(GLOB ANTLR_SRC src/SysY*.cpp)

# Part 2: type checking only (diagnostics go to stderr).
add_executable(sysy_typecheck
    src/main_typecheck.cpp
    src/TypeChecker.cpp
    ${ANTLR_SRC}
)
target_link_libraries(sysy_typecheck antlr4_static)

# Part 3: call graph only (Mermaid goes to stdout).
add_executable(sysy_callgraph
    src/main_callgraph.cpp
    src/CallGraph.cpp
    src/CallGraphBuilder.cpp
    ${ANTLR_SRC}
)
target_link_libraries(sysy_callgraph antlr4_static)
