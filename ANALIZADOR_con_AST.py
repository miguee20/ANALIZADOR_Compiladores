import re
import json
import os

# Definir patrones léxicos con operadores relacionales y lógicos separados
token_patron = {
    "KEYWORD": r"\b(if|else|while|for|return|int|float|void|print)\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "IDENTIFIER": r"\b(?!if|else|while|for|return|int|float|void|print\b)[a-zA-Z_][a-zA-Z0-9_]*\b",
    "OP_RELATIONAL": r"(<=|>=|==|!=|<|>)",
    "OP_LOGICAL": r"(&&|\|\|)",
    "ASSIGNMENT": r"=",
    "OP_ARITHMETIC": r"(\+\+|--|[+\-*/%])",
    "DELIMITER": r"[(),;{}]",
    "COMMENT": r"//.*",
    "WHITESPACE": r"\s+",
    "UNKNOWN": r"."
}

def identificar(texto):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None:
                if token == "WHITESPACE":
                    continue
                elif token == "UNKNOWN":
                    print(f"Error léxico: Carácter desconocido '{valor}'")
                else:
                    tokens_encontrados.append((token, valor))
    
    return tokens_encontrados

# Definición de nodos AST
class NodoAST:
    def to_dict(self):
        def convertir_a_dict(valor):
            if isinstance(valor, NodoAST):
                return valor.to_dict()
            elif isinstance(valor, list):
                return [convertir_a_dict(v) for v in valor]
            else:
                return valor
        return {key: convertir_a_dict(value) for key, value in self.__dict__.items()}

class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        self.tipo = "Funcion"
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = "Parametro"
        self.tipo_dato = tipo
        self.nombre = nombre

class NodoAsignacion(NodoAST):
    def __init__(self, tipo, nombre, expresion):
        self.tipo = "Asignacion"
        self.tipo_dato = tipo
        self.nombre = nombre
        self.expresion = expresion

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.tipo = "Operacion"
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.tipo = "Retorno"
        self.expresion = expresion

class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.tipo = "Identificador"
        self.nombre = nombre

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.tipo = "Numero"
        self.valor = int(valor) if valor.isdigit() else float(valor)

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
        funciones = []
        while self.obtener_token_actual():
            funciones.append(self.funcion())
        return funciones

    def funcion(self):
        self.coincidir("KEYWORD")
        nombre = self.coincidir("IDENTIFIER")[1]
        self.coincidir("DELIMITER")
        parametros = self.parametros()
        self.coincidir("DELIMITER")
        self.coincidir("DELIMITER")
        cuerpo = self.cuerpo()
        self.coincidir("DELIMITER")
        return NodoFuncion(nombre, parametros, cuerpo)

    def parametros(self):
        parametros = []
        while self.obtener_token_actual() and self.obtener_token_actual()[0] == "KEYWORD":
            tipo = self.coincidir("KEYWORD")[1]
            nombre = self.coincidir("IDENTIFIER")[1]
            parametros.append(NodoParametro(tipo, nombre))
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == ",":
                self.coincidir("DELIMITER")
        return parametros

    def cuerpo(self):
        instrucciones = []
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != "}":
            if self.obtener_token_actual()[0] == "KEYWORD" and self.obtener_token_actual()[1] == "return":
                self.coincidir("KEYWORD")
                expr = self.expresion()
                self.coincidir("DELIMITER")
                instrucciones.append(NodoRetorno(expr))
            else:
                instrucciones.append(self.asignacion())
        return instrucciones

    def asignacion(self):
        tipo = self.coincidir("KEYWORD")[1]
        nombre = self.coincidir("IDENTIFIER")[1]
        self.coincidir("ASSIGNMENT")
        expr = self.expresion()
        self.coincidir("DELIMITER")
        return NodoAsignacion(tipo, nombre, expr)

    def expresion(self):
        izquierda = self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] == "OP_ARITHMETIC":
            operador = self.coincidir("OP_ARITHMETIC")[1]
            derecha = self.termino()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        token_actual = self.obtener_token_actual()
        if token_actual[0] == "NUMBER":
            return NodoNumero(self.coincidir("NUMBER")[1])
        elif token_actual[0] == "IDENTIFIER":
            return NodoIdentificador(self.coincidir("IDENTIFIER")[1])
        raise SyntaxError(f"Expresión inválida: {token_actual}")

# Ejecutar análisis
codigo_fuente = "int main() { int a = 3; int b = 5; return a + b; }"
tokens = identificar(codigo_fuente)
print("Tokens encontrados:")
for t in tokens:
    print(f"  {t}")
parser = Parser(tokens)
ast = parser.parsear()

# Guardar AST en JSON
archivo_salida = os.path.join(os.getcwd(), "ast.json")
with open(archivo_salida, "w") as f:
    json.dump([nodo.to_dict() for nodo in ast], f, indent=4)
print(f"\nAST guardado en: {archivo_salida}")
