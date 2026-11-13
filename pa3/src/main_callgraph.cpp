#include <fstream>
#include <iostream>
#include <string>

#include "CallGraph.h"
#include "CallGraphBuilder.h"
#include "SysYLexer.h"
#include "SysYParser.h"

using namespace antlr4;

namespace {

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

// Part 3: the Mermaid call graph goes to stdout.
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

  CallGraph graph;
  CallGraphBuilder builder(graph);
  builder.visit(tree);
  std::cout << graph.toMermaid();
  return 0;
}
