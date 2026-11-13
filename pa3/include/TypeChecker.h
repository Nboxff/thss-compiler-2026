#pragma once

#include <any>
#include <memory>
#include <string>
#include <vector>

#include "Scope.h"
#include "SysYParserBaseVisitor.h"
#include "Type.h"

class TypeChecker : public SysYParserBaseVisitor {
public:
  TypeChecker();

  // Run the analysis over a compUnit tree and emit the diagnostics.
  void check(SysYParser::CompUnitContext *ctx);

  // TODO: You need to implement the visitor methods for type checking.
  // You may also add private helper methods or member variables if needed.
};
