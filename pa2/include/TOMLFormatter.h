#pragma once

#include <any>
#include <cstddef>

#include "TOMLParserBaseVisitor.h"

// TOMLFormatter walks the TOML parse tree and regenerates the document
// according to the formatting rules of this assignment.
//
// Every visit* method uniformly returns the formatted text of its node as
// std::string, so the entry point can simply use
// std::any_cast<std::string>(formatter.visit(tree)) to get the result.
class TOMLFormatter : public TOMLParserBaseVisitor {
public:
  std::any visitToml(TOMLParser::TomlContext *ctx) override;
  std::any visitLine(TOMLParser::LineContext *ctx) override;
  std::any visitKey_value(TOMLParser::Key_valueContext *ctx) override;
  std::any visitTable(TOMLParser::TableContext *ctx) override;
  // TODO: finish me

private:
  std::size_t indentLevel_ = 0;
};
