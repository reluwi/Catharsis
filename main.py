from enum import Enum
import string

class TokenType(Enum):
    SEMI = "SEMI" # ;
    OPEN_PAREN = "OPEN_PAREN" # (
    CLOSE_PAREN = "CLOSE_PAREN" # )
    EQUAL = "EQUAL" # =
    INT = "INT" 
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    INVALID_IDENTIFIER = "INVALID_IDENTIFIER"

# define the token class
class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.token_type}, {repr(self.value)})"
    
KEYWORDS = ["int", "float", "double", "char", "bool", "string", "exit"]

# check if a word is a keyword
def is_keyword(word):
    return word in KEYWORDS

# generate a token for a number
def generate_number(value):
    return {"type": "NUMBER", "value": value}

# generate a token for a keyword
def generate_keyword(value):
    return {"type": "KEYWORD", "value": value}

# generate a token for an identifier
def generate_identifier(value):
    return {"type": "IDENTIFIER", "value": value}

# generate a token for an invalid identifier
def generate_invalid_identifier(value):
    return {"type": "INVALID_IDENTIFIER", "value": value}

# Function to process a number
def process_number(input_text, index):
    start_index = index
    while index < len(input_text) and input_text[index].isdigit():
        index += 1
    number_value = input_text[start_index:index]
    return generate_number(number_value), index

# process a word (keyword or identifier)
def process_word(input_text, index):
    start_index = index
    while index < len(input_text) and (input_text[index].isalnum() or input_text[index] == "_"):
        index += 1
    word_value = input_text[start_index:index]

    # Determine if the word is a keyword, identifier, or invalid
    if is_keyword(word_value):
        return generate_keyword(word_value), index
    elif word_value[0].isdigit():
        return generate_invalid_identifier(word_value), index
    else:
        return generate_identifier(word_value), index
    
def lexer(input_text):
    index = 0
    tokens = []
    length = len(input_text)

    while index < len(input_text):
        char = input_text[index]

        # Skip whitespace
        if char.isspace():
            index += 1
            continue
        
        # Process other single-character tokens (e.g., symbols)
        elif char == ";":
            tokens.append({"type": "SEMI", "value": ";"})
            index += 1
        elif char == "(":
            tokens.append({"type": "OPEN_PAREN", "value": "("})
            index += 1
        elif char == ")":
            tokens.append({"type": "CLOSE_PAREN", "value": ")"})
            index += 1
        elif char == "=":
            tokens.append({"type": "EQUAL", "value": "="})
            index += 1

        # Process numbers
        elif char.isdigit():
            temp_index = index
            while temp_index < length and input_text[temp_index].isalnum():
                temp_index += 1

            token_value = input_text[index:temp_index]
            
            if any(c.isalpha() for c in token_value):  # Check if it contains letters
                tokens.append({'type': 'INVALID_IDENTIFIER', 'value': token_value})
            else:
                tokens.append({'type': 'NUMBER', 'value': token_value})

            index = temp_index

        # Process words (keywords, identifiers, or invalid identifiers)
        elif char.isalpha() or char == "_":
            token, index = process_word(input_text, index)
            tokens.append(token)

        # Handle unrecognized characters
        else:
            print(f"Warning: Unrecognized character '{char}' at index {index}")
            index += 1

    return tokens

def read_input_file(file_path):
    try:
        with open("test.unn", "r") as file:
            input_text = file.read()
        return input_text
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def main():
    file_name = "test.unn"

    input_text = read_input_file(file_name)

    # Proceed only if the file was read successfully
    if input_text is not None:
        print(f"Processing file: {file_name}")
        # Pass the input text to the lexer
        tokens = lexer(input_text)

        # Print each token
        for token in tokens:
            print(token)

if __name__ == "__main__":
    main()