%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* AST minimal */
typedef enum {
  NK_PROGRAM, NK_LIST, NK_DECL_INT, NK_DECL_STRING, NK_ASSIGN,
  NK_IF, NK_WHILE, NK_BLOCK, NK_PRINT,
  NK_OPEN, NK_PLAY, NK_PAUSE, NK_STOP, NK_SEEK, NK_FORWARD, NK_REWIND, NK_WAIT,
  NK_IDENT, NK_NUMBER, NK_STRING,
  NK_POS, NK_DUR, NK_ENDED, NK_ISPLAYING,
  NK_EQ, NK_NE, NK_LT, NK_LE, NK_GT, NK_GE,
  NK_ADD, NK_SUB, NK_MUL, NK_DIV, NK_NEG
} NodeKind;

typedef struct Node Node;
typedef struct NodeList NodeList;

struct Node {
  NodeKind kind;
  int line;
  char* sval;
  int ival;
  NodeList* kids;
};

struct NodeList {
  Node* node;
  NodeList* next;
};

static Node* mk(NodeKind k, int line, const char* s, int v, NodeList* kids) {
  Node* n = (Node*)calloc(1,sizeof(Node));
  n->kind = k; n->line=line;
  if (s) n->sval = strdup(s);
  n->ival = v;
  n->kids = kids;
  return n;
}
static NodeList* cons(Node* n, NodeList* xs) { NodeList* c=(NodeList*)malloc(sizeof(NodeList)); c->node=n; c->next=xs; return c; }
static NodeList* rev(NodeList* xs){ NodeList* r=NULL; while(xs){ NodeList* t=xs->next; xs->next=r; r=xs; xs=t;} return r; }

static void print_node(Node* n, int d){
  if(!n){ printf("%*s(null)\n",2*d,""); return;}
  static const char* K[] = {
    "PROGRAM","LIST","DECL_INT","DECL_STRING","ASSIGN",
    "IF","WHILE","BLOCK","PRINT",
    "OPEN","PLAY","PAUSE","STOP","SEEK","FORWARD","REWIND","WAIT",
    "IDENT","NUMBER","STRING",
    "POSITION","DURATION","ENDED","IS_PLAYING",
    "EQ","NE","LT","LE","GT","GE",
    "ADD","SUB","MUL","DIV","NEG"
  };
  printf("%*s%s",2*d,"", K[n->kind]);
  if(n->sval) printf(" ('%s')",n->sval);
  if(n->kind==NK_NUMBER) printf(" (%d)", n->ival);
  printf(" @%d\n", n->line);
  for(NodeList* k=n->kids;k;k=k->next) print_node(k->node,d+1);
}

static void free_ast(Node* n){
  if(!n) return;
  for(NodeList* k=n->kids;k;){
    NodeList* t=k->next;
    free_ast(k->node);
    free(k);
    k=t;
  }
  free(n->sval);
  free(n);
}

/* --- Code Generation --- */
static FILE* out = NULL;
static int label_counter = 0;
static int var_counter = 0;

typedef struct VarEntry {
  char* name;
  int addr;
  struct VarEntry* next;
} VarEntry;

static VarEntry* symtab = NULL;

static int get_var_addr(const char* name) {
  for (VarEntry* e = symtab; e; e = e->next) {
    if (strcmp(e->name, name) == 0) return e->addr;
  }
  /* create new variable */
  VarEntry* e = (VarEntry*)malloc(sizeof(VarEntry));
  e->name = strdup(name);
  e->addr = var_counter++;
  e->next = symtab;
  symtab = e;
  return e->addr;
}

static int new_label() { return label_counter++; }

static void gen_expr(Node* n);
static void gen_stmt(Node* n);

static void gen_expr(Node* n) {
  if (!n) return;
  NodeList* kids = n->kids;

  switch(n->kind) {
    case NK_NUMBER:
      fprintf(out, "PUSH %d\n", n->ival);
      break;

    case NK_IDENT: {
      int addr = get_var_addr(n->sval);
      fprintf(out, "LOAD %d\n", addr);
      break;
    }

    case NK_STRING:
      /* strings are handled specially in print/open */
      break;

    case NK_ADD:
      gen_expr(kids->node);       /* left */
      gen_expr(kids->next->node); /* right */
      fprintf(out, "ADD\n");
      break;

    case NK_SUB:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "SUB\n");
      break;

    case NK_MUL:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "MUL\n");
      break;

    case NK_DIV:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "DIV\n");
      break;

    case NK_NEG:
      gen_expr(kids->node);
      fprintf(out, "NEG\n");
      break;

    case NK_EQ:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "EQ\n");
      break;

    case NK_NE:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "NE\n");
      break;

    case NK_LT:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "LT\n");
      break;

    case NK_LE:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "LE\n");
      break;

    case NK_GT:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "GT\n");
      break;

    case NK_GE:
      gen_expr(kids->node);
      gen_expr(kids->next->node);
      fprintf(out, "GE\n");
      break;

    case NK_POS:
      fprintf(out, "GET_POS\n");
      break;

    case NK_DUR:
      fprintf(out, "GET_DUR\n");
      break;

    case NK_ENDED:
      fprintf(out, "GET_ENDED\n");
      break;

    case NK_ISPLAYING:
      fprintf(out, "GET_PLAYING\n");
      break;

    default:
      break;
  }
}

static void gen_stmt(Node* n) {
  if (!n) return;
  NodeList* kids = n->kids;

  switch(n->kind) {
    case NK_PROGRAM:
      for (NodeList* k = kids; k; k = k->next) {
        gen_stmt(k->node);
      }
      fprintf(out, "HALT\n");
      break;

    case NK_DECL_INT:
      /* optionally initialize */
      if (kids) {
        gen_expr(kids->node);  /* initial value */
        fprintf(out, "STORE %d\n", get_var_addr(n->sval));
      } else {
        fprintf(out, "PUSH 0\n");
        fprintf(out, "STORE %d\n", get_var_addr(n->sval));
      }
      break;

    case NK_DECL_STRING:
      /* strings stored as-is; we'll handle them separately if needed */
      break;

    case NK_ASSIGN:
      /* kids: [ident, expr/string] */
      if (kids && kids->next) {
        Node* lhs = kids->node;
        Node* rhs = kids->next->node;
        if (rhs->kind == NK_STRING) {
          /* ignore for now - strings are tricky in simple VM */
        } else {
          gen_expr(rhs);
          fprintf(out, "STORE %d\n", get_var_addr(lhs->sval));
        }
      }
      break;

    case NK_IF: {
      int else_label = new_label();
      int end_label = new_label();

      /* condition */
      gen_expr(kids->node);

      if (kids->next && kids->next->next) {
        /* has else branch */
        fprintf(out, "JUMPZ L%d\n", else_label);
        gen_stmt(kids->next->node);  /* then */
        fprintf(out, "GOTO L%d\n", end_label);
        fprintf(out, "L%d:\n", else_label);
        gen_stmt(kids->next->next->node);  /* else */
        fprintf(out, "L%d:\n", end_label);
      } else {
        /* no else */
        fprintf(out, "JUMPZ L%d\n", end_label);
        gen_stmt(kids->next->node);  /* then */
        fprintf(out, "L%d:\n", end_label);
      }
      break;
    }

    case NK_WHILE: {
      int loop_label = new_label();
      int end_label = new_label();

      fprintf(out, "L%d:\n", loop_label);
      gen_expr(kids->node);  /* condition */
      fprintf(out, "JUMPZ L%d\n", end_label);
      gen_stmt(kids->next->node);  /* body */
      fprintf(out, "GOTO L%d\n", loop_label);
      fprintf(out, "L%d:\n", end_label);
      break;
    }

    case NK_BLOCK:
      for (NodeList* k = kids; k; k = k->next) {
        gen_stmt(k->node);
      }
      break;

    case NK_PRINT:
      if (n->sval) {
        /* print string literal */
        fprintf(out, "PRINTS \"%s\"\n", n->sval);
      } else if (kids) {
        /* print expression */
        gen_expr(kids->node);
        fprintf(out, "PRINT\n");
      }
      break;

    case NK_OPEN:
      if (n->sval) {
        fprintf(out, "OPEN \"%s\"\n", n->sval);
      } else if (kids) {
        /* numeric ID - ignore for now */
      }
      break;

    case NK_PLAY:
      if (kids) {
        gen_expr(kids->node);
        fprintf(out, "POP R0\n");
        fprintf(out, "PLAY R0\n");
      } else {
        fprintf(out, "PLAY 1\n");
      }
      break;

    case NK_PAUSE:
      fprintf(out, "PAUSE\n");
      break;

    case NK_STOP:
      fprintf(out, "STOP\n");
      break;

    case NK_SEEK:
      gen_expr(kids->node);
      fprintf(out, "POP R0\n");
      fprintf(out, "SEEK R0\n");
      break;

    case NK_FORWARD:
      gen_expr(kids->node);
      fprintf(out, "POP R0\n");
      fprintf(out, "FORWARD R0\n");
      break;

    case NK_REWIND:
      gen_expr(kids->node);
      fprintf(out, "POP R0\n");
      fprintf(out, "REWIND R0\n");
      break;

    case NK_WAIT:
      gen_expr(kids->node);
      fprintf(out, "POP R0\n");
      fprintf(out, "WAIT R0\n");
      break;

    case NK_LIST:
      /* empty statement */
      break;

    default:
      break;
  }
}

/* lexer hooks */
int yylex(void);
extern int yylineno;
void yyerror(const char* s){
  fprintf(stderr,"[PARSER] error at line %d: %s\n", yylineno, s);
}
Node* g_root = NULL;
%}

/* types */
%union {
  int ival;
  char* sval;
  struct Node* node;
  struct NodeList* list;
}

/* tokens w/o values */
%token T_INT T_STRING T_IF T_ELSE T_WHILE T_PRINT
%token T_OPEN T_PLAY T_PAUSE T_STOP T_SEEK T_FORWARD T_REWIND T_WAIT
%token T_POSITION T_DURATION T_ENDED T_IS_PLAYING
%token T_EQ T_NE T_LE T_GE
%token T_ERROR

/* tokens with values */
%token <sval> T_IDENT
%token <sval> T_STRING_LIT
%token <ival> T_NUMBER

/* precedence */
%nonassoc LOWER_THAN_ELSE
%nonassoc T_ELSE

%left T_EQ T_NE
%left '<' '>' T_LE T_GE
%left '+' '-'
%left '*' '/'
%right UMINUS

/* nonterminal types */
%type <node> program decl optInitNum optInitStr
%type <node> stmt assign ifStmt whileStmt block printStmt streamStmt
%type <node> openStmt playStmt pauseStmt stopStmt seekStmt forwardStmt rewindStmt waitStmt
%type <node> expr equality relational additive term factor primary
%type <node> optExpr
%type <list> stmtlist

%%

program
    : %empty                    { $$ = mk(NK_PROGRAM, yylineno, NULL, 0, NULL); g_root = $$; }
    | stmtlist                  { $$ = mk(NK_PROGRAM, yylineno, NULL, 0, rev($1));   g_root = $$; }
    ;

stmtlist
    : stmt                      { $$ = cons($1, NULL); }
    | stmtlist stmt             { $$ = cons($2, $1); }
    ;

decl
    : T_INT T_IDENT optInitNum ';'
      { $$ = mk(NK_DECL_INT, yylineno, $2, 0, $3 ? cons($3,NULL):NULL); free($2); }
    | T_STRING T_IDENT optInitStr ';'
      { $$ = mk(NK_DECL_STRING, yylineno, $2, 0, $3 ? cons($3,NULL):NULL); free($2); }
    ;

optInitNum
    : %empty                    { $$ = NULL; }
    | '=' expr                  { $$ = $2; }
    ;

optInitStr
    : %empty                    { $$ = NULL; }
    | '=' T_STRING_LIT          { $$ = mk(NK_STRING, yylineno, $2, 0, NULL); free($2); }
    ;

stmt
    : decl                      { $$ = $1; }
    | assign ';'                { $$ = $1; }
    | ifStmt                    { $$ = $1; }
    | whileStmt                 { $$ = $1; }
    | block                     { $$ = $1; }
    | printStmt                 { $$ = $1; }
    | streamStmt                { $$ = $1; }
    | ';'                       { $$ = mk(NK_LIST, yylineno, NULL, 0, NULL); }
    ;

assign
    : T_IDENT '=' expr
      { Node* id=mk(NK_IDENT,yylineno,$1,0,NULL);
        $$=mk(NK_ASSIGN,yylineno,NULL,0,rev(cons($3,cons(id,NULL))));
        free($1); }
    | T_IDENT '=' T_STRING_LIT
      { Node* id=mk(NK_IDENT,yylineno,$1,0,NULL);
        Node* s=mk(NK_STRING,yylineno,$3,0,NULL);
        $$=mk(NK_ASSIGN,yylineno,NULL,0,rev(cons(s,cons(id,NULL))));
        free($1); free($3); }
    ;

ifStmt
    : T_IF '(' expr ')' stmt %prec LOWER_THAN_ELSE
      { $$ = mk(NK_IF, yylineno, NULL, 0, rev(cons($5, cons($3, NULL)))); }
    | T_IF '(' expr ')' stmt T_ELSE stmt
      { $$ = mk(NK_IF, yylineno, NULL, 0, rev(cons($7, cons($5, cons($3, NULL))))); }
    ;

whileStmt
    : T_WHILE '(' expr ')' stmt
      { $$ = mk(NK_WHILE, yylineno, NULL, 0, rev(cons($5, cons($3, NULL)))); }
    ;

block
    : '{' '}'
      { $$ = mk(NK_BLOCK, yylineno, NULL, 0, NULL); }
    | '{' stmtlist '}'
      { $$ = mk(NK_BLOCK, yylineno, NULL, 0, $2); }
    ;

printStmt
    : T_PRINT '(' expr ')' ';'
      { $$ = mk(NK_PRINT, yylineno, NULL, 0, cons($3,NULL)); }
    | T_PRINT '(' T_STRING_LIT ')' ';'
      { $$ = mk(NK_PRINT, yylineno, $3, 0, NULL); free($3); }
    ;

/* streaming commands */
streamStmt
    : openStmt                  { $$ = $1; }
    | playStmt                  { $$ = $1; }
    | pauseStmt                 { $$ = $1; }
    | stopStmt                  { $$ = $1; }
    | seekStmt                  { $$ = $1; }
    | forwardStmt               { $$ = $1; }
    | rewindStmt                { $$ = $1; }
    | waitStmt                  { $$ = $1; }
    ;

openStmt
    : T_OPEN '(' T_STRING_LIT ')' ';'
      { $$ = mk(NK_OPEN, yylineno, $3, 0, NULL); free($3); }
    | T_OPEN '(' expr ')' ';'
      { $$ = mk(NK_OPEN, yylineno, NULL, 0, cons($3,NULL)); }
    ;

optExpr
    : %empty                    { $$ = NULL; }
    | expr                      { $$ = $1; }
    ;

playStmt
    : T_PLAY '(' optExpr ')' ';'
      { $$ = mk(NK_PLAY, yylineno, NULL, 0, $3?cons($3,NULL):NULL); }
    ;

pauseStmt
    : T_PAUSE '(' ')' ';'
      { $$ = mk(NK_PAUSE, yylineno, NULL, 0, NULL); }
    ;

stopStmt
    : T_STOP '(' ')' ';'
      { $$ = mk(NK_STOP, yylineno, NULL, 0, NULL); }
    ;

seekStmt
    : T_SEEK '(' expr ')' ';'
      { $$ = mk(NK_SEEK, yylineno, NULL, 0, cons($3,NULL)); }
    ;

forwardStmt
    : T_FORWARD '(' expr ')' ';'
      { $$ = mk(NK_FORWARD, yylineno, NULL, 0, cons($3,NULL)); }
    ;

rewindStmt
    : T_REWIND '(' expr ')' ';'
      { $$ = mk(NK_REWIND, yylineno, NULL, 0, cons($3,NULL)); }
    ;

waitStmt
    : T_WAIT '(' expr ')' ';'
      { $$ = mk(NK_WAIT, yylineno, NULL, 0, cons($3,NULL)); }
    ;

/* expressions */
expr
    : equality                  { $$ = $1; }
    ;

equality
    : relational                { $$ = $1; }
    | equality T_EQ relational  { $$ = mk(NK_EQ, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    | equality T_NE relational  { $$ = mk(NK_NE, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    ;

relational
    : additive                  { $$ = $1; }
    | relational '<'  additive  { $$ = mk(NK_LT, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    | relational '>'  additive  { $$ = mk(NK_GT, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    | relational T_LE additive  { $$ = mk(NK_LE, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    | relational T_GE additive  { $$ = mk(NK_GE, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    ;

additive
    : term                      { $$ = $1; }
    | additive '+' term         { $$ = mk(NK_ADD, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    | additive '-' term         { $$ = mk(NK_SUB, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    ;

term
    : factor                    { $$ = $1; }
    | term '*' factor           { $$ = mk(NK_MUL, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    | term '/' factor           { $$ = mk(NK_DIV, yylineno, NULL, 0, rev(cons($3, cons($1,NULL)))); }
    ;

factor
    : primary                   { $$ = $1; }
    | '-' factor %prec UMINUS   { $$ = mk(NK_NEG, yylineno, NULL, 0, cons($2,NULL)); }
    ;

primary
    : T_NUMBER                  { $$ = mk(NK_NUMBER, yylineno, NULL, $1, NULL); }
    | T_IDENT                   { $$ = mk(NK_IDENT,  yylineno, $1, 0, NULL); free($1); }
    | '(' expr ')'              { $$ = $2; }
    | T_POSITION '(' ')'        { $$ = mk(NK_POS, yylineno, NULL, 0, NULL); }
    | T_DURATION '(' ')'        { $$ = mk(NK_DUR, yylineno, NULL, 0, NULL); }
    | T_ENDED '(' ')'           { $$ = mk(NK_ENDED, yylineno, NULL, 0, NULL); }
    | T_IS_PLAYING '(' ')'      { $$ = mk(NK_ISPLAYING, yylineno, NULL, 0, NULL); }
    ;

%%

int main(int argc, char** argv){
  int ret = yyparse();
  if(ret==0){
    puts("[OK] parsing concluído.");

    /* Generate assembly code */
    const char* outfile = "output.asm";
    if (argc > 1) {
      outfile = argv[1];
    }

    out = fopen(outfile, "w");
    if (!out) {
      fprintf(stderr, "[ERROR] Cannot open output file: %s\n", outfile);
      return 1;
    }

    fprintf(out, "; StreamLang Assembly - Generated Code\n\n");
    gen_stmt(g_root);
    fclose(out);

    printf("[OK] Assembly code generated: %s\n", outfile);

    /* Optional: print AST for debugging */
    /* print_node(g_root, 0); */
  }
  free_ast(g_root);
  return ret;
}
