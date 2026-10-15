ANTLR_JAR := $(abspath lib/antlr-4.13.1-complete.jar)
ANTLR     := java -jar $(ANTLR_JAR)

.PHONY: antlr build test test-part1 test-part2 clean

# Generate C++ sources from the .g4 files in grammar/ into src/
antlr:
	cd grammar && $(ANTLR) -Dlanguage=Cpp -visitor -no-listener -o ../src \
	    TOMLLexer.g4 TOMLParser.g4

build: antlr
	mkdir -p build && cd build && cmake .. && $(MAKE) -j4

test: build
	python3 run_tests.py

# Part 1 only needs the grammar, not the C++ build
test-part1:
	python3 run_tests.py --part1

test-part2: build
	python3 run_tests.py --part2

test-part3: build
	python3 run_tests.py --part3

clean:
	rm -rf build
	rm -f src/TOMLLexer.cpp src/TOMLLexer.h src/TOMLLexer.tokens src/TOMLLexer.interp \
	    src/TOMLParser.cpp src/TOMLParser.h src/TOMLParser.tokens src/TOMLParser.interp \
	    src/TOMLParserVisitor.h src/TOMLParserBaseVisitor.cpp src/TOMLParserBaseVisitor.h
