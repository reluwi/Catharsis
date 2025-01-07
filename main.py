from enum import Enum
import string
import os
    
KEYWORDS = ["int", "float", "double", "char", "bool", "string", "if", "else", "for", "while", "break", "continue", "printf", "scanf"]
RES_WORDS = ["gc", "main", "malloc", "true", "false", "enable", "disable"]
NOISE_WORDS = ["boolean" , "integer", "character"] #function
ARITH_OPS = ["*", "/", "%", "^", "#"]
DELI = [";", "(", ")", "[", "]", "{", "}", ","]
BOOL = ["True", "False", "TRUE", "FALSE", "true", "false"]
SPECIAL_CHAR = {"~", "?", "@","$", "|", "&"}

# check if a word is a keyword
def is_keyword(word):
    return word in KEYWORDS

# check if a word is a reserved word
def is_res_word(word):
    return word in RES_WORDS

# check if a word is a boolean value
def is_bool(word):
    return word in BOOL

# generate a token for a keyword
def generate_keyword(value):
    return {"type": "KEYWORD", "value": value}

# generate a token for a reserved word
def generate_res_word(value):
    return {"type": "RESERVED_WORD", "value": value}

# generate a token for a boolean value
def generate_bool(value):
    return {"type": "Boolean", "value": value}

# generate a token for an identifier
def generate_identifier(value):
    return {"type": "IDENTIFIER", "value": value}

# generate a token for an invalid identifier
def generate_invalid_identifier(value):
    return {"type": "INVALID_IDENTIFIER", "value": value}

# process a number
def process_number(input_text, index, previous_token):
    start_index = index
    has_dot = False  # Track if the number includes a '.'

    # Process the number (including potential float)
    while index < len(input_text):
        char = input_text[index]

        if char.isdigit():
            index += 1
        elif char == ".":
            if has_dot:  # If a dot already exists, stop processing (invalid float)
                break
            # Ensure the dot is followed by a digit
            if index + 1 < len(input_text) and input_text[index + 1].isdigit():
                has_dot = True
                index += 1
            else:
                break
        else:
            break

     # Check for invalid identifiers after processing numbers
    if index < len(input_text) and input_text[index].isalpha():
        # If a letter follows the number, it's an invalid identifier
        while index < len(input_text) and (input_text[index].isalnum() or input_text[index] == "_"):
            index += 1
        number_value = input_text[start_index:index]
        return {"type": "INVALID_IDENTIFIER", "value": number_value}, index

    # Otherwise, determine if it's a float or an integer
    number_value = input_text[start_index:index]
    if has_dot:
        num_after_dots = len(number_value.split('.', 1)[1])
        if(num_after_dots < 8):
            return {"type": "FLOAT", "value": number_value}, index
        else:
            return {"type": "DOUBLE", "value": number_value}, index
    else:
        return {"type": "INTEGER", "value": number_value}, index
        
# process a word (keyword or identifier)
def process_word(input_text, index):
    start_index = index
    while index < len(input_text) and (input_text[index].isalnum() or input_text[index] == "_" or input_text[index] in SPECIAL_CHAR):
        index += 1
    word_value = input_text[start_index:index]

    # Handle single-line comments ("//")
    if input_text.startswith("//", index):
        index += 2  # Skip the "//"
        while index < len(input_text) and input_text[index] != "\n":  # Read until end of line
            index += 1
        comment_value = input_text[start_index:index]
        return {"type": "COMMENT_VALUE", "value": comment_value}, index

    # Determine if the word is a keyword, identifier, arith_op, or invalid
    if is_keyword(word_value):
        return generate_keyword(word_value), index
    elif is_res_word(word_value):
        return generate_res_word(word_value), index
    elif is_bool(word_value):
        return generate_bool(word_value), index
    elif word_value[0].isdigit():
        return generate_invalid_identifier(word_value), index
    elif word_value.startswith("_"):
        return generate_invalid_identifier(word_value), index
    elif "__" in word_value:
        return generate_invalid_identifier(word_value), index
    elif any(char in word_value for char in SPECIAL_CHAR):
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
    VALID_OPERATORS = ["*", "/", "%", "^", "#", "=", "!", "&&", "||", "+", "-", "++", "--", 
                       "//", "/*", "*/", "+=", "-=", "/=", "*=", "%=", "==", "!=", ">=", "<=", ">", "<", "#"]
    
    start_index = index
    
    # Check for sequences of consecutive operators like "++", "--", etc.
    while index < len(input_text) and input_text[index] in "+-*/%=!&|<>^":
        index += 1

    # Get the operator sequence
    operator_sequence = input_text[start_index:index]
    
    # Check if the operator sequence is valid
    if operator_sequence in VALID_OPERATORS:
        # If it's a valid operator, check if it's a unary operator like '++' or '--'
        if operator_sequence == "++" or operator_sequence == "--":
            return {"type": "UNARY_OP", "value": operator_sequence}, index
        
        # Check for single line and multiple line comments
        # elif operator_sequence == "//":
        #     return {"type": "COMMENT_SYMBOL", "value": "//"}, index 
        # elif operator_sequence == "/*":
        #     return {"type": "COMMENT_SYMBOL", "value": "/*"}, index
        # elif operator_sequence == "*/":
        #     return {"type": "COMMENT_SYMBOL", "value": "*/"}, index

        # Handle single-line comments ("//")
        if operator_sequence == "//":
            # Collect the comment value until the end of the line
            while index < len(input_text) and input_text[index] != "\n":
                index += 1
            comment_value = input_text[start_index:index]
            return {"type": "SINGLE_LINE_COMMENT", "value": comment_value}, index 
        
        # Handle multi-line comments ("/* */")
        elif operator_sequence == "/*":
            comment_value = ""
            # Collect the comment value until "*/" is found
            while index < len(input_text) and not input_text.startswith("*/", index):
                if input_text[index] != "\n":  # Ignore newline characters
                    comment_value += input_text[index]
                index += 1
            if index < len(input_text):  # If "*/" is found
                index += 2
            comment_value = "/*" + comment_value + "*/"  # Add the delimiters back
            return {"type": "MULIT_LINE_COMMENT", "value": comment_value}, index

        
        # Check for assignment operators
        elif operator_sequence == "=":
            return {"type": "ASSIGNMENT_OP", "value": "="}, index 
        elif operator_sequence == "+=":
            return {"type": "ASSIGNMENT_OP", "value": "+="}, index
        elif operator_sequence == "-=":
            return {"type": "ASSIGNMENT_OP", "value": "-="}, index 
        elif operator_sequence == "*=":
            return {"type": "ASSIGNMENT_OP", "value": "*="}, index 
        elif operator_sequence == "/=":
            return {"type": "ASSIGNMENT_OP", "value": "/="}, index 
        elif operator_sequence == "%=":
            return {"type": "ASSIGNMENT_OP", "value": "%="}, index

        # Check for logical operators
        elif operator_sequence == "||":
            return {"type": "LOGICAL_OP", "value": "||"}, index 
        elif operator_sequence == "&&":
            return {"type": "LOGICAL_OP", "value": "&&"}, index 
        elif operator_sequence == "!":
            return {"type": "LOGICAL_OP", "value": "!"}, index
        
        # Check for relational operators
        elif operator_sequence == "==":
            return {"type": "RELATIONAL_OP", "value": "=="}, index 
        elif operator_sequence == "!=":
            return {"type": "RELATIONAL_OP", "value": "!="}, index 
        elif operator_sequence == ">=":
            return {"type": "RELATIONAL_OP", "value": ">="}, index 
        elif operator_sequence == "<=":
            return {"type": "RELATIONAL_OP", "value": "<="}, index 
        elif operator_sequence == ">":
            return {"type": "RELATIONAL_OP", "value": ">"}, index 
        elif operator_sequence == "<":
            return {"type": "RELATIONAL_OP", "value": "<"}, index 
        
        # Check for unary "+" or "-"
        elif operator_sequence == "+" or operator_sequence == "-":
            # Determine if it should be treated as a unary operator
            if previous_token == None or previous_token and previous_token["type"] in ["DELIMITER", "ASSIGNMENT_OP", "LOGICAL_OP", "RELATIONAL_OP", "COMMENT_SYMBOL", "KEYWORD"]:
                return {"type": "UNARY_OP", "value": operator_sequence}, index 
            else:
                # Otherwise, treat it as an arithmetic operator
                return {"type": "ARITHMETIC_OP", "value": operator_sequence}, index 

        # check for other arithmetic op
        elif operator_sequence in ARITH_OPS:
            return {"type": "ARITHMETIC_OP", "value": operator_sequence}, index 
    
    # If the operator sequence exceeds valid length, it's unrecognized
    if len(operator_sequence) > 2:  # Check if it's more than two consecutive symbols
        return {"type": "UNRECOGNIZED_OPERATOR", "value": operator_sequence}, index

    return None, index

# process char and string
def process_quotes(input_text, index):
    quote_type = input_text[index]  # Either single or double quote
    start_index = index
    index += 1  # Move past the opening quote
    content = ""

    while index < len(input_text):
        char = input_text[index]
        
        # If we encounter the matching closing quote
        if char == quote_type:
            index += 1  # Move past the closing quote
            if len(content) == 1:
                return {"type": "CHAR", "value": content}, index
            else:
                return {"type": "STRING", "value": content}, index
        
        # Otherwise, add character to the content
        content += char
        index += 1

    # If no closing quote is found, it's an invalid string or char
    return {"type": "INVALID_CHAR/STRING", "value": input_text[start_index:index]}, index

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
        
        # Handle quotes (single and double)
        if char in ["'", '"']:
            token, index = process_quotes(input_text, index)
            tokens.append(token)
            previous_token = token
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

        # Process numbers and float
        elif char.isdigit() or (char == "." and index + 1 < length and input_text[index + 1].isdigit()):
            token, new_index = process_number(input_text, index, previous_token)
            tokens.append(token)
            previous_token = token
            index = new_index
            continue

        # Process words (keywords, reserved words, identifiers, or invalid identifiers)
        elif char.isalpha() or char == "_" or input_text[index] in SPECIAL_CHAR:
            token, index = process_word(input_text, index)
            tokens.append(token)
            previous_token = token
            continue

        # Handle unrecognized characters
        else:
            print(f"Warning: Unrecognized character '{char}' at index {index}")
            index += 1

    return tokens

# Check if the file has a .cts extension
def validate_file_extension(filename):
    if not filename.endswith('.cat'):
        raise ValueError(f"Invalid file extension: {filename}. Only .cat files are allowed.")
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    return True

def main():
    try:
        # Example filename (replace with user input or actual filename)
        filename = "test.cat"
        
        # Validate the file extension
        validate_file_extension(filename)
        
        # Open and process the file (if valid)
        with open(filename, 'r') as file:
            input_text = file.read()
        
        # Call your lexer function or other processing logic
        tokens = lexer(input_text)
        for token in tokens:
            print(token)
    
    except ValueError as ve:
        print(ve)
    except FileNotFoundError as fnfe:
        print(fnfe)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the main function
if __name__ == "__main__":
    main()