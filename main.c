#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

// Token Types
typedef enum {
    SEMI,        // ;
    OPEN_PAREN,  // (
    CLOSE_PAREN, // )
    INT,         // Numbers
    KEYWORD      // Keywords like "exit"
} TokenType;

// Token Structure
typedef struct {
    TokenType type;
    char *value;
} Token;

// Function to create tokens for numbers
Token *generate_number(const char *input, int *index) {
    Token *token = malloc(sizeof(Token));
    token->type = INT;

    // Allocate memory for the number
    char *value = malloc(sizeof(char) * 16); // Max 15 digits + null terminator
    int value_index = 0;

    // Collect digits
    while (isdigit(input[*index])) {
        value[value_index++] = input[*index];
        (*index)++;
    }

    value[value_index] = '\0'; // Null-terminate the string
    token->value = value;
    return token;
}

// Function to create tokens for keywords
Token *generate_keyword(const char *input, int *index) {
    Token *token = malloc(sizeof(Token));
    token->type = KEYWORD;

    // Allocate memory for the keyword
    char *value = malloc(sizeof(char) * 16); // Max 15 characters + null terminator
    int value_index = 0;

    // Collect alphabetic characters
    while (isalpha(input[*index])) {
        value[value_index++] = input[*index];
        (*index)++;
    }

    value[value_index] = '\0'; // Null-terminate the string
    token->value = value;

    // Check if the keyword matches "exit"
    //if (strcmp(value, "exit") == 0) {
    //    printf("FOUND KEYWORD: exit\n");
    //}
    return token;
}

// Main Lexical Analyzer Function
void lexer(const char *input) {
    int index = 0;

    while (input[index] != '\0') {
        if (input[index] == ';') {
            printf("FOUND SEMICOLON\n");
            index++;
        } else if (input[index] == '(') {
            printf("FOUND OPEN PAREN\n");
            index++;
        } else if (input[index] == ')') {
            printf("FOUND CLOSE PAREN\n");
            index++;
        } else if (isdigit(input[index])) {
            Token *number_token = generate_number(input, &index);
            printf("FOUND NUMBER: %s\n", number_token->value);

            free(number_token->value); // Free memory
            free(number_token);
        } else if (isalpha(input[index])) {
            Token *keyword_token = generate_keyword(input, &index);
            printf("FOUND KEYWORD: %s\n", keyword_token->value);

            free(keyword_token->value); // Free memory
            free(keyword_token);
        } else {
            index++; // Skip unknown characters
        }
    }
}

int main() {
    FILE *file = fopen("test.unn", "r");
    if (!file) {
        perror("Error opening file");
        return 1;
    }

    // Read file into a buffer
    fseek(file, 0, SEEK_END);
    int length = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *buffer = malloc(length + 1);
    fread(buffer, 1, length, file);
    fclose(file);

    buffer[length] = '\0'; // Null-terminate the input
    lexer(buffer);

    free(buffer); // Free the buffer memory
    return 0;
}
