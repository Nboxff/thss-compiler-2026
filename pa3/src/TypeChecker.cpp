#include "TypeChecker.h"

#include <iostream>
#include <vector>

#include "SysYParser.h"

void TypeChecker::check(SysYParser::CompUnitContext *ctx) {
  visit(ctx);
  // TODO: If no error was reported, the program is valid.
}

// TODO: You need to implement the visitor methods for type checking. You may
// also add private helper methods or member variables if needed.
