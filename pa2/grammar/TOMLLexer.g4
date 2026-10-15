lexer grammar TOMLLexer;

// whitespace, newline and comment
WS      : [ \t]+        -> skip ;
NL      : ('\r'? '\n')+ ;
COMMENT : '#' ~[\r\n]* ;

// delimiters
L_BRACKET : '[' ;
R_BRACKET : ']' ;
L_BRACE   : '{' ;
R_BRACE   : '}' ;
EQUALS    : '=' ;
DOT       : '.' ;
COMMA     : ',' ;

// value keywords: must precede UNQUOTED_KEY
BOOLEAN : 'true' | 'false' ;
INF     : [+-]? 'inf' ;
NAN     : [+-]? 'nan' ;

// numbers: also must precede UNQUOTED_KEY
fragment DIGIT     : [0-9] ;
fragment ALPHA     : [A-Za-z] ;
fragment HEX_DIGIT : [A-Fa-f] | DIGIT ;

fragment ZERO_PREFIXABLE_INT : DIGIT (DIGIT | '_' DIGIT)* ;
fragment FRAC                : '.' ZERO_PREFIXABLE_INT ;
fragment EXP                 : ('e' | 'E') [+-]? ZERO_PREFIXABLE_INT ;
fragment DIGIT_1_9           : [1-9] ;
fragment DIGIT_0_7           : [0-7] ;
fragment DIGIT_0_1           : [0-1] ;

FLOAT   : DEC_INT (FRAC EXP? | EXP) ;
DEC_INT : [+-]? (DIGIT | DIGIT_1_9 (DIGIT | '_' DIGIT)*) ;
HEX_INT : '0x' HEX_DIGIT (HEX_DIGIT | '_' HEX_DIGIT)* ;
OCT_INT : '0o' DIGIT_0_7 (DIGIT_0_7 | '_' DIGIT_0_7)* ;
BIN_INT : '0b' DIGIT_0_1 (DIGIT_0_1 | '_' DIGIT_0_1)* ;

// strings: valid both as keys and as values
fragment UNICODE : 'u' HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT ;
fragment ESC     : '\\' (["\\/bfnrt] | UNICODE) ;
BASIC_STRING     : '"' (ESC | ~["\\\r\n])* '"' ;
LITERAL_STRING   : '\'' ~['\r\n]* '\'' ;

// bare key: must come last
UNQUOTED_KEY : (ALPHA | DIGIT | '-' | '_')+ ;
