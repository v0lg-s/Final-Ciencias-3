import re  # Importamos la librería de expresiones regulares para facilitar la búsqueda de patrones en el código fuente

# Palabras clave
keywords = {'if', 'else', 'while', 'return', 'for', 'int', 'float', 'bool', 'true', 'false'}

# Definición de tokens con expresiones regulares
token_definitions = [
    ('STRING', r'"([^"\\]|\\.)*"'),  # Cadenas entre comillas dobles
    ('CHAR', r"'([^'\\]|\\.)'"),  # Caracteres entre comillas simples (y permitiendo escape)
    ('EQUALS', r'=='),  # Comparación de igualdad
    ('NOTEQUAL', r'!='),  # Comparación de desigualdad
    ('LESSEQUAL', r'<='),  # Comparación menor o igual
    ('GREATEREQUAL', r'>='),  # Comparación mayor o igual
    ('LESS', r'<'),  # Comparación menor
    ('GREATER', r'>'),  # Comparación mayor
    ('COMMENT', r'//.*'),  # Comentarios de una sola línea
    ('NUMBER', r'\d+\.\d+|\d+'),  # Números enteros y flotantes
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),  # Identificadores (variables, funciones, etc.)
    ('OPERATOR', r'[+\-*/=]'),  # Operadores aritméticos y de asignación
    ('LPAREN', r'\('),  # Paréntesis de apertura
    ('RPAREN', r'\)'),  # Paréntesis de cierre
    ('LBRACE', r'\{'),  # Llave de apertura
    ('RBRACE', r'\}'),  # Llave de cierre
    ('SEMICOLON', r';'),  # Punto y coma
    ('WHITESPACE', r'\s+'),  # Espacios en blanco
]

# Compilamos todas las expresiones regulares para cada tipo de token
token_regex_compiled = [(ttype, re.compile(pattern)) for ttype, pattern in token_definitions]

def lexer(source_code):
    """
    Función principal que convierte el código fuente en una lista de tokens.
    La función recorre el código, encuentra coincidencias con las expresiones regulares definidas 
    y las convierte en tokens. También maneja la información de las líneas y columnas.
    """
    position = 0  # Índice actual del código fuente
    found_tokens = []  # Lista de tokens encontrados
    line = 1  # Número de la línea actual
    col = 1  # Columna actual

    # Mientras no lleguemos al final del código
    while position < len(source_code):
        match = None  # Variable para almacenar la coincidencia con el patrón

        # Intentamos hacer coincidir cada uno de los patrones definidos en token_definitions
        for token_type, regex in token_regex_compiled:
            match = regex.match(source_code, position)
            if match:
                # Si encontramos una coincidencia, obtenemos el valor del token
                token_value = match.group(0)
                start_line = line  # Línea en la que comienza el token
                start_col = col  # Columna en la que comienza el token

                # Actualizamos las líneas y columnas en caso de que el token ocupe varias líneas
                lines = token_value.split('\n')
                if len(lines) > 1:
                    line += len(lines) - 1
                    col = len(lines[-1]) + 1
                else:
                    col += len(token_value)

                # Ignoramos los espacios y los comentarios
                if token_type not in ('WHITESPACE', 'COMMENT'):
                    # Si el token es un identificador y se encuentra en las palabras clave, lo cambiamos a 'KEYWORD'
                    if token_type == 'IDENTIFIER' and token_value in keywords:
                        token_type = 'KEYWORD'
                    # Añadimos el token a la lista de tokens encontrados
                    found_tokens.append((token_type, token_value, start_line, start_col))

                # Avanzamos la posición del código fuente hasta donde termina la coincidencia
                position = match.end()
                break  # Salimos del ciclo de intentos de coincidencia, ya que encontramos un token válido

        # Si no encontramos ninguna coincidencia, significa que tenemos un error en el código
        if not match:
            char_error = source_code[position]  # Obtenemos el carácter donde ocurrió el error
            raise SyntaxError(f"Token no reconocido '{char_error}' en línea {line}, columna {col}")  # Lanza un error

    return found_tokens  # Devuelve la lista de tokens encontrados
