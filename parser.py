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
        self.variables = set()  # ✅ Tracks declared variables

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
                self.next_token()
                return  

            # Stop if a new valid declaration keyword is found (int, float, etc.)
            if token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "TRUE_BOOL", "FALSE_BOOL", "STRING_KEY", 
                                "FOR_KEY", "IF_KEY", "ELSE_KEY", "RETURN_KEY", "PRINTF_KEY", "CLOSE-CURL-BRAC_DELI", "RETURN_KEY", "SINGLE_LINE_COMMENT"]: 
                return

            self.next_token()  # Skip any other unrecognized tokens

    def skip_to_next_for_loop(self):
        """
        Skips tokens until the end of a `for` loop.
        - First, skips until `)` (closing parenthesis of loop header).
        - Then, skips until `}` (closing brace of loop body).
        """
        while self.current_token():
            token = self.current_token()
            
            # Stop at closing parenthesis `)` → End of for-loop header
            if token["type"] == "CLOSE-PAREN_DELI":
                self.next_token()
                break  # ✅ Exit loop after skipping header
            
            self.next_token()  # Skip unrecognized tokens in header

        while self.current_token():
            token = self.current_token()

            # Stop at closing brace `}` → End of loop body
            if token["type"] == "CLOSE-CURL-BRAC_DELI":
                self.next_token()
                return  # ✅ Exit function once loop body is skipped

            self.next_token()  # Skip unrecognized tokens in body

    def skip_to_next_statement(self):
        """
        Skips tokens until a semicolon (`;`), closing brace (`}`), or a valid new statement is found.
        This prevents infinite loops when encountering syntax errors.
        """
        while self.current_token():
            token = self.current_token()

            # Stop at a semicolon - likely end of a statement
            if token["type"] == "SEMI-COLON_DELI":
                self.next_token()
                return

            # Stop if a closing `}` is found (end of a block)
            if token["type"] == "CLOSE-CURL-BRAC_DELI":
                self.next_token()  # Move past `}`
                return  

            # Stop if a new valid declaration keyword or block end is found
            if token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "TRUE_BOOL", "FALSE_BOOL", "STRING_KEY", 
                                "FOR_KEY", "IF_KEY", "ELSE_KEY", "RETURN_KEY", "PRINTF_KEY", "SINGLE_LINE_COMMENT"]: 
                return

            self.next_token()  # Skip unrecognized tokens

    def parse_declaration(self):
        """
        Parses a declaration statement (e.g., int x = 5;).
        """       
        token = self.current_token()
        if not token:
            return []  # Return empty error list if no token

        line_number = token["line_number"]
        errors = []  # Store errors locally

        # Step 1: Check for a valid type keyword (int, float, etc.)
        if token["type"] not in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "BOOL_KEY", "STRING_KEY"]:
            errors.append(f"❌ Syntax Error on line {line_number}: Expected a type keyword at the beginning of the declaration.")
            self.skip_to_next_declaration()  # Move past faulty declaration
            return errors
        
        self.next_token()

        variables = []

        while True:
            # Step 2: Check for a valid identifier
            token = self.current_token()
            if token and token["type"] != "IDENTIFIER":
                errors.append(f"❌ Syntax Error on line {line_number}: Expected an identifier after the type.")
                self.skip_to_next_declaration()
                return errors 
            
            identifier = token["value"]
            self.variables.add(identifier)  # ✅ Store variable in symbol table
            self.next_token()

            # Step 3: Check for an optional assignment or a semicolon
            token = self.current_token()
            if token and token["type"] in ["ASSIGN_OP", "PLUS-ASSIGN_OP", "MINUS-ASSIGN_OP", "MULTI-ASSIGN_OP", "DIVIDE-ASSIGN_OP", "MOD-ASSIGN_OP"]:  # Handle assignment
                self.next_token()
                token = self.current_token()

                # Ensure a valid value follows the assignment
                if not token or token["type"] not in ["INTEGER", "FLOAT", "DOUBLE", "CHAR_KEY", "STRING_KEY", "TRUE_BOOL", "FALSE_BOOL", "IDENTIFIER"]:
                    errors.append(f"❌ Syntax Error on line {line_number}: Expected a valid value after assignment.")
                    self.skip_to_next_declaration()
                    return errors
                
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
                errors.append(f"❌ Syntax Error on line {line_number}: Missing ';' at the end of the declaration.")
                self.skip_to_next_declaration()
                return errors
        
        self.next_token()  # Move to the next token after semicolon

        return errors  # Return collected errors

    def parse_for_loop(self):
        """
        Parses a 'for' loop statement following:
        <For_Loop> ::= "for" "("<Init> ";" <Condition> ";" <Update> ")" <Body>
        """
        errors = []  # Store errors locally
        token = self.current_token()
        
        if not token:
            return []  # ✅ Return an empty list if no token

        line_number = token["line_number"]

        if not token or token["type"] != "FOR_KEY":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected 'for' keyword.")
            return errors 

        self.next_token()  # Move past 'for'
        
        # Expect '('
        token = self.current_token()
        if not token or token["type"] != "OPEN-PAREN_DELI":
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Expected '(' after 'for'.")
            return errors 
        
        self.next_token()  # Move past '('

        # === <Init> ::= ( <Dat_Type> <Identifier> "=" <Expression> ) | ( <Identifier> "=" <Expression> ) ===
        token = self.current_token()
        if token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "BOOL_KEY", "STRING_KEY"]:
             # Handle type keyword (e.g., "int i = 0;")
            self.next_token()

            token = self.current_token()
            if token["type"] == "IDENTIFIER":
                self.next_token()
                token = self.current_token()

                # Expect assignment operator and value
                if token["type"] == "ASSIGN_OP":
                    
                    self.next_token()
                    token = self.current_token()

                    if not token or token["type"] not in ["INTEGER", "FLOAT", "DOUBLE", "CHAR_KEY", "STRING_KEY", "IDENTIFIER"]:
                        self.skip_to_next_for_loop()
                        errors.append(f"❌ Syntax Error on line {line_number}: Expected a value after '=' in initialization.")
                        return errors  
                    self.next_token()
            else:
                self.skip_to_next_for_loop()
                errors.append(f"❌ Syntax Error on line {line_number}: Expected an Identifier after the type.")
                return errors  
        elif token["type"] == "IDENTIFIER":
            # Handle without type (e.g., "i = 0;")
            self.next_token()
            token = self.current_token()
        else:
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Invalid initialization in for loop.")
            return errors  

        # Expect semicolon
        token = self.current_token()
        if not token or token["type"] != "SEMI-COLON_DELI":
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Missing ';' after initialization.")
            return errors  
        self.next_token()

        # === <Condition> ::= <Identifier> <Rel_Op> <Expression> | <Expression> <Logic_Op> <Expression> ===
        condition_expr = []
        token = self.current_token()

        if token["type"] not in ["IDENTIFIER", "INTEGER", "FLOAT"]:
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Expected a condition expression after initialization.")
            return errors  

        condition_expr.append(token["value"])
        self.next_token()
        token = self.current_token()

        if token["type"] not in ["EQUAL-REL_OP", "NOT-REL_OP", "GREAT-EQL-REL_OP", "LESS-EQL-REL_OP", "LESS-REL_OP", "GREAT-REL_OP"]:
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Expected a relational operator.")
            return errors 
        condition_expr.append(token["value"])
        self.next_token()
        token = self.current_token()

        # Expect another identifier or number after the relational operator
        if token["type"] not in ["IDENTIFIER", "INTEGER", "FLOAT"]:
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Expected a value after the relational operator.")
            return errors 
        condition_expr.append(token["value"])
        self.next_token()
        token = self.current_token()

        if not token or token["type"] != "SEMI-COLON_DELI":
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Missing ';' after condition.")
            return errors  
        self.next_token()  # Move past ';'

        # === <Update> ::= <Identifier> <Increment> | <Identifier> <Assign_Op> <Expression> | OPTIONAL: <Update> "," <Update> ===

        token = self.current_token()
        # Expect an identifier
        if token["type"] != "IDENTIFIER":
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Expected an identifier at the beginning of the update expression.")
            return errors 
        
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
                self.skip_to_next_for_loop()
                errors.append(f"❌ Syntax Error on line {line_number}: Expected a valid expression after assignment operator in update section.")
                return errors            

            self.next_token()
            token = self.current_token()
            
        if not token or token["type"] != "CLOSE-PAREN_DELI":
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Missing ')' after the update statement.")
            return errors
        self.next_token()

        # === <Body> ::= "{" <Statements> "}" ===
        token = self.current_token()
        if not token or token["type"] != "OPEN-CURL-BRAC_DELI":
            self.skip_to_next_for_loop()
            errors.append(f"❌ Syntax Error on line {line_number}: Expected '{{' after 'for' loop header.")
            return errors

        self.next_token()  # Move past '{'

        # **Parse statements inside loop body**
        while self.current_token():
            token = self.current_token()
            
            # Stop when we reach '}'
            if token["type"] == "CLOSE-CURL-BRAC_DELI":
                self.next_token()  # Move past '}'
                return
            
             # **Parse statements inside loop body**
            try:
                errors.extend(self.parse_statement())  # ✅ Process statements inside `{}` correctly
            except SyntaxError as e:
                errors.append(str(e))
                self.skip_to_next_for_loop()
            
        return errors  # Return collected errors        
    
    def parse_statement(self):
        """
        General statement parser that delegates to specific parsing functions.
        Handles declarations, loops, function calls (e.g., printf, return).
        """
        token = self.current_token()
        errors = []
        
        if not token:
            return []
   
        line_number = token["line_number"]

        # ✅ Check if token is a previously declared variable
        if token["type"] == "IDENTIFIER":
            next_token = self.peek_next_token()

            # ✅ Handle decrement operation (a--)
            if next_token and next_token["type"] == "DECRE_OP":
                result = self.parse_decre_op()
                if result:
                    errors.extend(result)
                return errors  # ✅ No unexpected statement error

            elif next_token and next_token["type"] != "DECRE_OP":
                errors.append(f"❌ Syntax Error on line {line_number}: Unrecognized function or statement '{token['value']}'.")
                self.skip_to_next_for_loop() # ✅ Skip to avoid redundant errors
                return errors

            self.next_token()  # ✅ Move past variable (it's valid)
            return []
        
         # ✅ Handle decrement operation (standalone "--")
        if token["type"] == "DECRE_OP":
            result = self.parse_decre_op()
            if result:
                errors.extend(result)
            return errors

         # ✅ Skip single-line comments
        if token["type"] == "SINGLE_LINE_COMMENT":
            self.next_token()  # Move to the next statement
            return []  # No errors for comments

        if token["type"] == "INT_KEY" and self.peek_next_token() and self.peek_next_token()["type"] == "MAIN_KEY":
            result = self.parse_main_function()
            if result:
                errors.extend(result)

        elif token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "TRUE_BOOL", "FALSE_BOOL", "STRING_KEY"]:
            result = self.parse_declaration()
            if result:
                errors.extend(result)
        elif token["type"] == "FOR_KEY":
            result = self.parse_for_loop()
            if result:
                errors.extend(result)
        elif token["type"] in ["PRINTF_KEY", "RETURN_KEY", "GC_KEY"]:
            result = self.parse_function_call()
            if result:
                errors.extend(result)
        elif token["type"] == "IF_KEY":
            result = self.parse_if_else()
            if result:
                errors.extend(result)

        else:
            errors.append(f"❌ Syntax Error on line {line_number}: Unexpected statement.")
            self.skip_to_next_statement()

        return errors
    
    def parse_function_call(self):
        """
        Parses function calls like printf("text"); or return 0;
        """
        errors = []
        token = self.current_token()

        if not token:
            return []

        line_number = token["line_number"]

        if token["type"] in ["PRINTF_KEY", "GC_KEY"]:
            function_name = token["value"]  # Store function name
            self.next_token()
            token = self.current_token()

            if function_name == "printf":
                if not token or token["type"] != "OPEN-PAREN_DELI":
                    errors.append(f"❌ Syntax Error on line {line_number}: Expected '(' after 'printf'.")
                    #self.next_token()
                    self.skip_to_next_statement()
                    return errors
                self.next_token() # Move past '('

                # Expect string inside printf
                token = self.current_token()
                if not token or token["type"] != "STRING_KEY":
                    errors.append(f"❌ Syntax Error on line {line_number}: Expected a string inside printf.")
                    #self.next_token()
                    self.skip_to_next_statement()
                    return errors
                self.next_token()

                # ✅ Allow alternating , IDENTIFIER or STRING
                token = self.current_token()
                while token and token["type"] == "COMMA_DELI":
                    self.next_token()  # Move past `,`
                    token = self.current_token()
            
                    if not token or token["type"] not in ["IDENTIFIER", "STRING_KEY", "CHAR_KEY"]:
                        errors.append(f"❌ Syntax Error on line {line_number}: Expected an identifier or string after `,`.")
                        self.next_token()
                        self.skip_to_next_statement()
                        return errors

                    self.next_token()  # Move past identifier or string
                    token = self.current_token()
            
                # ✅ Expect `)` closing parenthesis
                if not token or token["type"] != "CLOSE-PAREN_DELI":
                    errors.append(f"❌ Syntax Error on line {line_number}: Expected ')' after printf arguments.")
                    #self.next_token()
                    self.skip_to_next_statement()
                    return errors
                self.next_token() # Move past ')'

                # ✅ Expect `;` after printf
                token = self.current_token()
                if not token or token["type"] != "SEMI-COLON_DELI":
                    errors.append(f"❌ Syntax Error on line {line_number}: Missing ';' after printf statement.")
                    #self.next_token()
                    self.skip_to_next_statement()
                    return errors
                self.next_token()

                return errors

            elif function_name == "gc":
                if not token or token["type"] != "OPEN-PAREN_DELI":
                    errors.append(f"❌ Syntax Error on line {line_number}: Expected '(' after 'gc'.")
                    #self.next_token()
                    self.skip_to_next_statement()
                    return errors
                self.next_token() # Move past '('

                # ✅ Expect `)` closing parenthesis
                token = self.current_token()
                if not token or token["type"] != "CLOSE-PAREN_DELI":
                    errors.append(f"❌ Syntax Error on line {line_number}: Expected ')' after '(' for gc function.")
                    #self.next_token()
                    self.skip_to_next_statement()
                    return errors
                self.next_token() # Move past ')'

                # ✅ Expect `{` after `gc()`
                token = self.current_token()
                if not token or token["type"] != "OPEN-CURL-BRAC_DELI":
                    errors.append(f"❌ Syntax Error on line {line_number}: Expected '{{' to start 'gc' function body.")
                    self.skip_to_next_statement()
                    return errors
                self.next_token()

                # ✅ Parse statements inside `gc` function body
                while self.current_token():
                    token = self.current_token()

                    # ✅ Stop when reaching `}`
                    if token["type"] == "CLOSE-CURL-BRAC_DELI":
                        self.next_token()
                        return errors

                    try:
                        # Parse declarations, loops, or other valid statements inside `gc`
                        errors.extend(self.parse_statement())
                    except SyntaxError as e:
                        errors.append(str(e))
                        self.skip_to_next_statement()
                
                 # ✅ Ensure function properly closes
                errors.append(f"❌ Syntax Error on line {line_number}: Missing closing Bracket for 'gc' function.")
                return errors

        elif token["type"] == "RETURN_KEY":
            self.next_token()
            token = self.current_token()

            if not token or token["type"] not in ["INTEGER", "FLOAT", "IDENTIFIER"]:
                errors.append(f"❌ Syntax Error on line {line_number}: Expected a return value.")
                self.next_token()
                self.skip_to_next_statement()
                return errors

            self.next_token()  # Move past return value
            token = self.current_token()

            if not token or token["type"] != "SEMI-COLON_DELI":
                errors.append(f"❌ Syntax Error on line {line_number}: Missing ';' after return statement.")
                self.next_token()
                self.skip_to_next_statement()
                return errors

            self.next_token()
            return errors

        else:
            # If function name is not recognized
            errors.append(f"❌ Syntax Error on line {line_number}: Unrecognized function or statement '{token['value']}'.")
            self.skip_to_next_statement()
            return errors
    
    def parse_if_else(self):
        """
        Parses if-else statements.
        <If_Else> ::= "if" "(" <Condition> ")" <Body> 
                    | "else if" "(" <Condition> ")" <Body>
                    | "else" <Body>
        """
        errors = []
        token = self.current_token()
        line_number = token["line_number"]

        if token["type"] != "IF_KEY":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected 'if' keyword.")
            self.skip_to_next_statement()
            return errors

        self.next_token()  # Move past 'if'

        # Expect '('
        token = self.current_token()
        if not token or token["type"] != "OPEN-PAREN_DELI":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected '(' after 'if'.")
            self.skip_to_next_statement()
            return errors

        self.next_token()  # Move past '('

        # Expect a condition (Identifier or value)
        token = self.current_token()
        if not token or token["type"] not in ["IDENTIFIER", "INTEGER", "FLOAT", "TRUE_BOOL", "FALSE_BOOL", "CHAR_KEY", "STRING_KEY"]:
            errors.append(f"❌ Syntax Error on line {line_number}: Expected a condition expression.")
            self.skip_to_next_statement()
            return errors       

        self.next_token()  # Move past condition

        # Expect a relational or logical operator
        token = self.current_token()
        if not token or token["type"] not in ["EQUAL-REL_OP", "NOT-REL_OP", "GREAT-EQL-REL_OP", 
                                            "LESS-EQL-REL_OP", "LESS-REL_OP", "GREAT-REL_OP", 
                                            "AND-LOGIC_OP", "OR-LOGIC_OP"]:
            errors.append(f"❌ Syntax Error on line {line_number}: Expected a valid comparison or logical operator.")
            self.skip_to_next_statement()
            return errors  

        self.next_token()  # Move past operator
        token = self.current_token()
        # Expect another identifier, number, or boolean after operator
        if not token or token["type"] not in ["IDENTIFIER", "INTEGER", "FLOAT", "TRUE_BOOL", "FALSE_BOOL", "STRING_KEY", "CHAR_KEY"]:
            errors.append(f"❌ Syntax Error on line {line_number}: Expected a value after the operator.")
            self.skip_to_next_statement()
            return errors

        self.next_token()  # Move past value
        token = self.current_token()
        # Expect ')'
        if not token or token["type"] != "CLOSE-PAREN_DELI":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected ')' after condition.")
            self.skip_to_next_statement()
            return errors

        self.next_token()  # Move past ')'

        # Expect '{' for body
        token = self.current_token()
        if not token or token["type"] != "OPEN-CURL-BRAC_DELI":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected OPEN_BRACKET after 'if' or 'else if'.")
            self.skip_to_next_statement()
            return errors

        self.next_token()  # Move past '{'

        # Parse statements inside `if` body
        while self.current_token():
            token = self.current_token()

            if token["type"] == "CLOSE-CURL-BRAC_DELI":  # End of if-block
                self.next_token()
                break

            try:
                errors.extend(self.parse_statement())
            except SyntaxError as e:
                errors.append(str(e))
                self.skip_to_next_statement()

        # ✅ **Check for `else` statement**
        token = self.current_token()
        if token and token["type"] == "ELSE_KEY":
            self.next_token()  # Move past 'else'

            # Expect '{'
            token = self.current_token()
            if not token or token["type"] != "OPEN-CURL-BRAC_DELI":
                errors.append(f"❌ Syntax Error on line {line_number}: Expected OPEN BRACKET to start else-body.")
                self.skip_to_next_statement()
                return errors
            
            self.next_token()  # Move past '{'

            # Parse statements inside `else` body
            while self.current_token():
                token = self.current_token()

                if token["type"] == "CLOSE-CURL-BRAC_DELI":  # End of else-block
                    self.next_token()
                    return errors
                
                try:
                    errors.extend(self.parse_statement())
                except SyntaxError as e:
                    errors.append(str(e))
                    self.skip_to_next_statement()

        return errors  # Return all collected errors
    
    def parse_main_function(self):
        """
        Parses the 'int main()' function structure.
        """
        errors = []
        token = self.current_token()
        line_number = token["line_number"]

        # Expect 'int'
        if not token or token["type"] != "INT_KEY":
            return []

        self.next_token()
        token = self.current_token()

        # Expect 'main'
        if not token or token["type"] != "MAIN_KEY":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected 'main' after 'int'.")
            self.skip_to_next_statement()
            return errors

        self.next_token()
        token = self.current_token()

        # Expect '('
        if not token or token["type"] != "OPEN-PAREN_DELI":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected '(' after 'main'.")
            self.skip_to_next_statement()
            return errors

        self.next_token()
        token = self.current_token()

        # Expect ')'
        if not token or token["type"] != "CLOSE-PAREN_DELI":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected ')' after 'main('.")
            self.skip_to_next_statement()
            return errors

        self.next_token()
        token = self.current_token()

        # Expect '{'
        if not token or token["type"] != "OPEN-CURL-BRAC_DELI":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected '{{' to start main function body.")
            self.skip_to_next_statement()
            return errors

        self.next_token()

        # **Parse statements inside main function**
        while self.current_token():
            token = self.current_token()
            
            if token["type"] == "CLOSE-CURL-BRAC_DELI":
                self.next_token()  # Move past '}'
                return errors  # Exit after closing '}'

            try:
                errors.extend(self.parse_statement())
            except SyntaxError as e:
                errors.append(str(e))
                self.skip_to_next_statement()
        
        return errors
    
    def peek_next_token(self):
        """ Returns the next token without advancing the current index. """
        if self.current_token_index + 1 < len(self.tokens):
            return self.tokens[self.current_token_index + 1]
        return None  # No more tokens
    
    def parse_decre_op(self):
        """
        Parses decrement operations like 'a--;'
        """
        errors = []
        token = self.current_token()
        line_number = token["line_number"]

        if not token or token["type"] != "IDENTIFIER":
            return []  # ✅ No decrement operation

        self.next_token()  # ✅ Move past the variable
        token = self.current_token()

        # Expect `--`
        if not token or token["type"] != "DECRE_OP":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected '--' after identifier.")
            self.skip_to_next_statement()
            return errors
        
        self.next_token()  # ✅ Move past '--'
        token = self.current_token()

        # Expect `;`
        if not token or token["type"] != "SEMI-COLON_DELI":
            errors.append(f"❌ Syntax Error on line {line_number}: Expected ';' after '--'.")
            self.skip_to_next_statement()
            return errors

        self.next_token()  # ✅ Move past `;`
        return errors
