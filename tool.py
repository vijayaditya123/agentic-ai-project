from sqlalchemy import inspect,text
from db import engine_read
from datetime import datetime
import matplotlib.pyplot as plt
def get_schema():
    insp = inspect(engine_read)
    lines =[]
    for table in insp.get_table_names():
        pk_column = insp.get_pk_constraint(table)["constrained_columns"]
        fk_map={}
        for fk in insp.get_foreign_keys(table):
            for col,ref_key in zip(fk["constrained_columns"], fk["referred_columns"]):
               fk_map[col]= f"{fk['referred_table']}.{ref_key}"

        lines.append(f"Table : {table}")
        for col in insp.get_columns(table):
            text = f" {col['name']} ({col["type"]})"
            if col["name"] in pk_column:
                text += " PRIMARY KEY"
            if col["name"] in fk_map:
                text += f" ->{fk_map[col["name"]]}"
            lines.append(text)
        lines.append("")
    return "\n".join(lines)         

def run_sql(query , max_rows=100):
    cleanned = query.strip().rstrip(";")
    if not cleanned.lower().startswith(("select","with")):
        return "Error :only  SELECT queries are allowed"

    try:
        with engine_read.connect() as conn:
            result = conn.execute(text(cleanned))
            columns = list(result.keys())
            rows=result.fetchmany(max_rows + 1)
    except Exception as e:
        return f"Error : {e}"

    truncated = len(rows) > max_rows
    rows = rows[:max_rows]

    if not rows:
        return "Query returned 0 rows."

    lines = [" | ".join(columns)]
    for row in rows:
        lines.append(" | ".join(str(value) for value in row))
    if truncated:
        lines.append(f"... (showing first {max_rows} rows, more exist)")
    return "\n".join(lines)

def _product(values):
    result = 1
    for v in values:
        result = result * v
    return result

def run_python(operation, values):

    two_value_ops = {"subtract", "divide", "remainder", "percentage"}

    if operation not in OPERATIONS:
        return f"Error: unknown operation '{operation}'."

    if operation in two_value_ops and len(values) != 2:
        return f"Error: {operation} needs exactly 2 values, got {len(values)}."

    if operation == "average" and len(values) < 1:
        return "Error: average needs at least 1 value."

    if operation == "divide" and values[1] == 0:
        return "Error: cannot divide by zero."

    if operation == "percentage" and values[1] == 0:
        return "Error: cannot calculate a percentage with a whole of zero."

    result = OPERATIONS[operation](values)
    return str(round(result, 2))

OPERATIONS = {
    "add":        lambda v: sum(v),
    "subtract":   lambda v: v[0] - v[1],
    "multiply":   lambda v: _product(v),
    "divide":     lambda v: v[0] / v[1],
    "remainder":  lambda v: v[0] % v[1],
    "average":    lambda v: sum(v) / len(v),
    "percentage": lambda v: v[0] / v[1] * 100,
}

def make_chart(chart_type, title, labels=None, values=None, x_values=None, x_label=None, y_label=None):
    if chart_type not in {"bar", "horizontal_bar", "line", "pie", "scatter", "histogram"}:
        return f"{chart_type} is not available we can return charts charts like bar,horizontal_bar, line,pie,scatter,histogram" 

    if chart_type in  {"bar", "horizontal_bar", "line", "pie"} and (title is None or labels is None or values is None):
        return "Error : requied values are missing"

    if chart_type == "scatter" and (x_values is None or values is None):
        return "Error: scatter needs x_values and values."

    if chart_type == "horizontal_bar" and (labels is None or values is None):
        return "Error: horizontal_bar needs labels and values."

    fig, ax = plt.subplots()
    graph[chart_type](ax,title, labels, values, x_values, x_label, y_label)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    path = f"charts/{chart_type}_{datetime.now():%Y%m%d%H%M%S}.png"
    fig.savefig(path)
    plt.close(fig)
    return path




graph={
    "line": lambda ax,title, labels, values, x_values, x_label, y_label : ax.plot(labels, values, marker="o"),
    "bar":lambda ax,title, labels, values, x_values, x_label, y_label : ax.bar(labels, values),
    "horizontal_bar":lambda ax,title, labels, values, x_values, x_label, y_label :ax.barh(labels, values),
    "pie":lambda ax,title, labels, values, x_values, x_label, y_label :ax.pie(values, labels=labels, autopct="%1.1f%%"),
    "scatter":lambda ax,title, labels, values, x_values, x_label, y_label :ax.scatter(values, labels=labels, autopct="%1.1f%%"),
    "histogram":lambda ax,title, labels, values, x_values, x_label, y_label :ax.hist(values, bins=10)
}

    

        
    


