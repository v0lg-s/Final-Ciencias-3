# -------------------------------------------------------------
# Analizador Sintáctico para Lenguajes de Programación
# Versión 4.0 - Febrero 1, 2025
# Desarrollado por: Ing. Jonathan Torres, Ph.D.
# -------------------------------------------------------------


# Variable global para la última línea procesada
last_token_line = None

# Función principal que maneja el análisis sintáctico
def parser(tokens):
    global last_token_line  # Acceder a la variable global que guarda la última línea procesada

    tokens = tokens.copy()  # Copiar los tokens para no modificar la lista original
    ast = []  # Lista donde se almacenará el árbol de sintaxis abstracta (AST)

    # Obtenemos la última línea de los tokens para informar sobre el contexto
    last_token = tokens[-1]
    last_token_line = last_token[2]  # Se asume que el tercer elemento de cada token es la línea

    # Procesar todos los tokens, agregando la estructura a 'ast'
    while tokens:
        try:
            ast.append(parse_statement(tokens))  # Llamar a la función que parsea las sentencias
        except SyntaxError as e:  # Si ocurre un error de sintaxis, lo propagamos
            raise SyntaxError(str(e))
    
    return ast  # Retorna el árbol de sintaxis abstracta (AST)

# Función para procesar una sentencia del código
def parse_statement(tokens):
    # Si el primer token es 'int' o 'float', procesamos como declaración
    if match_keyword(tokens, 'int') or match_keyword(tokens, 'float'):
        return parse_declaration(tokens)

    # Si el primer token es 'if', procesamos una estructura condicional
    elif match_keyword(tokens, 'if'):
        return parse_if(tokens)

    # Si el primer token es un identificador, procesamos una asignación
    elif match(tokens, 'IDENTIFIER'):
        return parse_assignment(tokens)

    # Si no es ninguno de los anteriores, es un error de sintaxis
    else:
        tipo, val, line, col = tokens[0]
        raise SyntaxError(f"Error en línea {line}, columna {col}: sentencia inválida, token inesperado '{val}'")

# Función para procesar una declaración (ejemplo: int a = 5;)
def parse_declaration(tokens):
    tipo = parse_type(tokens)  # Procesa el tipo de la declaración (ej. 'int', 'float')
    ident = parse_id(tokens)  # Procesa el identificador (ej. 'a')

    # Si el siguiente token es un punto y coma, significa que la declaración está completa
    if match(tokens, 'SEMICOLON'):
        tokens.pop(0)  # Consumir el token ';'
        return ('DECLARATION', tipo, ident)  # Retorna la estructura de la declaración
    
    # Si no es un punto y coma, debe ser una asignación
    parse_equals(tokens)  # Procesa el operador de asignación '='
    expr = parse_expression(tokens)  # Procesa la expresión a la derecha del '='
    parse_semi(tokens)  # Procesa el punto y coma al final
    return ('DECLARATION', tipo, ident, expr)  # Retorna la declaración con la expresión
# Función para procesar una asignación, por ejemplo: 'a = 5'
def parse_assignment(tokens):
    # Procesar el identificador (ej. 'a')
    ident = parse_id(tokens)
    
    # Procesar el operador de asignación ('=')
    parse_equals(tokens)
    
    # Procesar la expresión del lado derecho de la asignación (ej. '5')
    expr = parse_expression(tokens)
    
    # Procesar el punto y coma al final
    parse_semi(tokens)
    
    # Retornar la estructura de la asignación
    return ('ASSIGNMENT', ident, expr)

# Función para procesar una estructura condicional 'if'
def parse_if(tokens):
    # Verificamos si el primer token es la palabra clave 'if'
    expect_keyword(tokens, 'if')

    # Guardamos la información de la línea y columna del 'if' para mostrarla en caso de error
    if_line, if_col = tokens[0][2], tokens[0][3]

    # Espera el paréntesis de apertura '('
    expect(tokens, 'LPAREN')

    # Procesa la expresión dentro de los paréntesis
    cond = parse_expression(tokens)

    # Espera el paréntesis de cierre ')'
    expect(tokens, 'RPAREN')
    
    # Espera la llave de apertura '{'
    expect(tokens, 'LBRACE')

    block = []
    # Procesar sentencias dentro del bloque
    while tokens and not match(tokens, 'RBRACE'):
        block.append(parse_statement(tokens))

    # Si no hemos encontrado la llave de cierre 'RBRACE' y ya no quedan tokens, lanzar error
    if not match(tokens, 'RBRACE'):
        raise SyntaxError(f"Error en línea {if_line}, columna {if_col}: falta '}}' de cierre en el bloque 'if'")

    # Consumir la llave de cierre 'RBRACE'
    tokens.pop(0)

    # Retorna la estructura del bloque 'if' con su condición y bloque de sentencias
    return ('IF', cond, block)

# Función para procesar expresiones, que son comparaciones o operaciones
def parse_expression(tokens):
    return parse_comparison(tokens)

# Función para procesar expresiones de comparación (ejemplo: 'x > 5', 'y == 3')
def parse_comparison(tokens):
    # Primero procesamos las operaciones de adición y sustracción
    left = parse_add_sub(tokens)

    # Mientras encontremos un operador de comparación ('>', '<', '==')
    while match(tokens, 'GREATER') or match(tokens, 'LESS') or match(tokens, 'EQUALS') or match(tokens, 'NOTEQUAL'):
        _, op, _, _ = tokens.pop(0)  # Consumimos el operador de comparación
        # Procesamos la expresión de la derecha de la comparación
        right = parse_add_sub(tokens)
        # Retornamos la comparación estructurada
        left = (op, left, right)

    return left

# Función para procesar operaciones de adición y sustracción
def parse_add_sub(tokens):
    # Primero procesamos las multiplicaciones y divisiones
    left = parse_mul_div(tokens)
    # Mientras encontremos un operador de adición o sustracción
    while match(tokens, 'OPERATOR', '+') or match(tokens, 'OPERATOR', '-'):
        _, op, _, _ = tokens.pop(0)  # Consumimos el operador
        # Procesamos la expresión de la derecha
        right = parse_mul_div(tokens)
        # Retornamos la expresión con el operador aplicado
        left = (op, left, right)
    return left

# Función para procesar operaciones de multiplicación y división
def parse_mul_div(tokens):
    # Procesamos el primer operando
    left = parse_primary(tokens)
    # Mientras encontremos un operador de multiplicación o división
    while match(tokens, 'OPERATOR', '*') or match(tokens, 'OPERATOR', '/'):
        _, op, _, _ = tokens.pop(0)  # Consumimos el operador
        # Procesamos el operando de la derecha
        right = parse_primary(tokens)
        # Retornamos la expresión con el operador aplicado
        left = (op, left, right)

    return left

# Función para procesar los operandos primarios (números, identificadores o paréntesis)
def parse_primary(tokens):
    # Si encontramos un paréntesis de apertura, procesamos la expresión entre paréntesis
    if match(tokens, 'LPAREN'):
        tokens.pop(0)
        expr = parse_expression(tokens)
        # Verificamos que haya un paréntesis de cierre correspondiente
        if not match(tokens, 'RPAREN'):
            tipo, val, line, col = tokens[0]
            raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba RPAREN ')' pero se encontró '{val}'")
        tokens.pop(0)  # Consumimos 'RPAREN'
        return expr

    # Si encontramos un número, lo procesamos
    elif match(tokens, 'NUMBER'):
        return parse_num(tokens)
    
        # Si encontramos una cadena, la procesamos
    elif match(tokens, 'STRING'):
        return parse_string(tokens)

    # Si encontramos un carácter, lo procesamos
    elif match(tokens, 'CHAR'):
        return parse_char(tokens)


    # Si encontramos un identificador, lo procesamos
    elif match(tokens, 'IDENTIFIER'):
        return parse_id(tokens)

    # Si encontramos un operador de comparación '==', lanzamos un error
    elif match(tokens, 'OPERATOR') and tokens[0][1] == '==':
        _, val, line, col = tokens[0]
        raise SyntaxError(f"Error en línea {line}, columna {col}: expresión no puede comenzar con '=='")

    # Si no encontramos un token esperado, lanzamos un error
    else:
        tipo, val, line, col = tokens[0]
        raise SyntaxError(f"Error en línea {line}, columna {col}: token inesperado '{val}' en expresión")


# === FUNCIONES AUXILIARES ===

# Variable global para almacenar la última línea procesada en el analizador.
last_token_line = None

# Función para procesar un tipo de dato (int, float)
def parse_type(tokens):
    global last_token_line  # Accede a la variable global para la última línea procesada.

    # Si no hay más tokens, lanza un error especificando la última línea conocida.
    if not tokens:
        raise SyntaxError(f"Error en línea {last_token_line}: se esperaba tipo, pero no se encontró más tokens.")
    
    tipo, val, line, col = tokens.pop(0)  # Extrae el primer token de la lista.
    last_token_line = line  # Actualiza la última línea procesada con la línea actual.

    # Verifica si el tipo de token es 'int' o 'float', que son tipos válidos en este contexto.
    if tipo == 'KEYWORD' and val in ('int', 'float'):
        return val
    
    # Si no es un tipo válido, lanza un error especificando la línea y columna.
    raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba un tipo válido, pero se encontró '{val}'")

# Función para procesar un identificador (como variables o nombres de funciones)
def parse_id(tokens):
    global last_token_line  # Accede a la variable global de la última línea procesada.

    # Si no hay tokens disponibles, lanza un error especificando la última línea conocida.
    if not tokens:
        raise SyntaxError(f"Error en línea {last_token_line}: se esperaba identificador, pero no se encontró más tokens.")
    
    tipo, val, line, col = tokens.pop(0)  # Extrae el primer token de la lista.
    last_token_line = line  # Actualiza la última línea procesada con la línea actual.

    # Verifica si el token es un identificador válido.
    if tipo == 'IDENTIFIER':
        return val
    
    # Si el token no es un identificador válido, lanza un error con la línea y columna.
    raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba identificador, pero se encontró '{val}'")

# Función para procesar números (entero o decimal)
def parse_num(tokens):
    global last_token_line  # Accede a la variable global de la última línea procesada.

    # Si no hay más tokens, lanza un error especificando la última línea conocida.
    if not tokens:
        raise SyntaxError(f"Error en línea {last_token_line}: se esperaba número, pero no se encontró más tokens.")
    
    tipo, val, line, col = tokens.pop(0)  # Extrae el primer token de la lista.
    last_token_line = line  # Actualiza la última línea procesada con la línea actual.

    # Si el token es un número, lo procesa como entero o decimal según corresponda.
    if tipo == 'NUMBER':
        return float(val) if '.' in val else int(val)
    
    # Si el token no es un número válido, lanza un error con la línea y columna.
    raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba un número válido, pero se encontró '{val}'")

# Función para procesar el operador de asignación '='
def parse_equals(tokens):
    global last_token_line  # Accede a la variable global de la última línea procesada.

    # Si no hay más tokens, lanza un error especificando la última línea conocida.
    if not tokens:
        raise SyntaxError(f"Error en línea {last_token_line}: se esperaba '=', pero no se encontró más tokens.")
    
    tipo, val, line, col = tokens[0]  # Obtiene el tipo y valor del primer token.
    last_token_line = line  # Actualiza la última línea procesada con la línea actual.

    # Verifica que el token sea un operador '='.
    if tipo != 'OPERATOR' or val != '=':
        raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba '=', pero se encontró '{val}'.")
    
    tokens.pop(0)  # Consume el operador '='.

# Función para procesar el punto y coma ';' al final de las instrucciones
def parse_semi(tokens):
    global last_token_line  # Accede a la variable global de la última línea procesada.

    # Si no hay más tokens, lanza un error especificando la última línea conocida.
    if not tokens:
        raise SyntaxError(f"Error en línea {last_token_line}: se esperaba ';', pero no se encontró más tokens.")
    
    tipo, val, line, col = tokens[0]  # Obtiene el tipo y valor del primer token.
    last_token_line = line  # Actualiza la última línea procesada con la línea actual.

    # Verifica que el token sea un punto y coma ';'.
    if tipo != 'SEMICOLON':
        raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba ';', pero se encontró '{val}'.")
    
    tokens.pop(0)  # Consume el punto y coma ';'.


# Función para procesar cadenas de texto
def parse_string(tokens):
    tipo, val, line, col = tokens.pop(0)
    # Asegurarse que la cadena esté entre comillas dobles
    if tipo == 'STRING':
        return val  # Retorna el valor de la cadena
    raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba una cadena pero se encontró '{val}'")

# Función para procesar caracteres
def parse_char(tokens):
    tipo, val, line, col = tokens.pop(0)
    # Asegurarse que el carácter esté entre comillas simples
    if tipo == 'CHAR':
        return val  # Retorna el valor del carácter
    raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba un carácter pero se encontró '{val}'")

# Función para hacer coincidir un tipo de token y valor específico
def match(tokens, type_, value=None):
    if not tokens:
        return False
    tk_type, tk_val, *_ = tokens[0]  # Obtiene el tipo y valor del primer token
    return tk_type == type_ and (value is None or tk_val == value)

# Función para verificar si el token actual es una palabra clave
def match_keyword(tokens, keyword):
    if not tokens:
        return False
    tk_type, tk_val, *_ = tokens[0]  # Obtiene el tipo y valor del primer token
    return tk_type == 'KEYWORD' and tk_val == keyword

# Función para esperar un token específico
def expect(tokens, type_, value=None):
    if not match(tokens, type_, value):
        if tokens:
            tipo, val, line, col = tokens[0]  # Obtiene el tipo y valor del primer token
            raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba {type_} '{value}' pero se encontró '{val}'")
        else:
            raise SyntaxError(f"Error: se esperaba {type_} '{value}' pero se encontró EOF")
    tokens.pop(0)  # Consume el token esperado

# Función para esperar una palabra clave específica
def expect_keyword(tokens, keyword):
    if not match_keyword(tokens, keyword):
        if tokens:
            tipo, val, line, col = tokens[0]  # Obtiene el tipo y valor del primer token
            raise SyntaxError(f"Error en línea {line}, columna {col}: se esperaba palabra clave '{keyword}' pero se encontró '{val}'")
        else:
            raise SyntaxError(f"Error: se esperaba palabra clave '{keyword}' pero se encontró EOF")
    tokens.pop(0)  # Consume la palabra clave esperada

