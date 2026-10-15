#include <fstream>
#include <iostream>

#include "TOMLFormatter.h"
#include "TOMLLexer.h"
#include "TOMLParser.h"

using namespace antlr4;

int main(int argc, char *argv[]) {
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <input_file>" << std::endl;
    return 1;
  }

  std::ifstream stream;
  stream.open(argv[1]);
  if (!stream) {
    std::cerr << "Cannot open file: " << argv[1] << std::endl;
    return 1;
  }

  // TODO: Create an ANTLR input stream from the file, then create a lexer and
  // parser for TOML, and finally use the TOMLFormatter visitor to format the
  // input.
  return 0;
}
