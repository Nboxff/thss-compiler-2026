#include "TOMLFormatter.h"

#include "TOMLParser.h"

namespace {

std::size_t countNewlines(const std::string &text) {
  std::size_t count = 0;
  for (char c : text) {
    if (c == '\n')
      ++count;
  }
  return count;
}

// You can add some helper functions here if you want, e.g. for indentation or
// trimming whitespace.

} // namespace

std::any TOMLFormatter::visitToml(TOMLParser::TomlContext *ctx) {
  // TODO: Finish me.
}

std::any TOMLFormatter::visitLine(TOMLParser::LineContext *ctx) {
  // TODO: Finish me.
}

// key_value: key EQUALS value
std::any TOMLFormatter::visitKey_value(TOMLParser::Key_valueContext *ctx) {
  std::string key = std::any_cast<std::string>(visitKey(ctx->key()));
  std::string value = std::any_cast<std::string>(visitValue(ctx->value()));
  return key + " = " + value;
}

// table: standard_table | array_table
std::any TOMLFormatter::visitTable(TOMLParser::TableContext *ctx) {
  // TODO: Finish me.
}

// TODO: Implement the remaining visit methods for the other rules in the
// grammar, such as visitStandard_table, visitArray_table, visitKey, visitValue,
// etc.
