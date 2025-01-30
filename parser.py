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

    def skip_to_next_statement(self):
        """
        Skips tokens until a semicolon or a new declaration keyword is found.
        This prevents infinite loops when encountering syntax errors.
        """
        while self.current_token():
            token = self.current_token()

            # If we find a semicolon, move past it and stop skipping
            if token["type"] == "SEMI-COLON_DELI":
                print(f"Stopping at: {token['value']}")  # Debugging output
                self.next_token()
                return  
            # If we find a new valid declaration keyword (int, float, etc.), stop skipping
            if token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "BOOL_KEY", "STRING_KEY"]:
                return

            self.next_token()  # Skip unrecognized tokens

    def parse_declaration(self):
        """
        Parses a declaration statement (e.g., int x = 5;).
        """            
        token = self.current_token()
        if not token:
            return  # End of tokens

        line_number = token["line_number"]

        # Step 1: Check for a valid type keyword (int, float, etc.)
        if token["type"] not in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "BOOL_KEY", "STRING_KEY"]:
            raise SyntaxError("Expected a type keyword at the beginning of the declaration.", line_number)
        
        declaration_type = token["value"]
        self.next_token()

        variables = []

        while True:
            # Step 2: Check for a valid identifier
            token = self.current_token()
            if token and token["type"] != "IDENTIFIER":
                self.skip_to_next_statement()  # Skip to next statement after error
                raise SyntaxError("Expected an identifier after the type.", line_number)
            
            identifier = token["value"]
            self.next_token()

            # Step 3: Check for an optional assignment or a semicolon
            token = self.current_token()
            if token and token["type"] in ["ASSIGN_OP", "PLUS-ASSIGN_OP", "MINUS-ASSIGN_OP", "MULTI-ASSIGN_OP", "DIVIDE-ASSIGN_OP", "MOD-ASSIGN_OP"]:  # Handle assignment
                self.next_token()
                token = self.current_token()

                # Ensure a valid value follows the assignment
                if not token or token["type"] not in ["INTEGER", "FLOAT", "DOUBLE", "CHAR", "STRING", "TRUE_BOOL", "FALSE_BOOL", "IDENTIFIER"]:
                    self.skip_to_next_statement()  # Skip to next statement after error
                    raise SyntaxError("Expected a valid value after assignment.", line_number)
                
                value = token["value"]
                variables.append(f"{identifier} = {value}")
                self.next_token()   
            else:
                variables.append(identifier)  # Just store the variable name
            
            # Step 4: Check for a comma (more variables) or semicolon (end of declaration)
            token = self.current_token()
            if token and token["type"] == "COMMA_DELI":
                self.next_token()  # Move to the next variable
                continue  # Continue processing more variables
            elif token and token["type"] == "SEMI-COLON_DELI":  
                break  # End of declaration
            else:
                #self.next_token()
                #token = self.current_token()
                self.skip_to_next_statement()
                raise SyntaxError("Missing semicolon at the end of the declaration.", line_number)
        
        identifier_list = ", ".join(variables)
        print(f"Valid variable declaration: {declaration_type} {identifier_list}; (Line {line_number})")
        self.next_token()  # Move to the next token after semicolon

    def parse_for_loop(self):
        """
        Parses a 'for' loop statement following:
        <For_Loop> ::= "for" "("<Init> ";" <Condition> ";" <Update> ")" <Body>
        """
        token = self.current_token()
        line_number = token["line_number"]

        if not token or token["type"] != "FOR_KEY":
            raise SyntaxError("❌ Expected 'for' keyword.", line_number)

        self.next_token()  # Move past 'for'
        
        # Expect '('
        token = self.current_token()
        if not token or token["type"] != "OPEN-PAREN_DELI":
            raise SyntaxError("❌ Expected '(' after 'for'.", line_number)
        
        self.next_token()  # Move past '('

        # === <Init> ::= ( <Dat_Type> <Identifier> "=" <Expression> ) | ( <Identifier> "=" <Expression> ) ===
        token = self.current_token()
        if token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "BOOL_KEY", "STRING_KEY"]:
            try:
                self.parse_declaration()  # Valid variable declaration (already handles ';')
            except SyntaxError as e:
                print(f"error: {e}")
                self.skip_to_next_statement()
        elif token["type"] == "IDENTIFIER":
            self.next_token()  # Move past identifier
            token = self.current_token()
            if token["type"] != "ASSIGN_OP":
                raise SyntaxError("❌ Expected '=' in initialization.", line_number)
            
            self.next_token()  # Move past '='
            token = self.current_token()
            if token["type"] not in ["INTEGER", "FLOAT", "DOUBLE", "CHAR", "STRING", "TRUE_BOOL", "FALSE_BOOL", "IDENTIFIER"]:
                raise SyntaxError("❌ Expected a valid expression in initialization.", line_number)
            self.next_token()  # Move past expression

            # Ensure the next token is a ';'
            token = self.current_token()
            if not token or token["type"] != "SEMI-COLON_DELI":
                raise SyntaxError("❌ Missing ';' after initialization.", line_number)
            self.next_token()  # Move past ';'
        else:
            raise SyntaxError("❌ Invalid initialization in 'for' loop.", line_number)

        # === <Condition> ::= <Identifier> <Rel_Op> <Expression> | <Expression> <Logic_Op> <Expression> ===
        token = self.current_token()
        if token["type"] not in ["IDENTIFIER", "INTEGER"]:
            raise SyntaxError("❌ Expected a condition expression after initialization.", line_number)

        condition_expr = []
        while token and token["type"] not in ["SEMI-COLON_DELI"]:
            condition_expr.append(token["value"])
            self.next_token()
            token = self.current_token()

        if not token or token["type"] != "SEMI-COLON_DELI":
            raise SyntaxError("❌ Missing ';' after condition.", line_number)
        self.next_token()  # Move past ';'

        # === <Update> ::= <Identifier> <Increment> | <Identifier> <Assign_Op> <Expression> | <Update> "," <Update> ===
        updates = []
        while token and token["type"] != "CLOSE-PAREN_DELI":
            token = self.current_token()
            if not token:
                raise SyntaxError("❌ Expected update expression before ')'.", line_number)
            
            if token["type"] == "IDENTIFIER":
                update_expr = token["value"]
                self.next_token()  # Move past identifier

                token = self.current_token()
                if token and token["type"] in ["INCRE_OP", "DECRE_OP", "ASSIGN_OP", "PLUS-ASSIGN_OP", "MINUS-ASSIGN_OP", "MULTI-ASSIGN_OP", "DIVIDE-ASSIGN_OP", "MOD-ASSIGN_OP"]:
                    update_expr += f" {token['value']}"
                    self.next_token()  # Move past operator

                    if token["type"] in ["ASSIGN_OP", "PLUS-ASSIGN_OP", "MINUS-ASSIGN_OP", "MULTI-ASSIGN_OP", "DIVIDE-ASSIGN_OP", "MOD-ASSIGN_OP"]:
                        token = self.current_token()
                        if token and token["type"] in ["INTEGER", "FLOAT", "DOUBLE", "CHAR", "STRING", "IDENTIFIER"]:
                            update_expr += f" {token['value']}"
                            self.next_token()  # Move past expression
                        else:
                            raise SyntaxError("❌ Expected a valid expression after assignment in update.", line_number)
                    
                    updates.append(update_expr)
                else:
                    raise SyntaxError("❌ Invalid update expression.", line_number)

                token = self.current_token()
                if token and token["type"] == "COMMA_DELI":
                    self.next_token()  # Move past comma
                elif token and token["type"] == "CLOSE-PAREN_DELI":
                    break  # End of update expressions
                else:
                    raise SyntaxError("❌ Unexpected token in update section.", line_number)
            else:
                raise SyntaxError("❌ Invalid update expression.", line_number)

        if not token or token["type"] != "CLOSE-PAREN_DELI":
            raise SyntaxError("❌ Expected ')' at the end of 'for' loop header.", line_number)

        self.next_token()  # Move past ')'

        print(f"✅ Valid for loop detected on line {line_number}: for ({' '.join(condition_expr)}; {', '.join(updates)})")

        # === <Body> ::= "{" <Statements> "}" ===
        token = self.current_token()
        if not token or token["type"] != "OPEN-CURL-BRAC_DELI":
            raise SyntaxError("❌ Expected '{' after 'for' loop header.", line_number)

        self.next_token()  # Move past '{'

        # **Parse statements inside loop body**
        while self.current_token():
            token = self.current_token()
            
            # Stop when we reach '}'
            if token["type"] == "CLOSE-CURL-BRAC_DELI":
                self.next_token()  # Move past '}'
                print(f"✅ End of 'for' loop block on line {line_number}")
                return
            
            # Handle declarations or statements inside loop body
            try:
                self.parse_declaration()
            except SyntaxError as e:
                print(f"error: {e}")
                self.skip_to_next_statement()
            
                