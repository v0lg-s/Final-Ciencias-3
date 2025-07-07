class IntermediateCodeGenerator:
    """
    Generador de código intermedio (cuádruplas) a partir de un árbol de sintaxis abstracta (AST).
    Traduce instrucciones en forma de tuplas AST a una secuencia de cuádruplas para facilitar
    la generación posterior de código objeto.
    """

    def __init__(self):
        self.temp_counter = 0       # Contador para temporales (t1, t2, ...)
        self.label_counter = 0      # Contador para etiquetas (L1, L2, ...)
        self.code = []              # Lista de cuádruplas generadas

    def new_temp(self):
        """
        Genera un nuevo nombre de variable temporal.
        """
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        """
        Genera un nuevo nombre de etiqueta para saltos condicionales.
        """
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self, ast):
        """
        Genera cuádruplas a partir de una lista de nodos del AST.

        Parámetro:
        - ast: lista de tuplas que representan instrucciones del árbol de sintaxis.

        Retorna:
        - Lista de cuádruplas generadas.
        """
        self.code = []  # Reinicia el código generado
        for stmt in ast:
            self._generate_stmt(stmt)
        return self.code

    def _generate_stmt(self, node):
        """
        Genera cuádruplas para una instrucción individual (declaración, asignación, if...).
        """
        kind = node[0]

        # Declaración de variable con valor inicial (int x = expr;)
        if kind == "DECLARATION":
            if len(node) == 3:
                # Declaración sin inicialización (e.g., int x;)
                return
            _, _, name, expr = node
            result = self._generate_expr(expr)
            self.code.append((name, '=', result, ''))

        # Asignación simple (x = expr;)
        elif kind == "ASSIGNMENT":
            _, name, expr = node
            result = self._generate_expr(expr)
            self.code.append((name, '=', result, ''))

        # Condicional (if (cond) { ... })
        elif kind == "IF":
            _, cond_expr, block = node
            cond_result = self._generate_expr(cond_expr)
            false_label = self.new_label()
            self.code.append(('GOTOF', cond_result, false_label, ''))

            # Genera cuádruplas para el bloque dentro del if
            for stmt in block:
                self._generate_stmt(stmt)

            self.code.append(('LABEL', false_label, '', ''))

    def is_literal(self, expr):
        """
        Determina si una expresión es un literal (int, float, string o char).
        """
        return isinstance(expr, (int, float)) or (
            isinstance(expr, str) and (expr.startswith('"') or expr.startswith("'"))
        )

    def _generate_expr(self, expr):
        """
        Genera cuádruplas para una expresión (aritmética, literal, variable, etc.).
        Devuelve el nombre del temporal donde se almacena el resultado.

        Ejemplos:
        - 5        → genera t1 = 5
        - ('+', 'a', 3) → genera t2 = a + 3
        """
        # Literal (constante numérica o string/char)
        if self.is_literal(expr):
            temp = self.new_temp()
            self.code.append((temp, '=', expr, ''))
            return temp

        # Expresión binaria: operador y dos operandos
        elif isinstance(expr, tuple):
            op = expr[0]
            left = self._generate_expr(expr[1])
            right = self._generate_expr(expr[2])
            temp = self.new_temp()
            self.code.append((temp, op, left, right))
            return temp

        # Variable o identificador
        elif isinstance(expr, str):
            return expr

        # Cualquier otra estructura no válida
        else:
            raise ValueError(f"Expresión no válida: {expr}")
