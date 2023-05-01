import re

"""
Esta función recibe como argumento la ruta a un archivo de texto plano con un formato específico para definir tablas y sus datos.
Esta función lee el archivo línea por línea y al encontrar una línea que empieza con "TABLE", extrae el nombre de la tabla y crea una entrada en un diccionario llamado tables para almacenar sus columnas y filas. Luego, mientras se sigan leyendo líneas y ya se haya definido una tabla actual, la función verifica si ya se han definido las columnas. Si no es así, extrae los nombres de las columnas de la línea y los guarda en el diccionario de la tabla actual. Si ya se han definido las columnas, la función asume que las líneas siguientes contienen los valores de las filas y los agrega al diccionario de la tabla actual.
"""

def parse_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    tables = {}
    current_table = None
    for line in lines:
        if line.startswith("TABLE"):
            current_table = line.split()[1]
            tables[current_table] = {"columns": [], "rows": []}
        elif current_table:
            if not tables[current_table]["columns"]:
                tables[current_table]["columns"] = line.strip().split(',')
            else:
                tables[current_table]["rows"].append(line.strip().split(','))

    return tables

"""
Esta función recibe como argumentos una cadena de texto que representa una consulta SQL y el diccionario tables generado por la función parse_txt_file(). La función comienza analizando la consulta SQL mediante expresiones regulares para extraer las partes importantes: las columnas a seleccionar, la tabla a consultar y las condiciones y ordenamiento opcionales. Luego, verifica si la tabla especificada en la consulta existe en el diccionario tables. Si la tabla no existe, la función devuelve un mensaje de error.

Si la tabla existe, la función extrae las columnas especificadas en la consulta y verifica si alguna de ellas no pertenece a la tabla actual. Si hay alguna columna no válida, la función devuelve un mensaje de error.

Luego, la función recorre las filas de la tabla y aplica las condiciones especificadas en la consulta, si las hay. Si la fila no cumple con las condiciones, la función continúa con la siguiente fila. Si la fila cumple con las condiciones, la función extrae los valores de las columnas especificadas en la consulta y los agrega a una lista que representa el resultado de la consulta. Si la consulta especifica un ordenamiento, la función ordena la lista de resultados según las columnas y la dirección especificadas.
"""

def execute_query(query, tables):
    # Regular expressions to match SQL query components
    select_regex = r"SELECT\s+(?P<distinct>DISTINCT\s+)?(?P<columns>[\w\s\*,]+)\s+FROM\s+(?P<table>[\w]+)(?:\s+WHERE\s+(?P<conditions>[\w\s\=]+))?(?:\s+ORDER BY\s+(?P<order>[\w\s,]+)\s+(?P<direction>ASC|DESC))?"
    match = re.match(select_regex, query, re.IGNORECASE)

    if not match:
        return "Invalid query."

    groups = match.groupdict()
    table_name = groups['table']

    if table_name not in tables:
        return f"Table '{table_name}' not found."

    table = tables[table_name]
    table_columns = table["columns"]
    columns = groups['columns'].replace(" ", "").split(',')

    if "ALL" in columns or "*" in columns:
        columns = table_columns

    for column in columns:
        if column not in table_columns:
            return f"Column '{column}' not found in table '{table_name}'."

    result = []

    for row in table["rows"]:
        if groups['conditions']:
            condition_column, condition_value = groups['conditions'].split('=')
            condition_column = condition_column.strip()
            condition_value = condition_value.strip()

            if condition_column not in table_columns:
                return f"Column '{condition_column}' not found in table '{table_name}'."

            column_index = table_columns.index(condition_column)
            if row[column_index] != condition_value:
                continue

        if groups['distinct']:
            row_values = [row[table_columns.index(column)] for column in columns]
            if row_values in result:
                continue

        result.append([row[table_columns.index(column)] for column in columns])

    if groups['order']:
        order_columns = groups['order'].replace(" ", "").split(',')
        for column in order_columns:
            if column not in table_columns:
                return f"Column '{column}' not found in table '{table_name}'."

        order_indices = [table_columns.index(column) for column in order_columns]
        direction = 1 if groups['direction'].upper() == "ASC" else -1
        result.sort(key=lambda x: [x[i] for i in order_indices], reverse=direction == -1)

    return {"columns": columns, "data": result, "table_columns": table_columns}



"""
Esta función es la función principal del programa. Llama a la función parse_txt_file() para cargar los datos de las tablas del archivo de texto plano. Luego, solicita al usuario que ingrese una consulta SQL y llama a la función execute_query() para procesar la consulta y obtener el resultado. Finalmente, muestra el resultado de la consulta en la consola.
"""

def main():
    tables = parse_txt_file("C:/Users/alexr/Documents/COMPILADORES/ProyectoF.txt")
    query = input("Introduce tu consulta SQL: ")
    result = execute_query(query, tables)
    print(result)

if __name__ == "__main__":
    main()
