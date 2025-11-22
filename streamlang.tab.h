/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_STREAMLANG_TAB_H_INCLUDED
# define YY_YY_STREAMLANG_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    T_INT = 258,                   /* T_INT  */
    T_STRING = 259,                /* T_STRING  */
    T_IF = 260,                    /* T_IF  */
    T_ELSE = 261,                  /* T_ELSE  */
    T_WHILE = 262,                 /* T_WHILE  */
    T_PRINT = 263,                 /* T_PRINT  */
    T_OPEN = 264,                  /* T_OPEN  */
    T_PLAY = 265,                  /* T_PLAY  */
    T_PAUSE = 266,                 /* T_PAUSE  */
    T_STOP = 267,                  /* T_STOP  */
    T_SEEK = 268,                  /* T_SEEK  */
    T_FORWARD = 269,               /* T_FORWARD  */
    T_REWIND = 270,                /* T_REWIND  */
    T_WAIT = 271,                  /* T_WAIT  */
    T_POSITION = 272,              /* T_POSITION  */
    T_DURATION = 273,              /* T_DURATION  */
    T_ENDED = 274,                 /* T_ENDED  */
    T_IS_PLAYING = 275,            /* T_IS_PLAYING  */
    T_EQ = 276,                    /* T_EQ  */
    T_NE = 277,                    /* T_NE  */
    T_LE = 278,                    /* T_LE  */
    T_GE = 279,                    /* T_GE  */
    T_ERROR = 280,                 /* T_ERROR  */
    T_IDENT = 281,                 /* T_IDENT  */
    T_STRING_LIT = 282,            /* T_STRING_LIT  */
    T_NUMBER = 283,                /* T_NUMBER  */
    LOWER_THAN_ELSE = 284,         /* LOWER_THAN_ELSE  */
    UMINUS = 285                   /* UMINUS  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{
#line 374 "streamlang.y"

  int ival;
  char* sval;
  struct Node* node;
  struct NodeList* list;

#line 101 "streamlang.tab.h"

};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_STREAMLANG_TAB_H_INCLUDED  */
