import argparse
from lexer import lexer
from parser import parser
from semantic import semantic_analyze
from intermediate import IntermediateCodeGenerator
from objectcode import ObjectCodeGenerator

def compilar(codigo_fuente, mostrar_tokens=False, mostrar_ast=False, mostrar_cuadruplas=False):
    """
    Ejecuta todas las fases del compilador de forma secuencial:
    1. Análisis léxico
    2. Análisis sintáctico
    3. Análisis semántico
    4. Generación de código intermedio (cuádruplas)
    5. Generación de código objeto (ensamblador simple)

    Parámetros:
    - codigo_fuente: cadena con el código fuente completo.
    - mostrar_tokens: bool, si se desea imprimir los tokens.
    - mostrar_ast: bool, si se desea imprimir el árbol de sintaxis abstracta.
    - mostrar_cuadruplas: bool, si se desea imprimir las cuádruplas generadas.
    """
    print("\n[COMPILADOR INICIADO]")

    # Fase 1: Análisis léxico
    tokens = lexer(codigo_fuente)
    if mostrar_tokens:
        print("\n[TOKENS]")
        for t in tokens:
            print(t)

    # Fase 2: Análisis sintáctico
    ast = parser(tokens)
    if mostrar_ast:
        print("\n[ÁRBOL DE SINTAXIS ABSTRACTA (AST)]")
        for nodo in ast:
            print(nodo)

    # Fase 3: Análisis semántico
    semantic_analyze(ast)
    print("\n[ANÁLISIS SEMÁNTICO] ✔️ Sin errores")

    # Fase 4: Generación de código intermedio (cuádruplas)
    gen_intermedio = IntermediateCodeGenerator()
    cuads = gen_intermedio.generate(ast)
    if mostrar_cuadruplas:
        print("\n[CÓDIGO INTERMEDIO - CUÁDRUPLAS]")
        for q in cuads:
            print(q)

    # Fase 5: Generación de código objeto
    gen_objeto = ObjectCodeGenerator()
    instrucciones = gen_objeto.generate(cuads)

    print("\n[CÓDIGO OBJETO]")
    for instr in instrucciones:
        print(instr)

    print("\n[COMPILACIÓN COMPLETA ✅]\n")

def main():
    """
    Función principal que maneja la interfaz por línea de comandos.
    Permite ejecutar el compilador con opciones adicionales para depuración.
    """
    parser_args = argparse.ArgumentParser(description="Compilador simple")

    # Argumento obligatorio: archivo fuente
    parser_args.add_argument("archivo", help="Archivo de entrada con código fuente")

    # Opciones adicionales para mostrar fases del compilador
    parser_args.add_argument("--tokens", action="store_true", help="Mostrar tokens")
    parser_args.add_argument("--ast", action="store_true", help="Mostrar AST")
    parser_args.add_argument("--cuadruplas", action="store_true", help="Mostrar código intermedio")

    args = parser_args.parse_args()

    try:
        with open(args.archivo, "r", encoding="utf-8") as f:
            codigo = f.read()
        compilar(
            codigo,
            mostrar_tokens=args.tokens,
            mostrar_ast=args.ast,
            mostrar_cuadruplas=args.cuadruplas
        )
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA COMPILACIÓN:\n{e}\n")

if __name__ == "__main__":
    main()
