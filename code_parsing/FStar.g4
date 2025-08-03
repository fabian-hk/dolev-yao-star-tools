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

WS: [ \t\r\n]*;
LINE_COMMENT: '//' ~[\r\n]*;
BLOCK_COMMENT: '(*' .*? '*)';
Z3_OPTIONS: '#' .*? '\n';

// ----------------- Parser rules -----------------

program: moduleDecl WS (topLevelDecl WS)* EOF;

qualifiedName: ID ('.' ID)*;

moduleDecl: MODULE WS qualifiedName;

openDecl: OPEN WS qualifiedName (WS LBRACE WS ID (COMMA WS ID)* WS RBRACE)?;

topLevelDecl: openDecl | letDecl | assumeDecl | valDecl | Z3_OPTIONS | LINE_COMMENT | BLOCK_COMMENT;

letDecl: LET WS (REC WS)? ID WS params WS (COLON WS typeExpr WS)? EQ WS expr;

assumeDecl: ASSUME ID COLON typeExpr;

valDecl: VAL WS ID WS COLON WS typeExpr;

param
    : LPAREN ID COLON typeExpr RPAREN
    | ID
    ;

params: param+;

typeExpr
    : TYPE
    | ID
    | OPTION typeExpr
    | ID AND ID
    | ID typeExpr
    | LPAREN typeExpr RPAREN
    | typeExpr ARROW typeExpr
    ;

letOptions: LETSTAROPTION | LETOPTION | LETSTAR | LET;

expr
    :  ID
    | STRING
    | UNDERSCORE
    | CHAR
    | qualifiedName
    | NONE
    | SOME expr
    | expr EQ expr
    | expr AND_COMP expr
    | expr OR_COMP expr
    | letOptions qualifiedName EQ expr IN
    | expr expr
    | LPAREN expr RPAREN
    | expr ARROW expr
    | IF expr THEN expr ELSE expr
    | FUN (param)+ ARROW expr
    | MATCH qualifiedName WITH (PIPE expr ARROW expr)+
    ;
