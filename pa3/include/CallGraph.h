#pragma once

#include <set>
#include <string>
#include <utility>
#include <vector>

class CallGraph {
public:
  void addNode(const std::string &name);
  void addEdge(const std::string &caller, const std::string &callee);

  // Produce the Mermaid document.  Ends with exactly one '\n'.
  std::string toMermaid() const;

private:
  // TODO: You need to design the data structure for storing the CallGraph.
};
