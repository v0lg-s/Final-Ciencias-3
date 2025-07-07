from lexer import lexer
from parser import parser
from semantic import semantic_analyze
from intermediate import IntermediateCodeGenerator
from objectcode import ObjectCodeGenerator

def ejecutar_prueba(codigo, descripcion, debe_funcionar=True):
    print("=" * 100)
    print(f"[PRUEBA] {descripcion}")
    print("-" * 100)
    print("[CÓDIGO FUENTE]")
    print(codigo.strip())

    try:
        tokens = lexer(codigo)
        print("\n[TOKENS]")
        for t in tokens:
            print(t)

        ast = parser(tokens)
        print("\n[AST]")
        for nodo in ast:
            print(nodo)

        semantic_analyze(ast)
        print("\n[ANÁLISIS SEMÁNTICO] ✔️ Correcto")

        inter = IntermediateCodeGenerator()
        cuads = inter.generate(ast)
        print("\n[CUÁDRUPLAS]")
        for q in cuads:
            print(q)

        obj = ObjectCodeGenerator()
        instrucciones = obj.generate(cuads)
        print("\n[CÓDIGO OBJETO]")
        for instr in instrucciones:
            print(instr)

        if debe_funcionar:
            print("\n✅ PRUEBA EXITOSA")
        else:
            print("\n❌ ERROR: Se esperaba un fallo semántico, pero pasó correctamente.")

    except Exception as e:
        if not debe_funcionar:
            print("\n✅ ERROR DETECTADO COMO SE ESPERABA:")
            print(e)
        else:
            print("\n❌ ERROR INESPERADO:")
            print(e)

def pruebas_de_la_guia():
    print("\n\n🧪================ PRUEBAS DE LA GUÍA DE LA PRÁCTICA ================\n")
    casos = [
        (
            """
            int a = 5;
            int b = 3;
            int c = a + b;
            """,
            "Ejemplo 1: Declaración y operación válida",
            True
        ),
        (
            """
            int x = 2;
            int y = 3;
            int z = x + y * 4;
            """,
            "Ejemplo 2: Operación aritmética anidada",
            True
        ),
        (
            """
            int a = b + 1;
            """,
            "Ejemplo 3: Error semántico por variable no declarada",
            False
        )
    ]
    for codigo, desc, valido in casos:
        ejecutar_prueba(codigo, desc, valido)

def pruebas_adicionales():
    print("\n\n================ PRUEBAS ADICIONALES PROPUESTAS ===================\n")
    casos = [
                (
            """
            int a = 1;
            a = a + 1;
            a = a * 2 + 3;
            """,
            "Asignaciones encadenadas con operaciones compuestas",
            True
        ),
        (
            """
            int a = 10;
            int b = 5;
            if (a != b) {
                a = a - b;
            }
            """,
            "Condicional con operador de desigualdad (!=)",
            True
        ),
        (
            """
            int a = 1;
            if (a == 1) {
                if (a < 2) {
                    if (a > 0) {
                        a = a + 1;
                    }
                }
            }
            """,
            "If anidados con múltiples condiciones lógicas",
            True
        ),
        (
            """
            int a = 4;
            int b = 2;
            int c = a / b - 1;
            """,
            "Expresión con división y resta combinadas",
            True
        ),
        (
            """
            if (1 < 2) {
                int x = 10;
            }
            """,
            "Declaración de variable dentro de un bloque if (scope control limitado)",
            True
        )
    ]
    for codigo, desc, valido in casos:
        ejecutar_prueba(codigo, desc, valido)

if __name__ == "__main__":
    pruebas_de_la_guia()
    pruebas_adicionales()
