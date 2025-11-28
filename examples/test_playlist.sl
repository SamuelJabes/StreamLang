// Teste: Simulação de playlist com múltiplos vídeos
// Testa: open, play, wait, sensores (position, duration, ended)

print("=== Playlist Demo ===");

// Vídeo 1
open("Intro Video");
play();
wait(10);

if (position() >= 10) {
    print("Intro completo!");
}

stop();

// Vídeo 2
open("Main Content");
play();

// Aguardar até metade do vídeo
while (position() < duration() / 2) {
    wait(1);
}

print("Metade do vídeo alcançada");
print(position());

pause();
