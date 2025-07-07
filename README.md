# Cómo ejecutar el compilador
Desde la terminal, ejecutar el script compilador.py seguido del archivo fuente:

```bash
python compilador.py txt_pruebas/prueba1_if_simple.txt
```

Se pueden añadir opciones para mostrar salidas intermedias:

| Opción         | Descripción                          |
| -------------- | ------------------------------------ |
| `--tokens`     | Muestra la lista de tokens obtenidos |
| `--ast`        | Muestra el árbol de sintaxis (AST)   |
| `--cuadruplas` | Muestra las cuádruplas generadas     |


## Ejemplo completo:

```bash
python compilador.py txt_pruebas/prueba1_if_simple.txt --tokens --ast --cuadruplas
```
