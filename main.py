from enum import Enum
from parser import Parser, SyntaxError
import string
import os
import csv
    
KEYWORDS = ["int", "float", "double", "char", "bool", "string", "if", "else", "for", "while", "break", "continue", "printf", "scanf", "return"]
RES_WORDS = ["gc", "main", "malloc"]
NOISE_WORDS = ["boolean" , "integer", "character"] 
ARITH_OPS = ["*", "/", "%", "^", "#"]
DELI = [";", "(", ")", "[", "]", "{", "}", ","]
BOOL = ["True", "False", "TRUE", "FALSE", "true", "false"]
SPECIAL_CHAR = {"~", "?", "@","$", "|", "."}

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

# Process a delimiter
def process_deli(char, line_number):
    if char in DELI:
        if char == ";":
            return {"type": "SEMI-COLON_DELI", "value": char, "line_number": line_number}
        if char == "(":
            return {"type": "OPEN-PAREN_DELI", "value": char, "line_number": line_number}
        if char == ")":
            return {"type": "CLOSE-PAREN_DELI", "value": char, "line_number": line_number}
        if char == "[":
            return {"type": "OPEN-BRAC_DELI", "value": char, "line_number": line_number}
        if char == "]":
            return {"type": "CLOSE-BRAC_DELI", "value": char, "line_number": line_number}
        if char == "{":
            return {"type": "OPEN-CURL-BRAC_DELI", "value": char, "line_number": line_number}
        if char == "}":
            return {"type": "CLOSE-CURL-BRAC_DELI", "value": char, "line_number": line_number}
        if char == ",":
            return {"type": "COMMA_DELI", "value": char, "line_number": line_number}
    return None

# process a number
def process_number(input_text, index, line_number):
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
        return {"type": "DIGIT_INVAL_IDEN", "value": number_value, "line_number": line_number}, index

    # Otherwise, determine if it's a float or an integer
    number_value = input_text[start_index:index]
    if has_dot:
        num_after_dots = len(number_value.split('.', 1)[1])
        if(num_after_dots < 8):
            return {"type": "FLOAT", "value": number_value, "line_number": line_number}, index
        else:
            return {"type": "DOUBLE", "value": number_value, "line_number": line_number}, index
    else:
        return {"type": "INTEGER", "value": number_value, "line_number": line_number}, index

# process a word (keyword or identifier)
def process_word(input_text, index, line_number):
    start_index = index
    while index < len(input_text) and (input_text[index].isalnum() or input_text[index] == "_" or input_text[index] in SPECIAL_CHAR):
        index += 1
    word_value = input_text[start_index:index]

    # Determine if the word is a keyword, identifier, arith_op, or invalid
    if is_keyword(word_value):
        if word_value == "int":
            return {"type": "INT_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "float":
            return {"type": "FLOAT_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "double":
            return {"type": "DOUBLE_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "char":
            return {"type": "CHAR_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "bool":
            return {"type": "BOOL_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "string":
            return {"type": "STRING_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "if":
            return {"type": "IF_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "else":
            return {"type": "ELSE_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "for":
            return {"type": "FOR_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "while":
            return {"type": "WHILE_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "break":
            return {"type": "BREAK_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "continue":
            return {"type": "CONTINUE_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "printf":
            return {"type": "PRINTF_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "scanf":
            return {"type": "SCANF_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "return":
            return {"type": "RETURN_KEY", "value": word_value, "line_number": line_number}, index
    elif is_res_word(word_value):
        if word_value == "gc":
            return {"type": "GC_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "main":
            return {"type": "MAIN_KEY", "value": word_value, "line_number": line_number}, index
        if word_value == "malloc":
            return {"type": "MALLOC_KEY", "value": word_value, "line_number": line_number}, index
    elif is_bool(word_value):
        if word_value == "True":
            return {"type": "TRUE_BOOL", "value": word_value, "line_number": line_number}, index
        if word_value == "False":
            return {"type": "FALSE_BOOL", "value": word_value, "line_number": line_number}, index
        if word_value == "TRUE":
            return {"type": "TRUE_BOOL", "value": word_value, "line_number": line_number}, index
        if word_value == "FALSE":
            return {"type": "FALSE_BOOL", "value": word_value, "line_number": line_number}, index
        if word_value == "true":
            return {"type": "TRUE_BOOL", "value": word_value, "line_number": line_number}, index
        if word_value == "false":
            return {"type": "FALSE_BOOL", "value": word_value, "line_number": line_number}, index
    elif is_noise(word_value):
        if word_value == "boolean":
            return {"type": "BOOL_NOISE", "value": word_value, "line_number": line_number}, index
        if word_value == "integer":
            return {"type": "INT_NOISE", "value": word_value, "line_number": line_number}, index
        if word_value == "character":
            return {"type": "CHAR_NOISE", "value": word_value, "line_number": line_number}, index
    elif word_value[0].isdigit():
        return {"type": "DIGIT_INVAL_IDEN", "value": word_value, "line_number": line_number}, index
    elif word_value.startswith("_"):
        return {"type": "UNDER_INVAL_IDEN", "value": word_value, "line_number": line_number}, index
    elif "__" in word_value:
        return {"type": "UNDER_INVAL_IDEN", "value": word_value, "line_number": line_number}, index
    elif any(char in word_value for char in SPECIAL_CHAR):
        return {"type": "SPECIAL_INVAL_IDEN", "value": word_value, "line_number": line_number}, index
    elif word_value.endswith("_"):
        return {"type": "UNDER_INVAL_IDEN", "value": word_value, "line_number": line_number}, index
    else:
        return {"type": "IDENTIFIER", "value": word_value, "line_number": line_number}, index

# Process unary and arithmetic operators
def process_operator(input_text, index, previous_token, line_number):
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
        if operator_sequence == "++":
            return {"type": "INCRE_OP", "value": operator_sequence, "line_number": line_number}, index
        if operator_sequence == "--":
            return {"type": "DECRE_OP", "value": operator_sequence, "line_number": line_number}, index

        # Handle single-line comments ("//")
        if operator_sequence == "//":
            # Collect the comment value until the end of the line
            while index < len(input_text) and input_text[index] != "\n":
                index += 1
            comment_value = input_text[start_index:index]
            return {"type": "SINGLE_LINE_COMMENT", "value": comment_value, "line_number": line_number}, index 
        
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
            return {"type": "MULIT_LINE_COMMENT", "value": comment_value, "line_number": line_number}, index
        
        # Check for address operator
        elif operator_sequence == "&":
            return {"type": "ADDRESS_OP", "value": "&", "line_number": line_number}, index
        
        # Check for assignment operators
        elif operator_sequence == "=":
            return {"type": "ASSIGN_OP", "value": "=", "line_number": line_number}, index 
        elif operator_sequence == "+=":
            return {"type": "PLUS-ASSIGN_OP", "value": "+=", "line_number": line_number}, index
        elif operator_sequence == "-=":
            return {"type": "MINUS-ASSIGN_OP", "value": "-=", "line_number": line_number}, index 
        elif operator_sequence == "*=":
            return {"type": "MULTI-ASSIGN_OP", "value": "*=", "line_number": line_number}, index 
        elif operator_sequence == "/=":
            return {"type": "DIVIDE-ASSIGN_OP", "value": "/=", "line_number": line_number}, index 
        elif operator_sequence == "%=":
            return {"type": "MOD-ASSIGN_OP", "value": "%=", "line_number": line_number}, index

        # Check for logical operators
        elif operator_sequence == "||":
            return {"type": "OR-LOGIC_OP", "value": "||", "line_number": line_number}, index 
        elif operator_sequence == "&&":
            return {"type": "AND-LOGIC_OP", "value": "&&", "line_number": line_number}, index 
        elif operator_sequence == "!":
            return {"type": "NOT-LOGIC_OP", "value": "!", "line_number": line_number}, index
        
        # Check for relational operators
        elif operator_sequence == "==":
            return {"type": "EQUAL-REL_OP", "value": "==", "line_number": line_number}, index 
        elif operator_sequence == "!=":
            return {"type": "NOT-REL_OP", "value": "!=", "line_number": line_number}, index 
        elif operator_sequence == ">=":
            return {"type": "GREAT-EQL-REL_OP", "value": ">=", "line_number": line_number}, index 
        elif operator_sequence == "<=":
            return {"type": "LESS-EQL-REL_OP", "value": "<=", "line_number": line_number}, index 
        elif operator_sequence == ">":
            return {"type": "LESS-REL_OP", "value": ">", "line_number": line_number}, index 
        elif operator_sequence == "<":
            return {"type": "GREAT-REL_OP", "value": "<", "line_number": line_number}, index 
        
        # Check for unary "+" or "-"
        elif operator_sequence == "+" or operator_sequence == "-":
            # Determine if it should be treated as a unary operator
            if previous_token == None or previous_token and previous_token["type"] in ["DELIMITER", "ASSIGNMENT_OP", "LOGICAL_OP", 
                                                                                       "RELATIONAL_OP", "COMMENT_SYMBOL", "KEYWORD", 
                                                                                       "NOISE_WORD", "ASSIGN_OP"]:
                if operator_sequence == "+":
                    return {"type": "UNARY-PLUS_OP", "value": operator_sequence, "line_number": line_number}, index
                if operator_sequence == "-":
                    return {"type": "UNARY-MINUS_OP", "value": operator_sequence, "line_number": line_number}, index  
            else:
                if operator_sequence == "+":
                    return {"type": "PLUS-ARITH_OP", "value": operator_sequence, "line_number": line_number}, index
                if operator_sequence == "-":
                    return {"type": "MINUS-ARITH_OP", "value": operator_sequence, "line_number": line_number}, index
                if operator_sequence == "*":
                    return {"type": "MULTI-ARITH_OP", "value": operator_sequence, "line_number": line_number}, index
                if operator_sequence == "/":
                    return {"type": "DIV-ARITH_OP", "value": operator_sequence, "line_number": line_number}, index
                if operator_sequence == "%":
                    return {"type": "MOD-ARITH_OP", "value": operator_sequence, "line_number": line_number}, index
                if operator_sequence == "^":
                    return {"type": "POWER-ARITH_OP", "value": operator_sequence, "line_number": line_number}, index
                if operator_sequence == "#":
                    return {"type": "ROOT-ARITH_OP", "value": operator_sequence, "line_number": line_number}, index 
    
    #for invalid operators that are not more than 3
    if operator_sequence and operator_sequence not in VALID_OPERATORS:
        return {"type": "UNRECOGNIZED_OPERATOR", "value": operator_sequence, "line_number": line_number}, index

    # If the operator sequence exceeds valid length, it's unrecognized
    if len(operator_sequence) > 2:  # Check if it's more than two consecutive symbols
        return {"type": "UNRECOGNIZED_OPERATOR", "value": operator_sequence, "line_number": line_number}, index

    return None, index

# process char and string
def process_quotes(input_text, index, line_number):
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
                return {"type": "EMPTY-STRING", "value": content, "line_number": line_number}, index
            if len(content) == 1:
                return {"type": "CHAR_KEY", "value": content, "line_number": line_number}, index
            else:
                return {"type": "STRING_KEY", "value": content, "line_number": line_number}, index
        
        if char == "\n":
            break
        
        # Otherwise, add character to the content
        content += char
        index += 1

    # If no closing quote is found, it's an invalid string or char
    if(char == "\n"):
        return {"type": "INVALID_CHAR/STRING", "value": input_text[start_index:index], "line_number": line_number}, index

# main lexer function    
def lexer(input_text):
    index = 0
    tokens = []
    length = len(input_text)
    previous_token = None
    line_number = 1  # Track the current line number
    first_loop = True  # Flag to track the first loop execution

    while index < len(input_text):
        char = input_text[index]
        
        if first_loop and char == "\n":
            line_number += 1 
            index += 1
            first_loop = False
            continue

        # Handle Newlines (Only Tokenize EMPTY LINES)
        if char == "\n":
            line_number += 1
            index += 1
            continue

        # Skip whitespace
        if char.isspace():
            index += 1
            continue
        
        # Handle quotes (single and double)
        if char in ["'", '"']:
            token, index = process_quotes(input_text, index, line_number)
            token["line_number"] = line_number  # Store the line number
            tokens.append(token)
            previous_token = token
            continue

        # Handle delimiters
        delimiter_token = process_deli(char, line_number)
        if delimiter_token:
            delimiter_token["line_number"] = line_number
            tokens.append(delimiter_token)
            previous_token = delimiter_token  # Update previous_token
            index += 1
            continue
        
        # Handle unary and arithmetic operators
        un_op_token, new_index = process_operator(input_text, index, previous_token, line_number)
        if un_op_token:
            un_op_token["line_number"] = line_number
            tokens.append(un_op_token)
            previous_token = un_op_token
            index = new_index
            continue

        # Process numbers and float
        elif char.isdigit() or (char == "." and index + 1 < length and input_text[index + 1].isdigit()):
            token, new_index = process_number(input_text, index, line_number)
            token["line_number"] = line_number
            tokens.append(token)
            previous_token = token
            index = new_index
            continue

        # Process words (keywords, reserved words, identifiers, or invalid identifiers)
        elif char.isalpha() or char == "_" or input_text[index] in SPECIAL_CHAR:
            token, index = process_word(input_text, index, line_number)
            token["line_number"] = line_number
            tokens.append(token)
            previous_token = token
            continue

        # Handle unrecognized characters
        else:
            print(f"Warning: Unrecognized character '{char}' at index {index}, line {line_number}")
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
        writer.writerow(["Line Number", "Token Value", "Token Type"])
        
        # Write the tokens
        for token in tokens:
            token_type = token["type"]
            token_value = token["value"]
            line_number = token.get("line_number", "Unknown")

            writer.writerow([line_number, token_value, token_type]) 
    
    print(f"Tokens successfully written to {filename}")
    return True

def main():
    while True:
        try:
            # Ask user for the input file name for lexical analysis
            input_filename = input("Enter the name of the .cat file to process: ").strip()
            
            # Validate the input file name
            if validate_file_extension(input_filename):
                break  # Exit loop if the file is valid

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    try:
        # Open and process the .cat file
        with open(input_filename, 'r') as file:
            input_text = file.read()
        
        # Call your lexer function to generate tokens
        tokens = lexer(input_text)

        # Save tokens to a user-specified CSV file
        while True:
            output_filename = input("Enter the name of the CSV file to save the tokens (e.g., tokens.csv): ").strip()
            if not output_filename.endswith('.csv'):
                print("Invalid file extension. Please provide a filename ending with '.csv'.")
                continue
            
            # Write tokens to the specified CSV file
            write_tokens_to_csv(tokens, output_filename)
            break

        # Loop to ask for a valid CSV file to load tokens for parsing
        while True:
            try:
                parse_filename = input("Enter the name of the CSV file to load tokens for parsing: ").strip()

                # Ensure the file exists
                if not os.path.isfile(parse_filename):
                    print(f"File not found: {parse_filename}. Please try again.")
                    continue

                tokens_from_csv = []

                # Read the tokens from the CSV file
                with open(parse_filename, mode="r", encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader, None)  # Skip header row if present

                    for row in reader:
                        if len(row) < 3:
                            print(f"Warning: Skipping malformed CSV row: {row}")
                            continue  # Skip malformed rows

                        try:
                            line_number = int(row[0])  # Convert to integer safely
                        except ValueError:
                            print(f"Warning: Invalid line number '{row[0]}' in CSV. Skipping row.")
                            continue

                        tokens_from_csv.append({
                            "line_number": line_number,
                            "value": row[1],
                            "type": row[2]
                        })

                if not tokens_from_csv:
                    print("Error: No valid tokens found in the CSV file.")
                    continue
                
                # Ask user for the CSV file to save errors
                error_filename = input("Enter the name of the CSV file to save parsing errors: ").strip()
                if not error_filename.endswith(".csv"):
                    print("Invalid file extension. Please provide a filename ending with '.csv'.")
                    continue

                # Initialize the parser and parse the tokens
                parser = Parser(tokens_from_csv)
                errors = []  # Store errors
        
                while parser.current_token():
                    result = parser.parse_statement()
                    if result:
                        errors.extend(result)


                # Write errors to CSV file
                with open(error_filename, mode="w", newline="", encoding="utf-8") as error_file:
                    writer = csv.writer(error_file)
                    writer.writerow(["Error Message"])  # Header

                    if errors:
                        for error in errors:
                            writer.writerow([error])
                        writer.writerow([f"Total Errors: {len(errors)}"])  # Error count
                    else:
                        writer.writerow(["No errors found."])
                print(f"Errors successfully written to {error_filename}")
                
                break  # Exit loop after successful parsing
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the main function
if __name__ == "__main__":
    main()