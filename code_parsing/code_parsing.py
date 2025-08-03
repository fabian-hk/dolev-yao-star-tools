from pathlib import Path

import antlr4
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from FStarLexer import FStarLexer
from FStarParser import FStarParser
from FStarParser import FStarParser  # Redundant but safe for some linters
from FStarVisitor import FStarVisitor
from FStarListener import FStarListener



import sys

# Generate parsers: antlr4 -Dlanguage=Python3 FStar.g4

class ASTPrinter(antlr4.ParseTreeListener):
    def enterLetDecl(self, ctx):
        print(f"[Let Decl] {ctx.getText()}")
        for param in ctx.params().param():
            print(f"[Param] {param.getText()}")

    def enterAssumeDecl(self, ctx):
        print(f"[Assume Decl] {ctx.getText()}")

    def enterValDecl(self, ctx):
        print(f"[Val Decl] {ctx.getText()}")

    def enterModuleDecl(self, ctx):
        print(f"[Module Decl] {ctx.getText()}")
        
    def enterOpenDecl(self, ctx):
        print(f"[Open Decl]: {ctx.getText()}")

class ProgramRewriter(FStarVisitor):

    def visitParam(self, ctx):
        print(f"[Param] {ctx.getText()}")
        if ctx.getText() == "authorization_server":
            print("Modify")
            return "auth_server"
        return ctx.getText()
    


def parse_fstar_file():
    # Load input file
    input_stream = antlr4.FileStream("Test1.Test.fst", encoding='utf-8')

    # Lexer & Parser
    lexer = FStarLexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)

    parser = FStarParser(token_stream)
    #parser.addErrorListener(antlr4.DiagnosticErrorListener())

    # Parse the top-level rule from grammar
    tree = parser.program()
    rewriter = TokenStreamRewriter(token_stream)
    
    class ParamChanger(FStarListener):
        def exitParam(self, ctx):
            if ctx.getText() == "authorization_server":
                rewriter.replaceRange(ctx.start.tokenIndex, ctx.stop.tokenIndex, "auth_server")

    walker = antlr4.ParseTreeWalker()
    walker.walk(ParamChanger(), tree)
    print(rewriter.getDefaultText())

    #for topLevelDecl in tree.topLevelDecl():
    #   print(f"[TopLevelDecl] {topLevelDecl.getText()}")
    #    if topLevelDecl.letDecl():
    #        ctx = topLevelDecl.letDecl()
    #        ctx.params().param()[0].setText("auth_server")
    #        print(f"[LetDecl] {ctx.getText()}")




    # Walk parse tree
    #walker = antlr4.ParseTreeWalker()
    #printer = ASTPrinter()
    #walker.walk(printer, tree)

parse_fstar_file()



def test(source):
    lexer = FStarLexer(antlr4.InputStream(source))
    token_stream = antlr4.CommonTokenStream(lexer)
    token_stream.fill()

    print(f"input: {source}")

    for token in [t for t in token_stream.tokens if t.type != -1]:
        print(f"  {lexer.symbolicNames[token.type].ljust(20)}{token.text}")

    print("************* Parser *************")
    parser = FStarParser(token_stream)

    # Parse the top-level rule from grammar
    tree = parser.program()

    # Walk parse tree
    walker = antlr4.ParseTreeWalker()
    printer = ASTPrinter()
    walker.walk(printer, tree)


# test("module Test1.Test")