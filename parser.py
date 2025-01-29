class SyntaxError(Exception):
    """Custom exception for syntax errors, now includes line number."""
    def __init__(self, message, line_number):
        super().__init__(f"Syntax Error on line {line_number}: {message}")
        self.line_number = line_number

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.line_number = 1  # Track current line number

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def next_token(self):
        """ Advances to the next token, skipping any NEWLINE tokens. """
        while self.current_token_index < len(self.tokens):
            self.current_token_index += 1
            return self.current_token()  # Return the next non-NEWLINE token
        return None  # End of tokens

    def parse_declaration(self):
        """
        Parses a declaration statement (e.g., int x = 5;).
        """            
        
        token = self.current_token()

        line_number = token["line_number"]

        # Step 1: Check for a valid type keyword (int, float, etc.)
        if token and token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "BOOL_KEY", "STRING_KEY"]:
            declaration_type = token["value"]
            self.next_token()

            # Step 2: Check for a valid identifier
            token = self.current_token()
            if token and token["type"] == "IDENTIFIER":
                identifier = token["value"]
                self.next_token()

                # Step 3: Check for an optional assignment or a semicolon
                token = self.current_token()
                if token and token["type"] == "ASSIGN_OP":  # Handle assignment
                    self.next_token()
                    token = self.current_token()

                    # Check if the next token is a valid value type (e.g., INTEGER, FLOAT, etc.)
                    if token and token["type"] in ["INTEGER", "FLOAT", "DOUBLE", "CHAR", "STRING", "BOOLEAN"]:
                        value = token["value"]
                        self.next_token()
                        token = self.current_token()

                        if token and token["type"] == "SEMI-COLON_DELI":
                            print(f"Valid variable declaration: {declaration_type} {identifier} = {value}; (Line {line_number})")
                            self.next_token()
                        else:
                            raise SyntaxError("Missing semicolon at the end of the declaration.", line_number)
                    else:
                        raise SyntaxError("Expected a valid value after assignment.", line_number)
                elif token and token["type"] == "SEMI-COLON_DELI":  # Handle without assignment
                    print(f"Valid variable declaration: {declaration_type} {identifier}; (Line {line_number})")
                    self.next_token()
                else:
                    raise SyntaxError("Invalid variable declaration syntax.", line_number)
            else:
                raise SyntaxError("Expected an identifier after the type.", line_number)
        else:
            raise SyntaxError("Expected a type keyword at the beginning of the declaration.", line_number)
            