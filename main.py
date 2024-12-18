from enum import Enum
import string

class TokenType(Enum):
    ASSIGNMENT_OP = "ASSIGNMENT_OP"
    INT = "INT" 
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    INVALID_IDENTIFIER = "INVALID_IDENTIFIER"
    ARITHMETIC_OP = "ARITHMETIC_OP"
    DELIMITER = "DELIMITER"
    UNARY_OP = "UNARY_OP"
    LOGICAL_OP = "LOGICAL_OP"
    RELATIONAL_OP = "RELATIONAL_OP"
    RESERVED_WORD = "RESERVED_WORD"
    COMMENT_SYMBOL = "COMMENT_SYMBOL" 

# define the token class
class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.token_type}, {repr(self.value)})"
    
KEYWORDS = ["int", "float", "double", "char", "bool", "string", "if", "else", "for", "while", "break", "continue", "printf", "scanf"]
RES_WORDS = ["gc", "main", "malloc", "true", "false", "enable", "disable"]
ARITH_OPS = ["*", "/", "%", "^", "#"]
DELI = [";", "(", ")", "[", "]", "{", "}", ",", "."]

# check if a word is a keyword
def is_keyword(word):
    return word in KEYWORDS

# check if a word is a keyword
def is_res_word(word):
    return word in RES_WORDS

# generate a token for a number
def generate_number(value):
    return {"type": "NUMBER", "value": value}

# generate a token for a keyword
def generate_keyword(value):
    return {"type": "KEYWORD", "value": value}

# generate a token for a reserved word
def generate_res_word(value):
    return {"type": "RESERVED_WORD", "value": value}

# generate a token for an identifier
def generate_identifier(value):
    return {"type": "IDENTIFIER", "value": value}

# generate a token for an invalid identifier
def generate_invalid_identifier(value):
    return {"type": "INVALID_IDENTIFIER", "value": value}

# process a number
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

    # Determine if the word is a keyword, identifier, arith_op, or invalid
    if is_keyword(word_value):
        return generate_keyword(word_value), index
    elif is_res_word(word_value):
        return generate_res_word(word_value), index
    elif word_value[0].isdigit():
        return generate_invalid_identifier(word_value), index
    elif word_value.startswith("_"):
        return generate_invalid_identifier(word_value), index
    elif "__" in word_value:
        return generate_invalid_identifier(word_value), index
    elif word_value.endswith("_"):
        return generate_invalid_identifier(word_value), index
    else:
        return generate_identifier(word_value), index
    
# Process a delimiter
def process_deli(char):
    if char in DELI:
        return {"type": "DELIMITER", "value": char}
    return None

# Process unary and arithmetic operators
def process_operator(input_text, index, previous_token):
    # Check for "++" and "--"
    if input_text.startswith("++", index):
        return {"type": "UNARY_OP", "value": "++"}, index + 2
    elif input_text.startswith("--", index):
        return {"type": "UNARY_OP", "value": "--"}, index + 2
    
    # Check for single line and multiple line comments
    if input_text.startswith("//", index):
        return {"type": "COMMENT_SYMBOL", "value": "//"}, index + 2
    elif input_text.startswith("/*", index):
        return {"type": "COMMENT_SYMBOL", "value": "/*"}, index + 2
    elif input_text.startswith("*/", index):
        return {"type": "COMMENT_SYMBOL", "value": "*/"}, index + 2
    
    # Check for assignment operators
    elif input_text.startswith("=", index):
        return {"type": "ASSIGNMENT_OP", "value": "="}, index + 1
    elif input_text.startswith("+=", index):
        return {"type": "ASSIGNMENT_OP", "value": "+="}, index + 2
    elif input_text.startswith("-=", index):
        return {"type": "ASSIGNMENT_OP", "value": "-="}, index + 2
    elif input_text.startswith("*=", index):
        return {"type": "ASSIGNMENT_OP", "value": "*="}, index + 2
    elif input_text.startswith("/=", index):
        return {"type": "ASSIGNMENT_OP", "value": "/="}, index + 2
    elif input_text.startswith("%=", index):
        return {"type": "ASSIGNMENT_OP", "value": "%="}, index + 2
    
    # Check for logical operators
    elif input_text.startswith("||", index):
        return {"type": "LOGICAL_OP", "value": "||"}, index + 2
    elif input_text.startswith("&&", index):
        return {"type": "LOGICAL_OP", "value": "&&"}, index + 2
    elif input_text.startswith("!", index):
        return {"type": "LOGICAL_OP", "value": "!"}, index + 1
    
    # Check for relational operators
    elif input_text.startswith("==", index):
        return {"type": "RELATIONAL_OP", "value": "=="}, index + 2
    elif input_text.startswith("!=", index):
        return {"type": "RELATIONAL_OP", "value": "!="}, index + 2
    elif input_text.startswith(">=", index):
        return {"type": "RELATIONAL_OP", "value": ">="}, index + 2
    elif input_text.startswith("<=", index):
        return {"type": "RELATIONAL_OP", "value": "<="}, index + 2
    elif input_text.startswith(">", index):
        return {"type": "RELATIONAL_OP", "value": ">"}, index + 1
    elif input_text.startswith("<", index):
        return {"type": "RELATIONAL_OP", "value": "<"}, index + 1

    # Check for unary "+" or "-"
    elif input_text[index] in ["+", "-"]:
        # Determine if it should be treated as a unary operator
        if previous_token and previous_token["type"] in ["DELIMITER", "ASSIGNMENT_OP", "LOGICAL_OP", "RELATIONAL_OP", "COMMENT_SYMBOL"]:
            return {"type": "UNARY_OP", "value": input_text[index]}, index + 1
        else:
            # Otherwise, treat it as an arithmetic operator
            return {"type": "ARITHMETIC_OP", "value": input_text[index]}, index + 1

    # check for other arithmetic op
    elif input_text[index] in ARITH_OPS:
        return {"type": "ARITHMETIC_OP", "value": input_text[index]}, index + 1

    return None, index

# main lexer function    
def lexer(input_text):
    index = 0
    tokens = []
    length = len(input_text)
    previous_token = None

    while index < len(input_text):
        char = input_text[index]

        # Skip whitespace
        if char.isspace():
            index += 1
            continue
        
        # Handle delimiters
        delimiter_token = process_deli(char)
        if delimiter_token:
            tokens.append(delimiter_token)
            previous_token = delimiter_token  # Update previous_token
            index += 1
            continue
        
        # Handle unary and arithmetic operators
        un_op_token, new_index = process_operator(input_text, index, previous_token)
        if un_op_token:
            tokens.append(un_op_token)
            previous_token = un_op_token
            index = new_index
            continue

        # Process numbers
        elif char.isdigit():
            temp_index = index
            while temp_index < length and input_text[temp_index].isalnum():
                temp_index += 1

            token_value = input_text[index:temp_index]
            
            if any(c.isalpha() for c in token_value):  # Check if it contains letters
                token = ({"type": "INVALID_IDENTIFIER", "value": token_value})
            else:
                token = ({"type": "NUMBER", "value": token_value})

            tokens.append(token)
            previous_token = token
            index = temp_index
            continue

        # Process words (keywords, reserved words, identifiers, or invalid identifiers)
        elif char.isalpha() or char == "_":
            token, index = process_word(input_text, index)
            tokens.append(token)
            previous_token = token
            continue

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