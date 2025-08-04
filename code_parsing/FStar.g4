grammar FStar;

// ----------------- Lexer rules -----------------
fragment DIGIT: [0-9];
fragment LETTER: [a-zA-Z];

// Keywords (not complete)
MODULE: 'module';
OPEN: 'open';
LETSTAROPTION: 'let*?';
LETOPTION: 'let?';
LETSTAR: 'let*';
LET: 'let';
REC: 'rec';
IN: 'in';
FUN: 'fun';
MATCH: 'match';
WITH: 'with';
TYPE: 'Type';
VAL: 'val';
ASSUME: 'assume';
IF: 'if';
THEN: 'then';
ELSE: 'else';
SOME: 'Some';
NONE: 'None';
OPTION: 'option';

// Symbols
AND_COMP: '&&';
OR_COMP: '||';
EQ_COMP: '==';

ARROW: '->';
EQ: '=';
COLON: ':';
SEMICOLONSTAROPTION: ';*?';
SEMICOLONSTAR: ';*';
SEMICOLONOPTION: ';?';
SEMICOLON: ';';
COMMA: ',';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
AND: '&';
PIPE: '|';
UNDERSCORE: '_';

ID: LETTER (LETTER | DIGIT | '_')*;
INT: DIGIT+;

// Literals
STRING: '"' ( ~["\\] | '\\' . )* '"';
CHAR: '\'' . '\'';

WS: [ \t\r\n]+;
LINE_COMMENT: '//' ~[\r\n]*;
BLOCK_COMMENT: '(*' .*? '*)';
Z3_OPTIONS: '#' .*? '\n';

// ----------------- Parser rules -----------------

program: moduleDecl WS (topLevelDecl WS?)* EOF;

qualifiedName: ID ('.' ID)*;

moduleDecl: MODULE WS qualifiedName;

openDecl: OPEN WS qualifiedName (WS LBRACE WS ID (COMMA WS ID)* WS RBRACE)?;

topLevelDecl: openDecl | letDecl | assumeDecl | valDecl | Z3_OPTIONS | LINE_COMMENT | BLOCK_COMMENT;

letDecl: LET WS (REC WS)? ID WS params (COLON WS typeExpr WS)? EQ WS expr;

assumeDecl: ASSUME ID COLON typeExpr;

valDecl: VAL WS ID WS? COLON WS? typeExpr;

param
    : LPAREN WS? ID WS? COLON WS? typeExpr WS? RPAREN
    | ID
    ;

params: (param WS)+;

typeExpr
    : TYPE
    | ID
    | OPTION WS typeExpr
    | ID WS? AND WS? ID
    | ID WS? typeExpr
    | LPAREN WS? typeExpr WS? RPAREN
    | typeExpr WS? ARROW WS? typeExpr
    ;

letOptions: LETSTAROPTION | LETOPTION | LETSTAR | LET;

semicolonOptions: SEMICOLON | SEMICOLONSTAR | SEMICOLONOPTION | SEMICOLONSTAROPTION;

expr
    :  ID
    | STRING
    | INT
    | UNDERSCORE
    | CHAR
    | qualifiedName
    | NONE
    | SOME WS? expr
    | expr WS? EQ WS? expr
    | expr WS? AND_COMP WS? expr
    | expr WS? OR_COMP WS? expr
    | expr WS? semicolonOptions
    | letOptions WS expr WS? EQ WS? expr WS? IN
    | expr WS? expr
    | expr WS? EQ WS? expr
    | expr WS? COMMA WS? expr
    | LPAREN WS? expr? WS? RPAREN
    | LBRACE (WS? ID WS? EQ WS? expr WS? SEMICOLON? WS?)+ RBRACE
    | LBRACE WS? ID WS? WITH (WS? ID WS? EQ WS? expr WS? SEMICOLON? WS?)+ RBRACE
    | expr WS? ARROW WS? expr
    | IF WS expr WS? THEN WS? expr WS? ELSE WS? expr
    | FUN WS? (param)+ WS? ARROW WS? expr
    | MATCH WS qualifiedName WS WITH WS? (PIPE WS? expr WS? ARROW WS? expr WS?)+
    ;
