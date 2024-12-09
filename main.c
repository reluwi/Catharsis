#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

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
    char *value;
} TokenLiteral;

TokenLiteral *generate_number(char current, FILE *file){
    TokenLiteral *token = malloc(sizeof(TokenLiteral));
    token->type = INT;
    char *value = malloc(sizeof(char) * 8);
    int value_index = 0;
    
    while(isdigit(current) && current != EOF){
        if(!isdigit(current)){
            break;
        }
        value[value_index] = current;
        value_index++;
        current = fgetc(file);
    }

    value[value_index] = '\0';
    token->value = value; 
    return token;
}

TokenKeyword *generate_keyword(char current, FILE *file){
    TokenKeyword *token = malloc(sizeof(TokenKeyword));
    char *keyword = malloc(sizeof(char) * 4);
    int keyword_index = 0;

    while(isalpha(current) && current != EOF){
        keyword[keyword_index] = current;
        current = fgetc(file);
    }

    char keyword_str[keyword_index];
    for(int i = 0; i < keyword_index; i++){
        keyword_str[i] = keyword[i];
    }

    if(strcmp(keyword, "exit")){
        token->type = EXIT;
    }

    return token;
}

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
        else if(isdigit(current)){
            TokenLiteral *test_token = generate_number(current, file);
            printf("TEST TOKEN VALUE: %s\n", test_token->value);\

            free(test_token->value);
            free(test_token);

            //printf("FOUND DIGIT: %d\n", current - '0');
        }
        else if(isalpha(current)){
            TokenKeyword *test_keyword = generate_keyword(current, file);
            
            //printf("FOUND CHARACTER: %C\n", current);
        }
        current = fgetc(file);
    }
}

int main() {
    FILE *file;
    file = fopen("test.unn", "r");
    lexer(file);
}