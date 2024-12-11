#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

// Token Types (add more like for '{}' and others)
typedef enum {
    SEMI,        // ;
    OPEN_PAREN,  // (
    CLOSE_PAREN, // )
    EQUAL,
    INT,         // Numbers
    KEYWORD,      // Keywords like "exit"
    IDENTIFIER,
    INVALID_IDENTIFIER
} TokenType;

// Token Structure
typedef struct {
    TokenType type;
    char *value;
} Token;

//list of valid keywords (add more)
const char *keywords[] = {"int", "float", "double", "char", "bool", "string", "exit"};
const int keyword_count = sizeof(keywords) / sizeof(keywords[0]);

//check if the word is a keyword
int is_keyword(const char *word) {
    for(int i = 0; i < keyword_count; i++){
        if(strcmp(word, keywords[i]) == 0){
            return 1;
        }
    }
    return 0;
}

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
Token *generate_keyword(const char *word) {
    Token *token = malloc(sizeof(Token));
    token->type = KEYWORD;
    token->value = strdup(word); // Duplicate the word for the token
    return token;
}

// Function to create tokens for identifiers
Token *generate_identifier(const char *word) {
    Token *token = malloc(sizeof(Token));
    token->type = IDENTIFIER;
    token->value = strdup(word); 
    return token;
}

// Function to create token for invalid identifiers
Token *generate_invalid_identifier(const char *word) {
    Token *token = malloc(sizeof(Token));
    token->type = INVALID_IDENTIFIER;
    token->value = strdup(word); 
    return token;
}

// Function to process words (keywords or identifiers)
Token *process_word(const char *input, int *index) {
    char *word = malloc(sizeof(char) * 16); // Max 15 characters + null terminator
    int word_index = 0;

    // Collect identifier starting with number
    if (isdigit(input[*index])) {
        while (isalnum(input[*index])) {
            word[word_index++] = input[*index];
            (*index)++;
        }
        word[word_index] = '\0';
        Token *invalid_token = generate_invalid_identifier(word);
        
        free(word);
        return invalid_token;
    }
    
    //otherwise, collect valid identifier
    while (isalnum(input[*index])) {
        word[word_index++] = input[*index];
        (*index)++;
    }

    word[word_index] = '\0'; // Null-terminate the string

    Token *token;
    if (is_keyword(word)) {
        token = generate_keyword(word);
    } else {
        if(isdigit(word[0])) {
            token = generate_invalid_identifier(word);
        } else {
            token = generate_identifier(word);
        }
    }

    free(word); // Free the temporary word buffer
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
        } else if (input[index] == '=') {
            printf("FOUND EQUAL\n");
            index++;
        } else if (isdigit(input[index])) {
            int temp_index = index;
            while (isdigit(input[temp_index])) {
                temp_index++;
            }

            if(isalpha(input[temp_index])) {
                Token *invalid_token = process_word(input, &index);
                printf("FOUND INVALID_IDENTIFIER: %s\n", invalid_token->value);

                free(invalid_token->value);
                free(invalid_token);
            } else {
                Token *number_token = generate_number(input, &index);
                printf("FOUND NUMBER: %s\n", number_token->value);

                free(number_token->value); // Free memory
                free(number_token);
            }    
        } else if (isalnum(input[index])) {
            Token *word_token = process_word(input, &index);
            if (word_token->type == KEYWORD) {
                printf("FOUND KEYWORD: %s\n", word_token->value);
            } else if (word_token->type == IDENTIFIER) {
                printf("FOUND IDENTIFIER: %s\n", word_token->value);
            } else if (word_token->type == INVALID_IDENTIFIER) {
                printf("FOUND INVALID_IDENTIFIER: %s\n", word_token->value);
            }

            free(word_token->value);
            free(word_token);
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
