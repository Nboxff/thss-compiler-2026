import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.antlr.v4.runtime.BaseErrorListener;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.Recognizer;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.Trees;

/**
 * Test helper for PA2 Part 1.
 *
 * Usage:
 *   java ParseCheck <file.toml>            print the syntax-error count and
 *                                          the parse tree
 *   java ParseCheck --tokens <file.toml>   print the token stream instead
 *
 * The parser is driven exactly the way the OJ drives it: a TOMLLexer, a
 * CommonTokenStream, then parser.toml(). Errors are counted with a silent
 * error listener, so the number on the first line is the number of syntax
 * errors the parser reported (0 means the input is valid).
 *
 * The tree on the second line is only meant for debugging; it is not part of
 * the tests. Use --tokens to inspect the given lexer by hand.
 */
public final class ParseCheck {
  private static final class ErrorCounter extends BaseErrorListener {
    int count = 0;

    @Override
    public void syntaxError(Recognizer<?, ?> recognizer, Object offendingSymbol,
                            int line, int charPositionInLine, String msg,
                            RecognitionException e) {
      count++;
    }
  }

  public static void main(String[] args) throws Exception {
    boolean tokensOnly = args.length == 2 && args[0].equals("--tokens");
    if (!tokensOnly && args.length != 1) {
      System.err.println("usage: ParseCheck [--tokens] <file.toml>");
      System.exit(2);
    }
    String path = tokensOnly ? args[1] : args[0];

    String text =
        new String(Files.readAllBytes(Paths.get(path)), StandardCharsets.UTF_8);
    CharStream input = CharStreams.fromString(text);

    ErrorCounter errors = new ErrorCounter();
    TOMLLexer lexer = new TOMLLexer(input);
    lexer.removeErrorListeners();
    lexer.addErrorListener(errors);

    CommonTokenStream tokens = new CommonTokenStream(lexer);
    TOMLParser parser = new TOMLParser(tokens);
    parser.removeErrorListeners();
    parser.addErrorListener(errors);

    if (tokensOnly) {
      printTokens(lexer, tokens);
      return;
    }

    ParseTree tree = parser.toml();
    System.out.println("errors=" + errors.count);
    System.out.println("tree=" + Trees.toStringTree(tree, parser));
  }

  /** Same shape as TestRig's -tokens output. */
  private static void printTokens(TOMLLexer lexer, CommonTokenStream tokens) {
    tokens.fill();
    int index = 0;
    for (Token token : tokens.getTokens()) {
      String name = lexer.getVocabulary().getDisplayName(token.getType());
      System.out.printf("[@%d,%d:%d='%s',<%s>,%d:%d]%n", index++,
                        token.getStartIndex(), token.getStopIndex(),
                        escapeWhitespace(token.getText()), name,
                        token.getLine(), token.getCharPositionInLine());
    }
  }

  private static String escapeWhitespace(String text) {
    return text.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
  }
}
