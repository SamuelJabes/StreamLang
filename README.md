# StreamLang
Linguagem para Streaming

## EBNF

```bash
program         = { decl | stmt } ;

decl            = "int" ident [ "=" expr ] ";" 
                | "string" ident [ "=" string ] ";" ;

stmt            = assign ";" 
                | ifStmt 
                | whileStmt 
                | block
                | printStmt
                | streamStmt
                | ";" ;

assign          = ident "=" (expr | string) ;

ifStmt          = "if" "(" expr ")" stmt [ "else" stmt ] ;
whileStmt       = "while" "(" expr ")" stmt ;
block           = "{" { stmt } "}" ;
printStmt       = "print" "(" (expr | string) ")" ";" ;

(* ---- Streaming commands ---- *)
streamStmt      = openStmt | playStmt | pauseStmt | stopStmt 
                | seekStmt | forwardStmt | rewindStmt | waitStmt ;

openStmt        = "open" "(" (string | expr) ")" ";"    (* título ou id numérico *)
playStmt        = "play" "(" [ expr ] ")" ";"          (* opcional: velocidade; default 1 *)
pauseStmt       = "pause" "(" ")" ";" ;
stopStmt        = "stop" "(" ")" ";" ;
seekStmt        = "seek" "(" expr ")" ";"              (* posição absoluta em segundos *)
forwardStmt     = "forward" "(" expr ")" ";"           (* avança +expr segundos *)
rewindStmt      = "rewind" "(" expr ")" ";"            (* volta  -expr segundos *)
waitStmt        = "wait" "(" expr ")" ";"              (* aguarda expr segundos virtuais *)

(* ---- Built-ins que retornam valores ---- *)
(* usados em expr: ended(), position(), duration(), is_playing() *)
primary         = number 
                | ident 
                | "(" expr ")" 
                | "position" "(" ")" 
                | "duration" "(" ")" 
                | "ended" "(" ")" 
                | "is_playing" "(" ")" ;

(* ---- Expressões e operadores ---- *)
expr            = equality ;
equality        = relational { ("==" | "!=") relational } ;
relational      = additive  { ("<" | "<=" | ">" | ">=") additive } ;
additive        = term      { ("+" | "-" ) term } ;
term            = factor    { ("*" | "/" ) factor } ;
factor          = [ "-" ] primary ;

(* ---- Léxico ---- *)
ident           = letter { letter | digit | "_" } ;
number          = digit { digit } ;
string          = "\"" { any_char_except_quote } "\"" ;
letter          = "A"…"Z" | "a"…"z" ;
digit           = "0"…"9" ;

(* Comentários (opcional) *)
comment_line    = "//" { any_char_exc_newline } ;
comment_block   = "/*" { any_char } "*/" ;

```
