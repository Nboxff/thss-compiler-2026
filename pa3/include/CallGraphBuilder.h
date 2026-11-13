#pragma once

#include <any>
#include <string>

#include "CallGraph.h"
#include "SysYParserBaseVisitor.h"

class CallGraphBuilder : public SysYParserBaseVisitor {
public:
  explicit CallGraphBuilder(CallGraph &graph) : graph_(graph) {}

  // TODO: You need to implement the visitor methods for building the call
  // graph.

private:
  // TODO: You may add private helper methods or member variables if needed.
};
