#!/usr/bin/env python3
"""
StreamVM - Máquina Virtual Turing-completa para controle de streaming de vídeos.

Arquitetura:
  - 2+ Registradores: POS (posição), SPEED (velocidade), R0, R1 (propósito geral)
  - Memória: Pilha para expressões e variáveis locais
  - Sensores Readonly: DURATION, IS_PLAYING, ENDED

Conjunto de Instruções (Turing-completa via DECJZ + GOTO):
  Operações de Pilha:
    PUSH n          ; empilha valor literal n
    POP R           ; desempilha topo para registrador R
    LOAD addr       ; empilha memory[addr]
    STORE addr      ; desempilha para memory[addr]

  Aritmética:
    ADD             ; desempilha b, a, empilha a+b
    SUB             ; desempilha b, a, empilha a-b
    MUL             ; desempilha b, a, empilha a*b
    DIV             ; desempilha b, a, empilha a/b
    NEG             ; desempilha a, empilha -a

  Comparações (empilha 1 se verdadeiro, 0 se falso):
    EQ, NE, LT, LE, GT, GE

  Controle de Fluxo (Turing-completo):
    LABEL nome      ; define alvo de salto
    GOTO label      ; salto incondicional
    JUMPZ label     ; salta se topo da pilha == 0
    JUMPI label     ; salta se topo da pilha != 0
    DECJZ R label   ; se R == 0: salta para label, senão R := R - 1

  Comandos de Streaming:
    OPEN "titulo"   ; abre vídeo por título
    PLAY speed      ; reproduz na velocidade (padrão 1)
    PAUSE           ; pausa reprodução
    STOP            ; para reprodução
    SEEK pos        ; busca posição absoluta
    FORWARD delta   ; avança delta segundos
    REWIND delta    ; retrocede delta segundos
    WAIT time       ; aguarda time segundos (simulado)

  Sensores (empilham valor na pilha):
    GET_POS         ; empilha posição atual
    GET_DUR         ; empilha duração do vídeo
    GET_ENDED       ; empilha 1 se terminou, 0 caso contrário
    GET_PLAYING     ; empilha 1 se tocando, 0 caso contrário

  I/O:
    PRINT           ; imprime topo da pilha
    PRINTS "texto"  ; imprime literal string

  Controle:
    HALT            ; para execução
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import sys

@dataclass
class Instr:
    op: str
    args: Tuple[str, ...]

class StreamVM:
    def __init__(self):
        # Registradores (escrita permitida)
        self.registers: Dict[str, int] = {
            "POS": 0,      # Posição atual em segundos
            "SPEED": 1,    # Velocidade de reprodução (1 = normal)
            "R0": 0,       # Registrador de propósito geral 0
            "R1": 0,       # Registrador de propósito geral 1
        }

        # Sensores readonly
        self.sensors: Dict[str, int] = {
            "DURATION": 0,    # Duração do vídeo em segundos
            "IS_PLAYING": 0,  # 1 se tocando, 0 se pausado/parado
            "ENDED": 0,       # 1 se vídeo terminou, 0 caso contrário
        }

        # Memória e pilha
        self.memory: List[int] = [0] * 256  # 256 células de memória
        self.stack: List[int] = []

        # Estado do vídeo
        self.video_title: str = ""
        self.video_loaded: bool = False

        # Execução do programa
        self.program: List[Instr] = []
        self.labels: Dict[str, int] = {}
        self.pc: int = 0
        self.halted: bool = False
        self.steps: int = 0

    # --- Montador / Carregador ---
    def load_program(self, source: str):
        """Carrega e analisa programa assembly"""
        self.program.clear()
        self.labels.clear()
        self.stack.clear()
        self.pc = 0
        self.halted = False
        self.steps = 0

        lines = source.splitlines()

        # Primeira passagem: coletar labels
        idx = 0
        for raw in lines:
            line = raw.split(';', 1)[0].split('#', 1)[0].strip()
            if not line:
                continue
            if line.endswith(':'):
                label = line[:-1].strip()
                if not label:
                    raise ValueError("Definição de label vazia.")
                if label in self.labels:
                    raise ValueError(f"Label duplicado: {label}")
                self.labels[label] = idx
            else:
                idx += 1

        # Segunda passagem: analisar instruções
        for raw in lines:
            line = raw.split(';', 1)[0].split('#', 1)[0].strip()
            if not line or line.endswith(':'):
                continue

            # Tratar literais string
            if '"' in line:
                # Dividir no primeiro espaço, depois tratar string entre aspas
                parts = line.split(None, 1)
                if len(parts) == 2:
                    op = parts[0].upper()
                    # Extrair literal string
                    rest = parts[1].strip()
                    if rest.startswith('"') and rest.endswith('"'):
                        args = (rest[1:-1],)  # Remover aspas
                    else:
                        args = tuple(rest.replace(',', ' ').split())
                else:
                    op = parts[0].upper()
                    args = ()
            else:
                tokens = line.replace(',', ' ').split()
                op = tokens[0].upper()
                args = tuple(tokens[1:])

            self.program.append(Instr(op, args))

    # --- Execução ---
    def step(self):
        """Executa uma instrução"""
        if self.halted:
            return
        if not (0 <= self.pc < len(self.program)):
            self.halted = True
            return

        instr = self.program[self.pc]
        self.steps += 1

        op = instr.op
        args = instr.args

        # Operações de pilha
        if op == "PUSH":
            # Suporta literal e registrador
            arg = args[0]
            if arg.upper() in self.registers:
                val = self.registers[arg.upper()]
            else:
                val = int(arg)
            self.stack.append(val)
            self.pc += 1

        elif op == "POP":
            if not self.stack:
                raise RuntimeError("Não é possível fazer POP de pilha vazia")
            reg = args[0].upper()
            self.registers[reg] = self.stack.pop()
            self.pc += 1

        elif op == "LOAD":
            addr = int(args[0])
            self.stack.append(self.memory[addr])
            self.pc += 1

        elif op == "STORE":
            if not self.stack:
                raise RuntimeError("Não é possível fazer STORE de pilha vazia")
            addr = int(args[0])
            self.memory[addr] = self.stack.pop()
            self.pc += 1

        # Aritmética
        elif op == "ADD":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
            self.pc += 1

        elif op == "SUB":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
            self.pc += 1

        elif op == "MUL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
            self.pc += 1

        elif op == "DIV":
            b = self.stack.pop()
            a = self.stack.pop()
            if b == 0:
                raise RuntimeError("Divisão por zero")
            self.stack.append(a // b)  # Divisão inteira
            self.pc += 1

        elif op == "NEG":
            a = self.stack.pop()
            self.stack.append(-a)
            self.pc += 1

        # Comparações
        elif op == "EQ":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a == b else 0)
            self.pc += 1

        elif op == "NE":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a != b else 0)
            self.pc += 1

        elif op == "LT":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a < b else 0)
            self.pc += 1

        elif op == "LE":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a <= b else 0)
            self.pc += 1

        elif op == "GT":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a > b else 0)
            self.pc += 1

        elif op == "GE":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a >= b else 0)
            self.pc += 1

        # Controle de fluxo
        elif op == "GOTO":
            label = args[0]
            if label not in self.labels:
                raise ValueError(f"Label desconhecido: {label}")
            self.pc = self.labels[label]

        elif op == "JUMPZ":
            label = args[0]
            val = self.stack.pop()
            if val == 0:
                if label not in self.labels:
                    raise ValueError(f"Label desconhecido: {label}")
                self.pc = self.labels[label]
            else:
                self.pc += 1

        elif op == "JUMPI":
            label = args[0]
            val = self.stack.pop()
            if val != 0:
                if label not in self.labels:
                    raise ValueError(f"Label desconhecido: {label}")
                self.pc = self.labels[label]
            else:
                self.pc += 1

        elif op == "DECJZ":
            reg = args[0].upper()
            label = args[1]
            if self.registers[reg] == 0:
                if label not in self.labels:
                    raise ValueError(f"Label desconhecido: {label}")
                self.pc = self.labels[label]
            else:
                self.registers[reg] -= 1
                self.pc += 1

        # Comandos de streaming
        elif op == "OPEN":
            self.video_title = args[0]
            self.video_loaded = True
            # Simular metadados do vídeo
            self.sensors["DURATION"] = 180  # 3 minutos padrão
            self.sensors["IS_PLAYING"] = 0
            self.sensors["ENDED"] = 0
            self.registers["POS"] = 0
            print(f"[STREAM] Vídeo aberto: '{self.video_title}'")
            self.pc += 1

        elif op == "PLAY":
            if not self.video_loaded:
                raise RuntimeError("Nenhum vídeo carregado")
            speed = int(args[0]) if args else 1
            self.registers["SPEED"] = speed
            self.sensors["IS_PLAYING"] = 1
            print(f"[STREAM] Reproduzindo a {speed}x")
            self.pc += 1

        elif op == "PAUSE":
            self.sensors["IS_PLAYING"] = 0
            print(f"[STREAM] Pausado na posição {self.registers['POS']}s")
            self.pc += 1

        elif op == "STOP":
            self.sensors["IS_PLAYING"] = 0
            self.registers["POS"] = 0
            print("[STREAM] Parado")
            self.pc += 1

        elif op == "SEEK":
            # Suporta literal e registrador
            arg = args[0]
            if arg.upper() in self.registers:
                pos = self.registers[arg.upper()]
            else:
                pos = int(arg)
            self.registers["POS"] = pos
            print(f"[STREAM] Buscou para {pos}s")
            self.pc += 1

        elif op == "FORWARD":
            # Suporta literal e registrador
            arg = args[0]
            if arg.upper() in self.registers:
                delta = self.registers[arg.upper()]
            else:
                delta = int(arg)
            self.registers["POS"] += delta
            print(f"[STREAM] Avançou {delta}s para posição {self.registers['POS']}s")
            self.pc += 1

        elif op == "REWIND":
            # Suporta literal e registrador
            arg = args[0]
            if arg.upper() in self.registers:
                delta = self.registers[arg.upper()]
            else:
                delta = int(arg)
            self.registers["POS"] = max(0, self.registers["POS"] - delta)
            print(f"[STREAM] Retrocedeu {delta}s para posição {self.registers['POS']}s")
            self.pc += 1

        elif op == "WAIT":
            # Suporta literal e registrador
            arg = args[0]
            if arg.upper() in self.registers:
                time = self.registers[arg.upper()]
            else:
                time = int(arg)
            if self.sensors["IS_PLAYING"]:
                self.registers["POS"] += time * self.registers["SPEED"]
                # Verificar se terminou
                if self.registers["POS"] >= self.sensors["DURATION"]:
                    self.registers["POS"] = self.sensors["DURATION"]
                    self.sensors["ENDED"] = 1
                    self.sensors["IS_PLAYING"] = 0
            print(f"[STREAM] Aguardou {time}s (agora em {self.registers['POS']}s)")
            self.pc += 1

        # Sensores
        elif op == "GET_POS":
            self.stack.append(self.registers["POS"])
            self.pc += 1

        elif op == "GET_DUR":
            self.stack.append(self.sensors["DURATION"])
            self.pc += 1

        elif op == "GET_ENDED":
            self.stack.append(self.sensors["ENDED"])
            self.pc += 1

        elif op == "GET_PLAYING":
            self.stack.append(self.sensors["IS_PLAYING"])
            self.pc += 1

        # I/O
        elif op == "PRINT":
            if not self.stack:
                raise RuntimeError("Não é possível fazer PRINT de pilha vazia")
            val = self.stack.pop()
            print(val)
            self.pc += 1

        elif op == "PRINTS":
            text = args[0]
            print(text)
            self.pc += 1

        # Controle
        elif op == "HALT":
            print("[VM] Execução finalizada")
            self.halted = True

        else:
            raise ValueError(f"Opcode desconhecido: {op}")

    def run(self, max_steps: Optional[int] = 10000):
        """Executa programa até HALT ou max_steps"""
        while not self.halted:
            if self.steps >= max_steps:
                raise RuntimeError("Limite de passos atingido (possível loop infinito)")
            self.step()

    # --- Auxiliares ---
    def state(self) -> Dict:
        """Retorna estado atual da VM"""
        return {
            "registers": dict(self.registers),
            "sensors": dict(self.sensors),
            "stack": list(self.stack),
            "pc": self.pc,
            "halted": self.halted,
            "steps": self.steps,
            "video": self.video_title if self.video_loaded else None
        }


# --------- Programas Demo ---------

# Controle simples de reprodução
DEMO_SIMPLE = """
OPEN "Trailer 1"
PLAY 1
WAIT 5
PAUSE
HALT
"""

# Lógica condicional - reproduz até posição >= 30
DEMO_CONDITIONAL = """
OPEN "Demo Video"
PLAY 1

loop:
    WAIT 1
    GET_POS
    PUSH 30
    LT              ; pilha: 1 se pos < 30, senão 0
    JUMPI loop      ; continua se pos < 30

PAUSE
PRINTS "Alcançou 30 segundos!"
HALT
"""

# Uso de registradores e aritmética
DEMO_ARITHMETIC = """
OPEN "Tutorial"
PLAY 1
WAIT 10

; Armazena posição na memória
GET_POS
STORE 0         ; memory[0] = posição

; Adiciona 20 segundos
LOAD 0
PUSH 20
ADD
POP R0          ; R0 = posição + 20

; Busca nova posição
PUSH R0
POP R0
SEEK 30

HALT
"""

# Turing-completo: usa DECJZ para loop
DEMO_DECJZ = """
; Contagem regressiva de 5 usando DECJZ (instrução Turing-completa)
PUSH 5
POP R0

countdown:
    PUSH R0
    PRINT
    DECJZ R0 done
    GOTO countdown

done:
    PRINTS "Contagem finalizada!"
    HALT
"""


if __name__ == "__main__":
    vm = StreamVM()

    if len(sys.argv) > 1:
        # Carregar programa de arquivo
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                program = f.read()
            print(f"=== Carregando programa de {filename} ===\n")
            vm.load_program(program)
            vm.run()
            print("\n=== Estado Final ===")
            print(vm.state())
        except FileNotFoundError:
            print(f"Erro: Arquivo '{filename}' não encontrado")
            sys.exit(1)
        except Exception as e:
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Executar programas demo
        print("=== Demo 1: Reprodução Simples ===\n")
        vm.load_program(DEMO_SIMPLE)
        vm.run()
        print("\nEstado:", vm.state())

        print("\n\n=== Demo 2: Loop Condicional ===\n")
        vm = StreamVM()
        vm.load_program(DEMO_CONDITIONAL)
        vm.run()
        print("\nEstado:", vm.state())

        print("\n\n=== Demo 3: Contagem DECJZ (Turing-completo) ===\n")
        vm = StreamVM()
        vm.load_program(DEMO_DECJZ)
        vm.run()
        print("\nEstado:", vm.state())
