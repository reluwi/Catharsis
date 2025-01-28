class SyntaxError(Exception):
    """Custom exception for syntax errors."""
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def next_token(self):
        self.current_token_index += 1
        return self.current_token()

    def parse_declaration(self):
        """
        Parses a declaration statement (e.g., int x = 5;).
        """
        token = self.current_token()
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
                if token and token["type"] == "ASSIGN_OP":
                    self.next_token()
                    token = self.current_token()
                    if token and token["type"] in ["INT_KEY", "FLOAT_KEY", "DOUBLE_KEY", "CHAR_KEY", "STRING_KEY", "BOOL_KEY"]:
                        value = token["value"]
                        self.next_token()
                        token = self.current_token()
                        if token and token["type"] == "SEMI-COLON_DELI":
                            print(f"Valid variable declaration: {declaration_type} {identifier} = {value};")
                            self.next_token()
                            return
                        else:
                            raise SyntaxError("Missing semicolon at the end of the declaration.")
                elif token and token["type"] == "SEMI-COLON_DELI":
                    print(f"Valid variable declaration: {declaration_type} {identifier};")
                    self.next_token()
                    return
                else:
                    raise SyntaxError("Invalid variable declaration syntax.")
            else:
                raise SyntaxError("Expected an identifier after the type.")
        else:
            raise SyntaxError("Expected a type keyword at the beginning of the declaration.")