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

    def skip_to_next_declaration(self):
        """
        Skips tokens until a semicolon (`;`), a new declaration keyword, or a closing `}` is found.
        Also ensures proper skipping inside `for` loops or block structures.
        """
        while self.current_token():
            token = self.current_token()

            # Stop at a semicolon - likely end of a statement
            if token["type"] == "SEMI-COLON_DELI":
                print(f"🔹 Skipping to next statement. Stopping at: {token['value']}")  # Debugging output
                self.next_token()
                return  

            # Stop if a new valid declaration keyword is found (int, float, etc.)
            if token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "BOOL_KEY", "STRING_KEY"]: 
                return

            self.next_token()  # Skip any other unrecognized tokens

    def skip_to_next_for_loop(self):
        """
        Skips tokens until a closing parenthesis `)` is found, ensuring proper handling inside a `for` loop.
        Also, if an error happens inside the loop body, it skips until a closing brace `}` is found.
        """
        while self.current_token():
            token = self.current_token()

            # Stop at a closing parenthesis - likely end of for-loop header
            if token["type"] == "CLOSE-PAREN_DELI":
                print(f"🔹 Skipping to end of for loop header. Stopping at: {token['value']}")
                self.next_token()
                return  

            # Stop at a closing brace - likely end of loop body
            if token["type"] == "CLOSE-CURL-BRAC_DELI":
                print(f"🔹 Skipping to end of loop body. Stopping at: {token['value']}")
                self.next_token()
                return  

            self.next_token()  # Skip any other unrecognized tokens

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
                self.skip_to_next_declaration()  # Skip to next statement after error
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
                    self.skip_to_next_declaration()  # Skip to next statement after error
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
                self.skip_to_next_declaration()
                raise SyntaxError("Missing semicolon or Assignment Operator at the end of the declaration.", line_number)
        
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
             # Handle type keyword (e.g., "int i = 0;")
            self.next_token()

            token = self.current_token()
            if token["type"] == "IDENTIFIER":
                #raise SyntaxError("❌ Expected an identifier after type in initialization.", line_number)
                self.next_token()
                token = self.current_token()

                # Expect assignment operator and value
                if token["type"] == "ASSIGN_OP":
                    
                    self.next_token()
                    token = self.current_token()

                    if not token or token["type"] not in ["INTEGER", "FLOAT", "DOUBLE", "CHAR", "STRING"]:
                        raise SyntaxError("❌ Expected a value after '=' in initialization.", line_number) 
                    self.next_token()
                    
            else:
                raise SyntaxError("❌ Expected an Identifier after the Keyword.", line_number)  
        elif token["type"] == "IDENTIFIER":
            # Handle without type (e.g., "i = 0;")
            self.next_token()
            token = self.current_token()
        else:
            raise SyntaxError("❌ Invalid initialization in for loop.", line_number)  

        # Expect semicolon
        token = self.current_token()
        if not token or token["type"] != "SEMI-COLON_DELI":
            raise SyntaxError("❌ Missing ';' after initialization.", line_number)
        self.next_token()

        # === <Condition> ::= <Identifier> <Rel_Op> <Expression> | <Expression> <Logic_Op> <Expression> ===
        condition_expr = []
        token = self.current_token()

        if token["type"] not in ["IDENTIFIER", "INTEGER", "FLOAT"]:
            raise SyntaxError("❌ Expected a condition expression after initialization.", line_number)

        condition_expr.append(token["value"])
        self.next_token()
        token = self.current_token()

        if token["type"] not in ["EQUAL-REL_OP", "NOT-REL_OP", "GREAT-EQL-REL_OP", "LESS-EQL-REL_OP", "LESS-REL_OP", "GREAT-REL_OP"]:
            raise SyntaxError("❌ Expected a value after the relational operator.", line_number)
        condition_expr.append(token["value"])
        self.next_token()
        token = self.current_token()

        # Expect another identifier or number after the relational operator
        if token["type"] not in ["IDENTIFIER", "INTEGER", "FLOAT"]:
            raise SyntaxError("❌ Expected a value after the relational operator.", line_number)
        condition_expr.append(token["value"])
        self.next_token()
        token = self.current_token()

        if not token or token["type"] != "SEMI-COLON_DELI":
            raise SyntaxError("❌ Missing ';' after condition.", line_number)
        self.next_token()  # Move past ';'

        # === <Update> ::= <Identifier> <Increment> | <Identifier> <Assign_Op> <Expression> | OPTIONAL: <Update> "," <Update> ===

        token = self.current_token()
        # Expect an identifier
        if token["type"] != "IDENTIFIER":
            raise SyntaxError("❌ Expected an identifier at the beginning of the update expression.", line_number)
        
        self.next_token()
        token = self.current_token()
        
        # Check if it's an increment/decrement (i++ or i--)
        if token and token["type"] in ["INCRE_OP", "DECRE_OP"]:
            self.next_token()
            token = self.current_token()       

        # Otherwise, expect an assignment operator
        elif token and token["type"] in ["ASSIGN_OP", "PLUS-ASSIGN_OP", "MINUS-ASSIGN_OP", "MULTI-ASSIGN_OP", "DIVIDE-ASSIGN_OP", "MOD-ASSIGN_OP"]:
            self.next_token()
            token = self.current_token()

            # Ensure a valid expression follows (Identifier or Number)
            if not token or token["type"] not in ["IDENTIFIER", "INTEGER", "FLOAT", "DOUBLE"]:
                raise SyntaxError("❌ Expected a valid expression after assignment operator in update section.", line_number)           

            self.next_token()
            token = self.current_token()
            
        if not token or token["type"] != "CLOSE-PAREN_DELI":
            raise SyntaxError("❌ Missing ')' after the update statement.", line_number)
        self.next_token()

        # === <Body> ::= "{" <Statements> "}" ===
        token = self.current_token()
        if not token or token["type"] != "OPEN-CURL-BRAC_DELI":
            self.skip_to_next_for_loop()
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
                self.skip_to_next_for_loop()
            
                