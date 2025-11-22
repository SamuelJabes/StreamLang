#!/bin/bash
# Script de compilação e execução integrada para StreamLang
#
# Uso: ./run.sh <arquivo.sl> [output.asm]
#
# Exemplo:
#   ./run.sh examples/simple_demo.sl
#   ./run.sh examples/demo.sl meu_programa.asm

if [ $# -lt 1 ]; then
    echo "Uso: $0 <arquivo.sl> [output.asm]"
    echo ""
    echo "Exemplos:"
    echo "  $0 examples/simple_demo.sl"
    echo "  $0 meu_programa.sl saida.asm"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-output.asm}"

# Verificar se o arquivo de entrada existe
if [ ! -f "$INPUT_FILE" ]; then
    echo "Erro: Arquivo '$INPUT_FILE' não encontrado"
    exit 1
fi

# Verificar se o compilador existe
if [ ! -f "./streamlang" ]; then
    echo "Compilador não encontrado. Compilando..."
    make
    if [ $? -ne 0 ]; then
        echo "Erro ao compilar o compilador StreamLang"
        exit 1
    fi
fi

echo "=== StreamLang Compiler & VM ==="
echo "Input:  $INPUT_FILE"
echo "Output: $OUTPUT_FILE"
echo ""

# Compilar StreamLang para Assembly
echo "[1/2] Compilando para assembly..."
./streamlang "$OUTPUT_FILE" < "$INPUT_FILE"

if [ $? -ne 0 ]; then
    echo "Erro na compilação"
    exit 1
fi

echo ""
echo "[2/2] Executando na StreamVM..."
echo "================================"
echo ""

# Executar na VM
python3 streamvm.py "$OUTPUT_FILE"

if [ $? -ne 0 ]; then
    echo ""
    echo "Erro na execução"
    exit 1
fi

echo ""
echo "================================"
echo "Execução concluída!"
