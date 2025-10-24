%option noyywrap
%option yylineno

%{
#include "streamlang.tab.h"
#include <string.h>
#include <stdlib.h>

static char* sl_strdup(const char* s) {
    if (!s) return NULL;
    size_t n = strlen(s);
    char* p = (char*)malloc(n+1);
    memcpy(p, s, n+1);
    return p;
}
%}

/* start condition for block comments */
%x CMT

/* ----------- macros ----------- */
WS          [ \t\r]+
DIGIT       [0-9]
LETTER      [A-Za-z]
IDREST      [A-Za-z0-9_]
ID          {LETTER}{IDREST}*
NUMBER      {DIGIT}+
ESC         \\["\\nrt]
STRCHAR     ([^"\\]|{ESC})
STRING      \"{STRCHAR}*\"

%%

{WS}                        ;

"//".*                      ;

"/*"                        { BEGIN(CMT); }
<CMT>"*/"                   { BEGIN(INITIAL); }
<CMT>\n                     ;
<CMT>.                      ;


"int"                       { return T_INT; }
"string"                    { return T_STRING; }
"if"                        { return T_IF; }
"else"                      { return T_ELSE; }
"while"                     { return T_WHILE; }
"print"                     { return T_PRINT; }

"open"                      { return T_OPEN; }
"play"                      { return T_PLAY; }
"pause"                     { return T_PAUSE; }
"stop"                      { return T_STOP; }
"seek"                      { return T_SEEK; }
"forward"                   { return T_FORWARD; }
"rewind"                    { return T_REWIND; }
"wait"                      { return T_WAIT; }

"position"                  { return T_POSITION; }
"duration"                  { return T_DURATION; }
"ended"                     { return T_ENDED; }
"is_playing"                { return T_IS_PLAYING; }

"=="                        { return T_EQ; }
"!="                        { return T_NE; }
"<="                        { return T_LE; }
">="                        { return T_GE; }

{ID}                        { yylval.sval = sl_strdup(yytext); return T_IDENT; }
{NUMBER}                    { yylval.ival = atoi(yytext); return T_NUMBER; }
{STRING}                    {
                                size_t n = yyleng;
                                char* buf = (char*)malloc(n-1);
                                size_t j=0;
                                for (size_t i=1; i<n-1; ++i) {
                                    if (yytext[i] == '\\') {
                                        ++i;
                                        switch(yytext[i]) {
                                            case 'n': buf[j++] = '\n'; break;
                                            case 'r': buf[j++] = '\r'; break;
                                            case 't': buf[j++] = '\t'; break;
                                            case '\\': buf[j++]='\\'; break;
                                            case '"': buf[j++]='"'; break;
                                            default: buf[j++]=yytext[i]; break;
                                        }
                                    } else {
                                        buf[j++] = yytext[i];
                                    }
                                }
                                buf[j]='\0';
                                yylval.sval = buf;
                                return T_STRING_LIT;
                            }

";"                         { return ';'; }
"="                         { return '='; }
"("                         { return '('; }
")"                         { return ')'; }
"{"                         { return '{'; }
"}"                         { return '}'; }
"+"                         { return '+'; }
"-"                         { return '-'; }
"*"                         { return '*'; }
"/"                         { return '/'; }
"<"                         { return '<'; }
">"                         { return '>'; }

\n                          ;

.                           { fprintf(stderr,"[LEXER] invalid char '%c' at line %d\n", yytext[0], yylineno); return T_ERROR; }

%%
