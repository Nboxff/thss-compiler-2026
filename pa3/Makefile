ANTLR_JAR := $(abspath lib/antlr-4.13.1-complete.jar)
ANTLR     := java -jar $(ANTLR_JAR)

.PHONY: antlr build test test-part1 test-part2 test-part3 clean

# Generate the C++ lexer/parser/visitor from grammar/ into src/
antlr:
	cd grammar && $(ANTLR) -Dlanguage=Cpp -visitor -no-listener -o ../src \
	    SysYLexer.g4 SysYParser.g4

build: antlr
	mkdir -p build && cd build && cmake .. && $(MAKE) -j4

test: build
	python3 run_tests.py

# Part 1 uses the same Java parser harness as Gradescope and needs no C++ code.
test-part1:
	python3 run_tests.py --part1

# Parts 2 and 3 build only their own executable.
test-part2: antlr
	mkdir -p build && cd build && cmake .. && $(MAKE) sysy_typecheck -j4
	python3 run_tests.py --part2

test-part3: antlr
	mkdir -p build && cd build && cmake .. && $(MAKE) sysy_callgraph -j4
	python3 run_tests.py --part3

clean:
	rm -rf build
	rm -f src/SysYLexer.cpp src/SysYLexer.h src/SysYLexer.tokens src/SysYLexer.interp \
	    src/SysYParser.cpp src/SysYParser.h src/SysYParser.tokens src/SysYParser.interp \
	    src/SysYParserVisitor.cpp src/SysYParserVisitor.h \
	    src/SysYParserBaseVisitor.cpp src/SysYParserBaseVisitor.h
