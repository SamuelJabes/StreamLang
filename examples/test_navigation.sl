// Teste: Navegação avançada de vídeo
// Testa: seek, forward, rewind, position()

int target = 60;

open("Tutorial Video");
play();

print("Posição inicial:");
print(position());

// Pular para 30 segundos
seek(30);
print("Após seek(30):");
print(position());

// Avançar 20 segundos
forward(20);
print("Após forward(20):");
print(position());

// Voltar 10 segundos
rewind(10);
print("Posição atual:");
print(position());

// Navegar para posição alvo
if (position() < target) {
    int diff = target - position();
    forward(diff);
    print("Navegado para posição alvo!");
}

pause();
print("Posição final:");
print(position());
