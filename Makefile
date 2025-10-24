CC=gcc

all: streamlang

streamlang: streamlang.tab.c lex.yy.c
	$(CC) -o $@ streamlang.tab.c lex.yy.c -lfl

streamlang.tab.c streamlang.tab.h: streamlang.y
	bison -Wall -d streamlang.y

lex.yy.c: streamlang.l streamlang.tab.h
	flex streamlang.l

clean:
	rm -f streamlang.tab.c streamlang.tab.h lex.yy.c streamlang

.PHONY: all clean
