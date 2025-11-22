// Simple demo of StreamLang
int timer = 10;

open("My Favorite Video");
play();

// Wait 10 seconds
wait(timer);

// Check position
if (position() > 5) {
    print("More than 5 seconds elapsed");
}

pause();
print(position());
