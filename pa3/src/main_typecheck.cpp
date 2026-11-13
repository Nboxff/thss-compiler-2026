#include <fstream>
#include <iostream>
#include <string>

#include "SysYLexer.h"
#include "SysYParser.h"
#include "TypeChecker.h"

using namespace antlr4;

namespace {

// ANTLR's default console listener writes to stderr, which Part 2 grades, so
// replace it with a silent listener that only counts syntax errors.
class SilentErrorListener : public BaseErrorListener {
public:
  int errorCount = 0;

  void syntaxError(Recognizer * /*recognizer*/, Token * /*offendingSymbol*/,
                   size_t /*line*/, size_t /*charPositionInLine*/,
                   const std::string & /*msg*/,
                   std::exception_ptr /*e*/) override {
    ++errorCount;
  }
};

} // namespace

// Part 2: type checking.  All diagnostics go to stderr.
int main(int argc, char *argv[]) {
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <input_file>" << std::endl;
    return 1;
  }

  std::ifstream stream(argv[1]);
  if (!stream) {
    std::cerr << "Cannot open file: " << argv[1] << std::endl;
    return 1;
  }

  ANTLRInputStream input(stream);
  SysYLexer lexer(&input);
  CommonTokenStream tokens(&lexer);
  SysYParser parser(&tokens);

  SilentErrorListener errors;
  lexer.removeErrorListeners();
  lexer.addErrorListener(&errors);
  parser.removeErrorListeners();
  parser.addErrorListener(&errors);

  SysYParser::CompUnitContext *tree = parser.compUnit();
  if (errors.errorCount > 0)
    return 1;

  TypeChecker checker;
  checker.check(tree);
  return 0;
}
