# StreamLang
## Linguagem de Programação para Controle de Streaming

**Aluno:** Samuel Jabes
**Disciplina:** Lógica da Computação
**Data:** Dezembro 2025

---

## Motivação

### Por que StreamLang?

- **Problema**: Controlar reprodução de vídeos/mídia requer uso de APIs complexas
- **Solução**: Linguagem de alto nível específica para streaming
- **Objetivo**: Simplificar automação de testes, demos e controle de mídia

### Casos de Uso

1. **Testes automatizados** de players de vídeo
2. **Scripts de demonstração** para apresentações
3. **Automação de controle** de mídia em sistemas embarcados
4. **Prototipagem rápida** de comportamentos de streaming

---

## Características da Linguagem

### Sintaxe Familiar
- Baseada em C/Java para facilitar adoção
- Tipos: `int` e `string`
- Estruturas de controle: `if/else`, `while`

### Comandos Específicos de Streaming
```streamlang
open("video.mp4");    // Abrir vídeo
play();               // Reproduzir
pause();              // Pausar
stop();               // Parar
seek(30);             // Ir para posição (segundos)
forward(10);          // Avançar 10s
rewind(5);            // Voltar 5s
wait(2);              // Aguardar 2s
```

### Built-ins de Consulta
```streamlang
position()      // Posição atual (s)
duration()      // Duração total (s)
ended()         // 1 se terminou, 0 caso contrário
is_playing()    // 1 se tocando, 0 caso contrário
```

---

## Exemplo de Código

```streamlang
// Declarações
int target_pos = 120;
string video_name = "Tutorial";

// Abrir e reproduzir
open(video_name);
play();

// Loop até atingir posição alvo
while (position() < target_pos) {
    wait(1);

    if (position() >= 60) {
        print("Metade do caminho!");
    }
}

// Pausar quando atingir alvo
pause();
print("Posição final:");
print(position());
```

---

## Arquitetura do Compilador

### Pipeline de Compilação

```
┌──────────────┐
│ Código .sl   │
│ (StreamLang) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Análise      │
│ Léxica       │  ← Flex
│ (streamlang.l)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Análise      │
│ Sintática    │  ← Bison
│(streamlang.y)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Geração AST  │
│ (C/structs)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Geração de   │
│ Código       │
│ Assembly     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Arquivo .asm │
│ (StreamVM)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ StreamVM     │
│ (Python)     │  ← Interpretador
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Execução     │
└──────────────┘
```

---

## StreamVM - Máquina Virtual

### Arquitetura Turing-Completa

**Registradores:**
- `POS` - Posição atual do vídeo
- `SPEED` - Velocidade de reprodução
- `R0`, `R1` - Registradores de propósito geral

**Memória:**
- 256 células de memória
- Pilha para expressões

**Sensores (Readonly):**
- `DURATION` - Duração do vídeo
- `IS_PLAYING` - Status de reprodução
- `ENDED` - Flag de fim

### Conjunto de Instruções

#### Pilha
```assembly
PUSH n         ; empilha literal ou registrador
POP R          ; desempilha para registrador
LOAD addr      ; empilha memory[addr]
STORE addr     ; desempilha para memory[addr]
```

#### Aritmética
```assembly
ADD, SUB, MUL, DIV, NEG
EQ, NE, LT, LE, GT, GE
```

#### Controle de Fluxo (Turing-Complete!)
```assembly
GOTO label     ; pulo incondicional
JUMPZ label    ; pula se pilha == 0
JUMPI label    ; pula se pilha != 0
DECJZ R label  ; decrementa R, pula se zero
```

#### Streaming
```assembly
OPEN "video"
PLAY speed
PAUSE
STOP
SEEK pos
FORWARD delta
REWIND delta
WAIT time
```

#### Sensores
```assembly
GET_POS
GET_DUR
GET_ENDED
GET_PLAYING
```

#### I/O
```assembly
PRINT          ; imprime topo da pilha
PRINTS "text"  ; imprime string
HALT           ; para execução
```

---

## Exemplo de Assembly Gerado

### Código StreamLang:
```streamlang
int timer = 5;
open("Video");
play();
wait(timer);
pause();
```

### Assembly Gerado:
```assembly
; StreamLang Assembly - Generated Code

PUSH 5
STORE 0         ; timer = 5
OPEN "Video"
PLAY 1
LOAD 0          ; carrega timer
POP R0
WAIT R0         ; wait(timer)
PAUSE
HALT
```

---

## Prova de Turing-Completude

### Instrução DECJZ

A instrução `DECJZ R label` torna a VM Turing-completa:

```assembly
; Countdown de 5 até 0
PUSH 5
POP R0

loop:
    PUSH R0
    PRINT
    DECJZ R0 done    ; Se R0 == 0: vai para done
                     ; Senão: R0 := R0 - 1
    GOTO loop

done:
    HALT
```

**Saída:**
```
5
4
3
2
1
0
```

### Equivalência a Minsky Machine

A combinação de:
- `DECJZ` (decrementa e testa zero)
- `GOTO` (pulo incondicional)
- Registradores

É equivalente a uma **Counter Machine** (Minsky Machine), provadamente Turing-completa.

---

## EBNF da Linguagem

```ebnf
program    = { decl | stmt } ;

decl       = "int" ident [ "=" expr ] ";"
           | "string" ident [ "=" string ] ";" ;

stmt       = assign ";"
           | ifStmt
           | whileStmt
           | block
           | printStmt
           | streamStmt
           | ";" ;

assign     = ident "=" (expr | string) ;

ifStmt     = "if" "(" expr ")" stmt [ "else" stmt ] ;
whileStmt  = "while" "(" expr ")" stmt ;
block      = "{" { stmt } "}" ;
printStmt  = "print" "(" (expr | string) ")" ";" ;

streamStmt = openStmt | playStmt | pauseStmt | stopStmt
           | seekStmt | forwardStmt | rewindStmt | waitStmt ;

openStmt   = "open" "(" string ")" ";" ;
playStmt   = "play" "(" [ expr ] ")" ";" ;
pauseStmt  = "pause" "(" ")" ";" ;
stopStmt   = "stop" "(" ")" ";" ;
seekStmt   = "seek" "(" expr ")" ";" ;
forwardStmt= "forward" "(" expr ")" ";" ;
rewindStmt = "rewind" "(" expr ")" ";" ;
waitStmt   = "wait" "(" expr ")" ";" ;

expr       = equality ;
equality   = relational { ("==" | "!=") relational } ;
relational = additive { ("<" | "<=" | ">" | ">=") additive } ;
additive   = term { ("+" | "-") term } ;
term       = factor { ("*" | "/") factor } ;
factor     = [ "-" ] primary ;

primary    = number
           | ident
           | "(" expr ")"
           | "position" "(" ")"
           | "duration" "(" ")"
           | "ended" "(" ")"
           | "is_playing" "(" ")" ;
```

---

## Ferramentas Utilizadas

### Análise Léxica e Sintática
- **Flex** - Gerador de analisadores léxicos
- **Bison** - Gerador de parsers LALR
- **GCC** - Compilador C para o código gerado

### Máquina Virtual
- **Python 3** - Implementação da StreamVM
- Design baseado em VMs educacionais (ex: MicrowaveVM do prof.)

### Desenvolvimento
- **Git** - Controle de versão
- **Make** - Automação de build
- **VSCode** - Editor

---

## Como Usar

### 1. Compilar o Compilador
```bash
make
```

### 2. Escrever Programa StreamLang
```streamlang
// meu_programa.sl
open("Meu Video");
play();
wait(10);
pause();
```

### 3. Compilar para Assembly
```bash
./streamlang output.asm < meu_programa.sl
```

### 4. Executar na VM
```bash
python3 streamvm.py output.asm
```

### Saída:
```
[STREAM] Opened video: 'Meu Video'
[STREAM] Playing at speed 1x
[STREAM] Waited 10s (now at 10s)
[STREAM] Paused at position 10s
[VM] Execution halted
```

---

## Estrutura do Repositório

```
StreamLang/
├── README.md              # Documentação principal
├── APRESENTACAO.md        # Esta apresentação
├── Makefile               # Build automation
│
├── streamlang.l           # Especificação léxica (Flex)
├── streamlang.y           # Gramática e codegen (Bison)
├── streamvm.py            # Máquina virtual (Python)
│
├── examples/              # Programas de exemplo
│   ├── demo.sl
│   ├── simple_demo.sl
│   ├── test_if_simple.sl
│   └── ...
│
└── output.asm             # Assembly gerado (exemplo)
```

---

## Diferencial Técnico

### ✅ VM Própria Criada
- **+1 conceito** conforme especificação da APS
- Design customizado para domínio de streaming
- Instruções específicas (OPEN, PLAY, etc.)

### ✅ Turing-Completude
- Prova formal via DECJZ + GOTO
- Equivalência a Counter Machines

### ✅ Compilador Completo
- Análise léxica (Flex)
- Análise sintática (Bison)
- Geração de código (C)
- Interpretador funcional (Python)

### ✅ Documentação Completa
- EBNF formal
- Exemplos funcionais
- Instruções de uso

---

## Testes e Validação

### Casos de Teste Implementados

1. **test_simple.sl** - Comandos básicos
2. **test_if_simple.sl** - Condicional simples
3. **test_if_else.sl** - If com else
4. **test_if_block.sl** - Blocos em condicionais
5. **demo.sl** - Demonstração completa
6. **simple_demo.sl** - Exemplo didático

### Validação

Todos os testes executam corretamente:
- ✅ Parsing sem erros
- ✅ Geração de assembly válido
- ✅ Execução na VM com resultados esperados

---

## Curiosidades e Insights

### 1. Domínio Específico
StreamLang é uma **DSL** (Domain-Specific Language) - linguagens especializadas são mais eficientes que linguagens gerais para problemas específicos.

### 2. Sensores Readonly
A distinção entre registradores e sensores simula hardware real de dispositivos de streaming.

### 3. Abstração de Tempo
O comando `wait()` abstrai a complexidade de sincronização temporal em sistemas de streaming.

### 4. Stack-Based VM
A VM usa arquitetura de pilha para expressões, similar a JVM e CLR (.NET).

### 5. Label-Based Control Flow
O uso de labels para controle de fluxo é similar a bytecode de linguagens modernas (Java, Python).

---

## Possíveis Extensões Futuras

### Funcionalidades
- [ ] Suporte a playlists
- [ ] Legendas e áudio tracks
- [ ] Filtros e efeitos (brilho, contraste)
- [ ] Callbacks e eventos
- [ ] Streaming de rede (URLs)

### Otimizações
- [ ] Otimização de código (constant folding)
- [ ] JIT compilation para performance
- [ ] Garbage collection para strings

### Ferramentas
- [ ] Debugger interativo
- [ ] Profiler de execução
- [ ] LSP (Language Server Protocol) para IDEs

---

## Conclusão

### Objetivos Alcançados ✅

1. ✅ Linguagem estruturada segundo EBNF
2. ✅ Análise Léxica e Sintática (Flex/Bison)
3. ✅ VM Turing-completa customizada
4. ✅ Exemplos de teste funcionais
5. ✅ Apresentação documentada

### Conceito Esperado: **A+ (+1 por VM própria)**

### Aprendizados

- Compreensão profunda de compiladores
- Design de linguagens de programação
- Arquitetura de máquinas virtuais
- Ferramentas de parsing (Flex/Bison)
- Importância de testes e documentação

---

## Referências

1. **Flex & Bison** - John Levine, O'Reilly Media
2. **Crafting Interpreters** - Robert Nystrom
3. **Engineering a Compiler** - Cooper & Torczon
4. **MicrowaveVM** - Exemplo do professor (repositório da disciplina)
5. **Counter Machines** - Wikipedia (Minsky Machines)
6. **EBNF Specification** - ISO/IEC 14977

---

## Contato

**GitHub:** [repositório StreamLang]
**Email:** [seu email]
**Insper:** Lógica da Computação - 7º Semestre

---

# Obrigado!

**Perguntas?**
