class ObjectCodeGenerator:
    """
    Generador de código objeto a partir de cuádruplas intermedias.
    Traduce instrucciones intermedias a una representación tipo ensamblador simple.
    """

    def __init__(self):
        # Lista de instrucciones generadas en formato de pseudocódigo ensamblador
        self.instructions = []

    def generate(self, quads):
        """
        Traduce una lista de cuádruplas a instrucciones tipo ensamblador.

        Parámetros:
        - quads: lista de tuplas (cuádruplas) representando el código intermedio.

        Retorna:
        - Lista de instrucciones tipo ensamblador.
        """
        self.instructions = []  # Reinicia para permitir reutilización

        for quad in quads:
            op = quad[1] if len(quad) > 1 else None  # Extrae el operador

            # Instrucción de salto condicional (if-false)
            if quad[0] == 'GOTOF':
                cond = quad[1]
                label = quad[2]
                self._emit_load(cond)
                self._emit(f"JUMP_IF_FALSE {label}")

            # Instrucción de salto incondicional
            elif quad[0] == 'GOTO':
                label = quad[1]
                self._emit(f"JUMP {label}")

            # Marca de etiqueta (LABEL)
            elif quad[0] == 'LABEL':
                label = quad[1]
                self._emit(f"LABEL {label}")

            # Asignación directa (a = b)
            elif op == '=':
                dest, _, src, _ = quad
                self._emit_load(src)
                self._emit(f"STORE {dest}")

            # Operaciones aritméticas binarias: +, -, *, /
            elif op in {'+', '-', '*', '/'}:
                dest, _, left, right = quad
                self._emit_load(left)
                mnemonic = {
                    '+': 'ADD',
                    '-': 'SUB',
                    '*': 'MUL',
                    '/': 'DIV'
                }[op]
                self._emit(f"{mnemonic} {right}")
                self._emit(f"STORE {dest}")

            # Operaciones relacionales: <, >, ==, !=
            elif op in {'<', '>', '==', '!='}:
                dest, _, left, right = quad
                self._emit_load(left)
                cmp_op = {
                    '<': 'CMP_LT',
                    '>': 'CMP_GT',
                    '==': 'CMP_EQ',
                    '!=': 'CMP_NE'
                }[op]
                self._emit(f"{cmp_op} {right}")
                self._emit(f"STORE {dest}")

            # Si ninguna de las anteriores coincide, es un error
            else:
                raise ValueError(f"Cuádrupla no soportada: {quad}")

        return self.instructions

    def _emit(self, instr):
        """
        Añade una instrucción al código objeto generado.
        """
        self.instructions.append(instr)

    def _emit_load(self, value):
        """
        Genera la instrucción LOAD para cargar un valor o variable.
        """
        self._emit(f"LOAD {value}")
