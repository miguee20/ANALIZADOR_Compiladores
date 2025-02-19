import re

# Definir patrones léxicos con operadores relacionales y lógicos separados
token_patron = {
    "KEYWORD": r"\b(if|else|while|for|return|int|float|void|print)\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "IDENTIFIER": r"\b(?!if|else|while|for|return|int|float|void|print\b)[a-zA-Z_][a-zA-Z0-9_]*\b",
    "OP_RELATIONAL": r"(<=|>=|==|!=|<|>)",  # Todos los operadores relacionales
    "OP_LOGICAL": r"(&&|\|\|)",             # Todos los operadores lógicos
    "ASSIGNMENT": r"=",                     # Operador de asignación
    "OP_ARITHMETIC": r"(\+\+|--|[+\-*/%])", # Incluir operadores dobles (++, --)
    "DELIMITER": r"[(),;{}]",               # Delimitadores comunes
    "COMMENT": r"//.*",
    "WHITESPACE": r"\s+",                   # Espacios en blanco
    "UNKNOWN": r"."                         # Para cualquier carácter desconocido
}


def identificar(texto):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None:
                if token == "WHITESPACE":  # Ignorar espacios en blanco
                    continue
                elif token == "UNKNOWN":
                    print(f"Error léxico: Carácter desconocido '{valor}'")
                else:
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

# --------------------------------------------------------------------------
class NodoAST:
    #clase para nodos 
    pass

class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):    
        self.nombre = nombre
        self.parameteos = parametros
        self.cuerpo = cuerpo

class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):  
        self.tipo = tipo
        self.nombre = nombre    

class NodoAsignacion(NodoAST):
    # nodo de asignacion de variabels
    def __init__(self, nombre, expresion):         
        self.nombre = nombre
        self.expresion= expresion

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion         


class NodoIdentificador(NodoAST):
    def __init__(self,nombre):
        self.nombre = nombre

class NodoNumero(NodoAST):
    def __init__(self, valor):  
        self.valor = valor            


# ------------------------------------------------------------------------------------


# Código fuente de prueba que analiza todo problema lexico posible 
codigo_fuente = """
int suma(int a, int b) { 
    return a + b; 
}

float division(float x, float y) {
    if (y != 0.0) {
        return x / y;
    } else {
        return -1.0;
    }
}

// Variables y operadores
int contador = 10;
contador++;  // Incremento
contador--;  // Decremento

if (contador >= 5 && contador < 20 || contador == 15) {
    print(contador);
}

// Bucle for
for (int i = 0; i < 10; i++) {
    print(i);
}

// Bucle while
while (contador > 0) {
    contador -= 2;
}

// Prueba de caracteres desconocidos
@ # $ % & ^

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
