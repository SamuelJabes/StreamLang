// Declarações
int pos = 0;
int v;
string title = "Meu Video";

/* Abrir por título e tocar */
open("Trailer 1");
play();
wait(5);
pause();
seek(30);
play();
forward(15);
rewind(5);

// Prints e built-ins
print("andando...");
print(position());
print(duration());
if (is_playing() == 1) {
    print(123 + 7*3);
} else {
    print("paused");
}

// Control flow
while (ended() == 0) {
    v = position();
    if (v >= 120) { stop(); } else { wait(1); }
}
