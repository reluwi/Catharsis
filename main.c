#include <stdio.h>
#include <stdlib.h>

typedef enum {
    SEMI,
    OPEN_PAREN,
    CLOSE_PAREN,
} TypeSeperator;

typedef enum {
    EXIT,
} TypeKeyword;

typedef enum {
    INT, 
} TypeLiteral;

typedef struct {
    TypeKeyword type;
} TokenKeyword;

typedef struct {
    TypeSeperator type;
} TokenSeperator;

typedef struct {
    TypeLiteral type;
    int value;
} TokenLiteral;

void lexer(FILE *file){
    char current = fgetc(file);
    
    while(current != EOF){
        if(current == ';'){
            printf("FOUND SEMICOLON\n");
        }
        else if(current == '('){
            printf("FOUND OPEN PAREN\n");
        }
        else if(current == ')'){
            printf("FOUND CLOSE PAREN\n");
        }
        current = fgetc(file);
    }
}

int main() {
    FILE *file;
    file = fopen("test.unn", "r");
    lexer(file);
}