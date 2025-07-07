"""
Archivo: semantic.py

Analizador semántico para el lenguaje definido en la práctica.

Objetivo:
Verificar que el programa tenga sentido lógico, asegurando el uso correcto
de variables, funciones, tipos de datos, estructuras de control y ámbitos anidados.

Este analizador cumple con los literales a–i, y además:
- Declara y verifica funciones con sus argumentos y tipos de retorno
- Maneja scopes anidados mediante una pila
- Detecta y advierte shadowing de variables (variables con el mismo nombre en diferentes scopes) 
"""
# Tabla global de funciones (nombre → parámetros y tipo de retorno)
functions = {}

# Pila de scopes anidados (cada uno es un diccionario variable → tipo)
scope_stack = []

# ========================
# Manejo de scopes
# ========================

def enter_scope():
    """Crea un nuevo ámbito local (nuevo diccionario en la pila)."""
    scope_stack.append({})

def exit_scope():
    """Elimina el ámbito actual (último diccionario en la pila)."""
    scope_stack.pop()

def current_scope():
    """Obtiene el scope actual (el más interno)."""
    return scope_stack[-1] if scope_stack else {}

def is_declared(name):
    """Verifica si una variable ha sido declarada en algún scope."""
    for scope in reversed(scope_stack):
        if name in scope:
            return True
    return False

def get_declared_type(name):
    """Obtiene el tipo de una variable ya declarada en cualquier scope."""
    for scope in reversed(scope_stack):
        if name in scope:
            return scope[name]
    raise Exception(f"Error semántico: la variable '{name}' no ha sido declarada.")

def declare_variable(name, var_type):
    """
    Declara una nueva variable en el scope actual.
    Valida duplicación local (literal a) y advierte si hace shadowing (oculta otra variable externa).
    """
    if name in current_scope():
        raise Exception(f"Error semántico: la variable '{name}' ya fue declarada en este ámbito.")
    for outer_scope in scope_stack[:-1]:
        if name in outer_scope:
            print(f"Advertencia: la variable local '{name}' oculta una variable del ámbito externo (shadowing).")
            break
    current_scope()[name] = var_type

# ========================
# Manejo de funciones
# ========================

def declare_function(name, param_list, return_type):
    """
    Registra una nueva función en la tabla global de funciones.
    Valida duplicación de nombre.
    """
    if name in functions:
        raise Exception(f"Error semántico: la función '{name}' ya fue declarada.")
    functions[name] = {"params": param_list, "return": return_type}

def check_function_call(name, arg_types):
    """
    Verifica la existencia de la función, la aridad y los tipos de los argumentos.
    """
    if name not in functions:
        raise Exception(f"Error semántico: la función '{name}' no ha sido declarada.")
    expected = functions[name]["params"]
    if len(expected) != len(arg_types):
        raise Exception(f"Error semántico: la función '{name}' esperaba {len(expected)} argumentos, se recibieron {len(arg_types)}.")
    for i, ((expected_type, _), actual_type) in enumerate(zip(expected, arg_types)):
        if not are_types_compatible(expected_type, actual_type):
            raise Exception(f"Error semántico: argumento {i+1} de '{name}' debe ser '{expected_type}', se recibió '{actual_type}'.")

# ========================
# Análisis semántico general
# ========================

def semantic_analyze(ast):
    """
    Función principal del analizador semántico.
    Recorre el AST generado por el parser y realiza validaciones semánticas.

    Args:
        ast (list): Lista de nodos del árbol de sintaxis abstracta (AST).

    Raises:
        Exception: Si se detecta algún error semántico.
    """
    enter_scope()
    used_variables = set()

    for node in ast:
        _analyze_node(node, used_variables)
    # Validación de variables no usadas (literal h)
    unused = [var for var in current_scope() if var not in used_variables]
    if unused:
        print(f"Advertencia: las siguientes variables no se usaron: {', '.join(unused)}")
    
    exit_scope()

# ========================
# Evaluación de nodos del AST
# ========================

def _analyze_node(node, used_variables):
    node_type = node[0]

    if node_type == "DECLARATION":
        # Validación de declaración previa de variables (literal a)
        var_type = node[1]
        var_name = node[2]
        value = node[3] if len(node) == 4 else None

        declare_variable(var_name, var_type)
        if value is not None:
            val_type = evaluate_expression(value, used_variables)
            if not are_types_compatible(var_type, val_type):
                raise Exception(f"Error semántico: tipo incompatible, se esperaba '{var_type}', se recibió '{val_type}'.")



    elif node_type == "ASSIGNMENT":
        var_name = node[1]
        expr = node[2]

        if not is_declared(var_name):
            raise Exception(f"Error semántico: la variable '{var_name}' no ha sido declarada.")

        val_type = evaluate_expression(expr, used_variables)
        expected_type = get_declared_type(var_name)

        if not are_types_compatible(expected_type, val_type):
            raise Exception(f"Error semántico: tipo incompatible. No se puede asignar '{val_type}' a '{expected_type}'.")

        used_variables.add(var_name)

    elif node_type == "IF":
        condition = node[1]
        block = node[2]

        cond_type = evaluate_expression(condition, used_variables)
        if cond_type != "bool":
            raise Exception("Error semántico: la condición del 'if' debe ser booleana.")

        enter_scope()
        for stmt in block:
            _analyze_node(stmt, used_variables)
        exit_scope()

    elif node_type == "FUNCTION_DECLARATION":
        # Declaración de función con nuevo scope (param_list: [(tipo, nombre)])
        name = node[1]
        params = node[2]
        return_type = node[3]
        block = node[4]

        declare_function(name, params, return_type)

        enter_scope()
        for param_type, param_name in params:
            declare_variable(param_name, param_type)
        for stmt in block:
            _analyze_node(stmt, used_variables)
        exit_scope()

    elif node_type == "FUNCTION_CALL":
        # Validación de llamada a función: existencia, aridad, tipos
        name = node[1]
        args = node[2]
        arg_types = [evaluate_expression(arg, used_variables) for arg in args]
        check_function_call(name, arg_types)

    else:
        raise Exception(f"Error semántico: tipo de nodo no reconocido '{node_type}'")

# ========================
# Evaluación de expresiones
# ========================

def evaluate_expression(expr, used_variables):
    """
    Evalúa el tipo de una expresión en el AST.
    Admite literales, variables, operaciones y comparaciones.

    Args:
        expr: La expresión a evaluar.
        used_variables (set): Conjunto de variables utilizadas.

    Returns:
        str: Tipo inferido de la expresión ('int', 'float', 'string', 'char', 'bool').

    Raises:
        Exception: Si se encuentra una variable no declarada o una operación inválida.
    """
    if isinstance(expr, int):
        return "int"
    elif isinstance(expr, float):
        return "float"
    elif isinstance(expr, str):
        if expr.startswith('"') and expr.endswith('"'):
            return "string"
        elif expr.startswith("'") and expr.endswith("'"):
            return "char"
        elif expr == "true" or expr == "false":
            return "bool"
        elif is_declared(expr):
            used_variables.add(expr)
            return get_declared_type(expr)
        else:
            raise Exception(f"Error semántico: la variable '{expr}' no ha sido declarada.")      
    elif isinstance(expr, tuple):
        op, left, right = expr
        lt = evaluate_expression(left, used_variables)
        rt = evaluate_expression(right, used_variables)

        # Validación de operadores (d), tipo booleano (e), división por cero (f)
        if op in {"+", "-", "*", "/"}:
            if lt == rt and lt in {"int", "float"}:
                if op == "/" and isinstance(right, (int, float)) and right == 0:
                    raise Exception("Error semántico: división por cero.")
                return "float" if "float" in (lt, rt) else "int"
            else:
                raise Exception(f"Error semántico: operación '{op}' inválida entre '{lt}' y '{rt}'.")
        elif op in {"==", ">", "<","!="}:
            if lt != rt:
                raise Exception(f"Error semántico: comparación entre tipos incompatibles '{lt}' y '{rt}'.")
            return "bool"
        else:
            raise Exception(f"Error semántico: operador desconocido '{op}'.")

    else:
        raise Exception(f"Error semántico: expresión no válida: {expr}")

# ========================
# Compatibilidad de tipos
# ========================

def are_types_compatible(expected, actual):
    """
    Literal c: Verifica si un tipo puede ser asignado implícitamente al otro.
    Permite int → float, pero no al revés (para evitar pérdida de precisión).
    """
    return expected == actual or (expected == "float" and actual == "int")