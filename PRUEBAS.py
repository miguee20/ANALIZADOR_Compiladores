import re

# Definir patrones léxicos con operadores relacionales y lógicos separados
token_patron = {
    "KEYWORD": r"\b(if|else|while|for|return|int|float|void|print)\b",
    "IDENTIFIER": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "OP_RELATIONAL": r"[<>]=?|==|!=",
    "OP_LOGICAL": r"&&|\|\|",
    "OP_ARITHMETIC": r"[+\-*/=]",
    "DELIMITER": r"[(),;{}]",
    "WHITESPACE": r"\s+",
}

def identificar(texto):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token, valor))
    return tokens_encontrados

# Analizador sintáctico
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        raise SyntaxError(f'Error Sintáctico, se esperaba {tipo_esperado}, pero se encontró {token_actual}')

    def parsear(self):
        self.funcion()

    def funcion(self):
        self.coincidir("KEYWORD")
        self.coincidir("IDENTIFIER")
        self.coincidir("DELIMITER")
        self.parametros()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        self.cuerpo()
        self.coincidir("DELIMITER")

    def parametros(self):
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "KEYWORD":
            self.coincidir("KEYWORD")
            self.coincidir("IDENTIFIER")
            while self.obtener_token_actual() and self.obtener_token_actual()[1] == ",":
                self.coincidir("DELIMITER")
                self.coincidir("KEYWORD")
                self.coincidir("IDENTIFIER")

    def cuerpo(self):
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
            if self.obtener_token_actual()[0] == "KEYWORD" and self.obtener_token_actual()[1] == "return":
                self.coincidir("KEYWORD")
                self.expresion()
                self.coincidir("DELIMITER")
            elif self.obtener_token_actual()[0] == "KEYWORD" and self.obtener_token_actual()[1] == "if":
                self.condicional()
            elif self.obtener_token_actual()[0] == "KEYWORD" and self.obtener_token_actual()[1] == "while":
                self.bucle()
            elif self.obtener_token_actual()[0] == "KEYWORD" and self.obtener_token_actual()[1] == "for":
                self.bucle_for()
            elif self.obtener_token_actual()[0] == "KEYWORD" and self.obtener_token_actual()[1] == "print":
                self.imprimir()
            else:
                self.asignacion()

    def asignacion(self):
        self.coincidir("IDENTIFIER")
        self.coincidir("OP_ARITHMETIC")
        self.expresion()
        self.coincidir("DELIMITER")

    def expresion(self):
        self.relacional()

    def relacional(self):
        self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] in ["OP_RELATIONAL", "OP_LOGICAL"]:
            self.coincidir(self.obtener_token_actual()[0])
            self.termino()

    def termino(self):
        self.factor()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] == "OP_ARITHMETIC":
            self.coincidir("OP_ARITHMETIC")
            self.factor()

    def factor(self):
        token_actual = self.obtener_token_actual()
        if token_actual[0] in ["NUMBER", "IDENTIFIER"]:
            self.coincidir(token_actual[0])
        elif token_actual[1] == "(":
            self.coincidir("DELIMITER")
            self.expresion()
            self.coincidir("DELIMITER")
        else:
            raise SyntaxError(f"Error Sintáctico en la expresión: {token_actual}")

    def condicional(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        self.expresion()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        self.cuerpo()
        self.coincidir("DELIMITER")
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == "else":
            self.coincidir("KEYWORD")
            self.coincidir("DELIMITER")
            self.cuerpo()
            self.coincidir("DELIMITER")

    def bucle(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        self.expresion()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        self.cuerpo()
        self.coincidir("DELIMITER")

    def bucle_for(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        self.asignacion()
        self.expresion()
        self.coincidir("DELIMITER")
        self.asignacion()
        self.coincidir("DELIMITER")
        self.cuerpo()
        self.coincidir("DELIMITER")

    def imprimir(self):
        self.coincidir("KEYWORD")
        self.coincidir("DELIMITER")
        self.expresion()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")

# Código fuente de prueba
codigo_fuente = """
int comparar(int a, int b) {
    if (a >= b && b != 0) {
        print(a);
    } else {
        print(b);
    }
}

for(i=1; i<5; i++)
    print(i);
"""

texto_bienvenida = "INICIANDO ANALISIS LEXICO/SINTACTICO"
print("-" * (len(texto_bienvenida) + 4))  
print(f"| {texto_bienvenida} |")
print("-" * (len(texto_bienvenida) + 4))

# Análisis léxico
tokens = identificar(codigo_fuente)
print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f"{tipo}: {valor}")

# Análisis sintáctico
try:
    parser = Parser(tokens)
    parser.parsear()
    texto_exito ="ANALISIS COMPLETO CON EXITO"
    print("-" * (len(texto_exito) + 4))  
    print(f"| {texto_exito} |")
    print("-" * (len(texto_exito) + 4))
except SyntaxError as e:
    print(e)
