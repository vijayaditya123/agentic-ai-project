from sqlalchemy import inspect
from db import engine_read
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


