parser grammar TOMLParser;
options {
	tokenVocab = TOMLLexer;
}

toml: line* EOF;

line:
	key_value COMMENT? NL?
	| table COMMENT? NL?
	| COMMENT NL?
	| NL;

// TODO: finish me
key_value:;

// TODO: finish me
table:;

// TODO: Implement the remaining TOML syntax rules mentioned in the PA2 documentation.
