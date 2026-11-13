import org.antlr.v4.runtime.*;

/** Count syntax errors reported while parsing a SysY source file. */
public class ParseCheck {
    public static void main(String[] args) throws Exception {
        CharStream input = CharStreams.fromFileName(args[0]);
        SysYLexer lexer = new SysYLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        SysYParser parser = new SysYParser(tokens);
        final int[] errors = {0};
        BaseErrorListener listener = new BaseErrorListener() {
            @Override
            public void syntaxError(Recognizer<?, ?> recognizer, Object offendingSymbol,
                                    int line, int charPositionInLine, String msg,
                                    RecognitionException e) {
                errors[0]++;
            }
        };
        lexer.removeErrorListeners();
        lexer.addErrorListener(listener);
        parser.removeErrorListeners();
        parser.addErrorListener(listener);
        parser.compUnit();
        System.out.println("errors=" + errors[0]);
    }
}
