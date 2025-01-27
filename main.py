from enum import Enum
import string
import os
import csv
    
KEYWORDS = ["int", "float", "double", "char", "bool", "string", "if", "else", "for", "while", "break", "continue", "printf", "scanf"]
RES_WORDS = ["gc", "main", "malloc", "true", "false"]
NOISE_WORDS = ["boolean" , "integer", "character"] 
ARITH_OPS = ["*", "/", "%", "^", "#"]
DELI = [";", "(", ")", "[", "]", "{", "}", ","]
BOOL = ["True", "False", "TRUE", "FALSE", "true", "false"]
SPECIAL_CHAR = {"~", "?", "@","$", "|", "&", "."}

# check if a word is a keyword
def is_keyword(word):
    return word in KEYWORDS

# check if a word is a reserved word
def is_res_word(word):
    return word in RES_WORDS

# check if a word is a boolean value
def is_bool(word):
    return word in BOOL

def is_noise(word):
    return word in NOISE_WORDS

# generate a token for a keyword
def generate_keyword(value):
    return {"type": "KEYWORD", "value": value}

# generate a token for a reserved word
def generate_res_word(value):
    return {"type": "RESERVED_WORD", "value": value}

# generate a token for a boolean value
def generate_bool(value):
    return {"type": "BOOLEAN", "value": value}

# generate a token for an identifier
def generate_identifier(value):
    return {"type": "IDENTIFIER", "value": value}

# generate a token for an invalid identifier
def generate_invalid_identifier(value):
    return {"type": "INVALID_IDENTIFIER", "value": value}

def generate_noise_word(value):
    return {"type": "NOISE_WORD", "value": value}

# Process a delimiter
def process_deli(char):
    if char in DELI:
        return {"type": "DELIMITER", "value": char}
    return None

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

    # Determine if the word is a keyword, identifier, arith_op, or invalid
    if is_keyword(word_value):
        return generate_keyword(word_value), index
    elif is_res_word(word_value):
        return generate_res_word(word_value), index
    elif is_bool(word_value):
        return generate_bool(word_value), index
    elif is_noise(word_value):
        return generate_noise_word(word_value), index
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

# Process unary and arithmetic operators
def process_operator(input_text, index, previous_token):
    VALID_OPERATORS = ["*", "/", "%", "^", "#", "=", "!", "&&", "||", "+", "-", "++", "--", "&",
                       "//", "/*", "*/", "+=", "-=", "/=", "*=", "%=", "==", "!=", ">=", "<=", ">", "<"]
    
    start_index = index
    
    # Check for sequences of consecutive operators like "++", "--", etc.
    while index < len(input_text) and input_text[index] in "#+-*/%=!&|<>^":
        index += 1

    # Get the operator sequence
    operator_sequence = input_text[start_index:index]
    
    # Check if the operator sequence is valid
    if operator_sequence in VALID_OPERATORS:
        # If it's a valid operator, check if it's a unary operator like '++' or '--'
        if operator_sequence == "++" or operator_sequence == "--":
            return {"type": "UNARY_OP", "value": operator_sequence}, index

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
        
        # Check for address operator
        elif operator_sequence == "&":
            return {"type": "ADDRESS_OP", "value": "&"}, index
        
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
            if previous_token == None or previous_token and previous_token["type"] in ["DELIMITER", "ASSIGNMENT_OP", "LOGICAL_OP", "RELATIONAL_OP", "COMMENT_SYMBOL", "KEYWORD", "NOISE_WORD"]:
                return {"type": "UNARY_OP", "value": operator_sequence}, index 
            else:
                # Otherwise, treat it as an arithmetic operator
                return {"type": "ARITHMETIC_OP", "value": operator_sequence}, index 

        # check for other arithmetic op
        elif operator_sequence in ARITH_OPS:
            return {"type": "ARITHMETIC_OP", "value": operator_sequence}, index 
    
    #for invalid operators that are not more than 3
    if operator_sequence and operator_sequence not in VALID_OPERATORS:
        return {"type": "UNRECOGNIZED_OPERATOR", "value": operator_sequence}, index

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
            if len(content) == 0:
                return {"type": "EMPTY_STRING", "value": content}, index
            if len(content) == 1:
                return {"type": "CHAR", "value": content}, index
            else:
                return {"type": "STRING", "value": content}, index
        
        if char == "\n":
            break
        
        # Otherwise, add character to the content
        content += char
        index += 1

    # If no closing quote is found, it's an invalid string or char
    if(char == "\n"):
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

# Check if the file has a .cat extension
def validate_file_extension(filename):
    if not filename.endswith('.cat'):
        raise ValueError(f"Invalid file extension: {filename}. Only .cat files are allowed.")
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    return True

# Function to write tokens to a CSV file
def write_tokens_to_csv(tokens, filename="LexOutput.csv"):
    """
    Writes the list of tokens to a CSV file.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write the header
        writer.writerow(["Token Value", "Token Type"])
        
        # Write the tokens
        for token in tokens:
            token_type = token["type"]
            token_value = token["value"]
            writer.writerow([token_value, token_type]) 
    
    print(f"Tokens successfully written to {filename}")
    return True

def main():
    while True:
        try:
            # Ask user for the input file name
            input_filename = input("Enter the name of the .cat file to process: ").strip()
            
            # Validate the input file name
            if validate_file_extension(input_filename):
                break  # Exit loop if the file is valid

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    try:
        # Open and process the file (if valid)
        with open(input_filename, 'r') as file:
            input_text = file.read()
        
        # Call your lexer function or other processing logic
        tokens = lexer(input_text)  # Replace with your lexer implementation
        
        while True:
            # Ask user for the output CSV file name
            output_filename = input("Enter the name of the CSV file to save the tokens (e.g., tokens.csv): ").strip()
            
            # Ensure it has a .csv extension
            if not output_filename.endswith('.csv'):
                print("Invalid file extension. Please provide a filename ending with '.csv'.")
                continue
            
            # Write tokens to the specified CSV file
            write_tokens_to_csv(tokens, output_filename)
            break  # Exit the loop once the tokens are written successfully

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the main function
if __name__ == "__main__":
    main()