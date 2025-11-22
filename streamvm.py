#!/usr/bin/env python3
"""
StreamVM - A Turing-complete Virtual Machine for video streaming control.

Architecture:
  - 2+ Registers: POS (position), SPEED (playback speed), R0, R1 (general purpose)
  - Memory: Stack for expressions and local variables
  - Readonly Sensors: DURATION, IS_PLAYING, ENDED

Instruction Set (Turing-complete via DECJZ + GOTO):
  Stack Operations:
    PUSH n          ; push literal value n onto stack
    POP R           ; pop top of stack into register R
    LOAD addr       ; push memory[addr] onto stack
    STORE addr      ; pop stack into memory[addr]

  Arithmetic:
    ADD             ; pop b, pop a, push a+b
    SUB             ; pop b, pop a, push a-b
    MUL             ; pop b, pop a, push a*b
    DIV             ; pop b, pop a, push a/b
    NEG             ; pop a, push -a

  Comparisons (push 1 if true, 0 if false):
    EQ, NE, LT, LE, GT, GE

  Control Flow (Turing-complete):
    LABEL name      ; define a jump target
    GOTO label      ; unconditional jump
    JUMPZ label     ; jump if top of stack == 0
    JUMPI label     ; jump if top of stack != 0
    DECJZ R label   ; if R == 0: jump to label, else R := R - 1

  Streaming Commands:
    OPEN "title"    ; open video by title
    PLAY speed      ; play at speed (default 1)
    PAUSE           ; pause playback
    STOP            ; stop playback
    SEEK pos        ; seek to absolute position
    FORWARD delta   ; skip forward delta seconds
    REWIND delta    ; skip backward delta seconds
    WAIT time       ; wait for time seconds (simulated)

  Sensors (push value onto stack):
    GET_POS         ; push current position
    GET_DUR         ; push video duration
    GET_ENDED       ; push 1 if ended, 0 otherwise
    GET_PLAYING     ; push 1 if playing, 0 otherwise

  I/O:
    PRINT           ; print top of stack
    PRINTS "text"   ; print string literal

  Control:
    HALT            ; stop execution
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
        # Registers (writable)
        self.registers: Dict[str, int] = {
            "POS": 0,      # Current position in seconds
            "SPEED": 1,    # Playback speed (1 = normal)
            "R0": 0,       # General purpose register 0
            "R1": 0,       # General purpose register 1
        }

        # Readonly sensors
        self.sensors: Dict[str, int] = {
            "DURATION": 0,    # Video duration in seconds
            "IS_PLAYING": 0,  # 1 if playing, 0 if paused/stopped
            "ENDED": 0,       # 1 if video ended, 0 otherwise
        }

        # Memory and stack
        self.memory: List[int] = [0] * 256  # 256 cells of memory
        self.stack: List[int] = []

        # Video state
        self.video_title: str = ""
        self.video_loaded: bool = False

        # Program execution
        self.program: List[Instr] = []
        self.labels: Dict[str, int] = {}
        self.pc: int = 0
        self.halted: bool = False
        self.steps: int = 0

    # --- Assembler / Loader ---
    def load_program(self, source: str):
        """Load and parse assembly program"""
        self.program.clear()
        self.labels.clear()
        self.stack.clear()
        self.pc = 0
        self.halted = False
        self.steps = 0

        lines = source.splitlines()

        # First pass: collect labels
        idx = 0
        for raw in lines:
            line = raw.split(';', 1)[0].split('#', 1)[0].strip()
            if not line:
                continue
            if line.endswith(':'):
                label = line[:-1].strip()
                if not label:
                    raise ValueError("Empty label definition.")
                if label in self.labels:
                    raise ValueError(f"Duplicate label: {label}")
                self.labels[label] = idx
            else:
                idx += 1

        # Second pass: parse instructions
        for raw in lines:
            line = raw.split(';', 1)[0].split('#', 1)[0].strip()
            if not line or line.endswith(':'):
                continue

            # Handle string literals
            if '"' in line:
                # Split at first space, then handle quoted string
                parts = line.split(None, 1)
                if len(parts) == 2:
                    op = parts[0].upper()
                    # Extract string literal
                    rest = parts[1].strip()
                    if rest.startswith('"') and rest.endswith('"'):
                        args = (rest[1:-1],)  # Remove quotes
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

    # --- Execution ---
    def step(self):
        """Execute one instruction"""
        if self.halted:
            return
        if not (0 <= self.pc < len(self.program)):
            self.halted = True
            return

        instr = self.program[self.pc]
        self.steps += 1

        op = instr.op
        args = instr.args

        # Stack operations
        if op == "PUSH":
            # Support both literal and register
            arg = args[0]
            if arg.upper() in self.registers:
                val = self.registers[arg.upper()]
            else:
                val = int(arg)
            self.stack.append(val)
            self.pc += 1

        elif op == "POP":
            if not self.stack:
                raise RuntimeError("Cannot POP from empty stack")
            reg = args[0].upper()
            self.registers[reg] = self.stack.pop()
            self.pc += 1

        elif op == "LOAD":
            addr = int(args[0])
            self.stack.append(self.memory[addr])
            self.pc += 1

        elif op == "STORE":
            if not self.stack:
                raise RuntimeError("Cannot STORE from empty stack")
            addr = int(args[0])
            self.memory[addr] = self.stack.pop()
            self.pc += 1

        # Arithmetic
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
                raise RuntimeError("Division by zero")
            self.stack.append(a // b)  # Integer division
            self.pc += 1

        elif op == "NEG":
            a = self.stack.pop()
            self.stack.append(-a)
            self.pc += 1

        # Comparisons
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

        # Control flow
        elif op == "GOTO":
            label = args[0]
            if label not in self.labels:
                raise ValueError(f"Unknown label: {label}")
            self.pc = self.labels[label]

        elif op == "JUMPZ":
            label = args[0]
            val = self.stack.pop()
            if val == 0:
                if label not in self.labels:
                    raise ValueError(f"Unknown label: {label}")
                self.pc = self.labels[label]
            else:
                self.pc += 1

        elif op == "JUMPI":
            label = args[0]
            val = self.stack.pop()
            if val != 0:
                if label not in self.labels:
                    raise ValueError(f"Unknown label: {label}")
                self.pc = self.labels[label]
            else:
                self.pc += 1

        elif op == "DECJZ":
            reg = args[0].upper()
            label = args[1]
            if self.registers[reg] == 0:
                if label not in self.labels:
                    raise ValueError(f"Unknown label: {label}")
                self.pc = self.labels[label]
            else:
                self.registers[reg] -= 1
                self.pc += 1

        # Streaming commands
        elif op == "OPEN":
            self.video_title = args[0]
            self.video_loaded = True
            # Simulate video metadata
            self.sensors["DURATION"] = 180  # 3 minutes default
            self.sensors["IS_PLAYING"] = 0
            self.sensors["ENDED"] = 0
            self.registers["POS"] = 0
            print(f"[STREAM] Opened video: '{self.video_title}'")
            self.pc += 1

        elif op == "PLAY":
            if not self.video_loaded:
                raise RuntimeError("No video loaded")
            speed = int(args[0]) if args else 1
            self.registers["SPEED"] = speed
            self.sensors["IS_PLAYING"] = 1
            print(f"[STREAM] Playing at speed {speed}x")
            self.pc += 1

        elif op == "PAUSE":
            self.sensors["IS_PLAYING"] = 0
            print(f"[STREAM] Paused at position {self.registers['POS']}s")
            self.pc += 1

        elif op == "STOP":
            self.sensors["IS_PLAYING"] = 0
            self.registers["POS"] = 0
            print("[STREAM] Stopped")
            self.pc += 1

        elif op == "SEEK":
            # Support both literal and register
            arg = args[0]
            if arg.upper() in self.registers:
                pos = self.registers[arg.upper()]
            else:
                pos = int(arg)
            self.registers["POS"] = pos
            print(f"[STREAM] Seeked to {pos}s")
            self.pc += 1

        elif op == "FORWARD":
            # Support both literal and register
            arg = args[0]
            if arg.upper() in self.registers:
                delta = self.registers[arg.upper()]
            else:
                delta = int(arg)
            self.registers["POS"] += delta
            print(f"[STREAM] Forwarded {delta}s to position {self.registers['POS']}s")
            self.pc += 1

        elif op == "REWIND":
            # Support both literal and register
            arg = args[0]
            if arg.upper() in self.registers:
                delta = self.registers[arg.upper()]
            else:
                delta = int(arg)
            self.registers["POS"] = max(0, self.registers["POS"] - delta)
            print(f"[STREAM] Rewinded {delta}s to position {self.registers['POS']}s")
            self.pc += 1

        elif op == "WAIT":
            # Support both literal and register
            arg = args[0]
            if arg.upper() in self.registers:
                time = self.registers[arg.upper()]
            else:
                time = int(arg)
            if self.sensors["IS_PLAYING"]:
                self.registers["POS"] += time * self.registers["SPEED"]
                # Check if ended
                if self.registers["POS"] >= self.sensors["DURATION"]:
                    self.registers["POS"] = self.sensors["DURATION"]
                    self.sensors["ENDED"] = 1
                    self.sensors["IS_PLAYING"] = 0
            print(f"[STREAM] Waited {time}s (now at {self.registers['POS']}s)")
            self.pc += 1

        # Sensors
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
                raise RuntimeError("Cannot PRINT from empty stack")
            val = self.stack.pop()
            print(val)
            self.pc += 1

        elif op == "PRINTS":
            text = args[0]
            print(text)
            self.pc += 1

        # Control
        elif op == "HALT":
            print("[VM] Execution halted")
            self.halted = True

        else:
            raise ValueError(f"Unknown opcode: {op}")

    def run(self, max_steps: Optional[int] = 10000):
        """Run program until HALT or max_steps"""
        while not self.halted:
            if self.steps >= max_steps:
                raise RuntimeError("Step limit reached (possible infinite loop)")
            self.step()

    # --- Helpers ---
    def state(self) -> Dict:
        """Get current VM state"""
        return {
            "registers": dict(self.registers),
            "sensors": dict(self.sensors),
            "stack": list(self.stack),
            "pc": self.pc,
            "halted": self.halted,
            "steps": self.steps,
            "video": self.video_title if self.video_loaded else None
        }


# --------- Demo Programs ---------

# Simple playback control
DEMO_SIMPLE = """
OPEN "Trailer 1"
PLAY 1
WAIT 5
PAUSE
HALT
"""

# Conditional logic - play until position >= 30
DEMO_CONDITIONAL = """
OPEN "Demo Video"
PLAY 1

loop:
    WAIT 1
    GET_POS
    PUSH 30
    LT              ; stack: 1 if pos < 30, else 0
    JUMPI loop      ; continue if pos < 30

PAUSE
PRINTS "Reached 30 seconds!"
HALT
"""

# Use registers and arithmetic
DEMO_ARITHMETIC = """
OPEN "Tutorial"
PLAY 1
WAIT 10

; Store position in memory
GET_POS
STORE 0         ; memory[0] = position

; Add 20 seconds
LOAD 0
PUSH 20
ADD
POP R0          ; R0 = position + 20

; Seek to new position
PUSH R0
POP R0
SEEK 30

HALT
"""

# Turing-complete: use DECJZ for loop
DEMO_DECJZ = """
; Count down from 5 using DECJZ (Turing-complete instruction)
PUSH 5
POP R0

countdown:
    PUSH R0
    PRINT
    DECJZ R0 done
    GOTO countdown

done:
    PRINTS "Countdown finished!"
    HALT
"""


if __name__ == "__main__":
    vm = StreamVM()

    if len(sys.argv) > 1:
        # Load program from file
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                program = f.read()
            print(f"=== Loading program from {filename} ===\n")
            vm.load_program(program)
            vm.run()
            print("\n=== Final State ===")
            print(vm.state())
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Run demo programs
        print("=== Demo 1: Simple Playback ===\n")
        vm.load_program(DEMO_SIMPLE)
        vm.run()
        print("\nState:", vm.state())

        print("\n\n=== Demo 2: Conditional Loop ===\n")
        vm = StreamVM()
        vm.load_program(DEMO_CONDITIONAL)
        vm.run()
        print("\nState:", vm.state())

        print("\n\n=== Demo 3: DECJZ Countdown (Turing-complete) ===\n")
        vm = StreamVM()
        vm.load_program(DEMO_DECJZ)
        vm.run()
        print("\nState:", vm.state())
