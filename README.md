# StreamLang
Linguagem de Programação para Controle de Streaming de Vídeos

## Visão Geral

StreamLang é uma linguagem de programação de alto nível projetada especificamente para controlar reprodução de mídia/vídeos. Possui sintaxe familiar (baseada em C/Java) e comandos específicos para streaming.

**Características:**
- Compilador completo (Flex + Bison)
- Máquina Virtual própria (StreamVM) - Turing-completa
- Comandos nativos de streaming (open, play, pause, seek, etc.)
- Sensores de estado (position, duration, ended, is_playing)

## Requisitos

### Dependências Necessárias

- **Flex** (analisador léxico)
- **Bison** (analisador sintático)
- **GCC** (compilador C)
- **Make** (automação de build)
- **Python 3** (para executar a VM)

### Instalação no Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install flex bison gcc make python3
```

## Guia de Uso Completo

### 1. Compilar o Compilador StreamLang

```bash
make
```

Para limpar os arquivos gerados:

```bash
make clean
```

### 2. Escrever um Programa StreamLang

Crie um arquivo `.sl`:

```streamlang
// meu_programa.sl
int tempo = 10;

open("Meu Video");
play();
wait(tempo);

if (position() >= 10) {
    print("Já passou 10 segundos!");
}

pause();
```

### 3. Compilar para Assembly

```bash
./streamlang output.asm < meu_programa.sl
```

Isso gera um arquivo `output.asm` com o código assembly da StreamVM.

### 4. Executar na StreamVM

```bash
python3 streamvm.py output.asm
```

### Pipeline Completo (Exemplo)

```bash
# 1. Compilar o compilador
make

# 2. Compilar programa StreamLang para assembly
./streamlang output.asm < examples/simple_demo.sl

# 3. Executar na VM
python3 streamvm.py output.asm
```

### Script de Compilação e Execução Rápida

```bash
# Criar um script run.sh
echo './streamlang output.asm < $1 && python3 streamvm.py output.asm' > run.sh
chmod +x run.sh

# Usar
./run.sh examples/simple_demo.sl
```

### Exemplo de Programa

```streamlang
// Declarações de variáveis
int pos = 0;
string title = "Meu Video";

// Comandos de streaming
open("Trailer 1");
play();
wait(5);
pause();

// Controle de fluxo
if (is_playing() == 1) {
    print("Video em execução");
} else {
    print("Video pausado");
}

// Loop
while (ended() == 0) {
    pos = position();
    if (pos >= 120) {
        stop();
    }
}
```

Veja mais exemplos em [examples/](examples/).

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
