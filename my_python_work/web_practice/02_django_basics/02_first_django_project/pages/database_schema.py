"""Read-only database schema data for the staff explorer."""

from django.apps import apps
from django.db import connection


def _display(value, empty="—"):
    if value is None or value == "":
        return empty
    return str(value)


def _constraint_kind(details):
    if details["primary_key"]:
        return "PRIMARY KEY"
    if details["foreign_key"]:
        return "FOREIGN KEY"
    if details["unique"] and details["index"]:
        return "UNIQUE INDEX"
    if details["unique"]:
        return "UNIQUE"
    if details["check"]:
        return "CHECK"
    if details["index"]:
        return "INDEX"
    return "CONSTRAINT"


def _postgres_column_types(cursor, table_name):
    if connection.vendor != "postgresql":
        return {}

    cursor.execute(
        """
        SELECT a.attname, format_type(a.atttypid, a.atttypmod)
        FROM pg_catalog.pg_attribute AS a
        JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE c.relname = %s
          AND a.attnum > 0
          AND NOT a.attisdropped
          AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
          AND pg_catalog.pg_table_is_visible(c.oid)
        ORDER BY a.attnum
        """,
        [table_name],
    )
    return dict(cursor.fetchall())


def _row_count(cursor, table_name, table_type):
    if table_type not in {"t", "v", "p"}:
        return None

    quoted_table = connection.ops.quote_name(table_name)
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {quoted_table}")
        return cursor.fetchone()[0]
    except Exception:
        return None


def get_database_schema():
    """Return database metadata without loading user row contents."""
    introspection = connection.introspection
    model_labels = {
        model._meta.db_table: model._meta.label
        for model in apps.get_models()
        if model._meta.managed
    }
    table_kind_labels = {
        "t": "table",
        "v": "view",
        "p": "partition",
    }

    tables = []
    relationships = []
    total_rows = 0

    with connection.cursor() as cursor:
        table_infos = sorted(
            introspection.get_table_list(cursor),
            key=lambda table_info: table_info.name,
        )

        for table_info in table_infos:
            table_name = table_info.name
            table_type = getattr(table_info, "type", "t")
            description = introspection.get_table_description(cursor, table_name)
            postgres_types = _postgres_column_types(cursor, table_name)
            constraints = introspection.get_constraints(cursor, table_name)
            relations = introspection.get_relations(cursor, table_name)
            primary_key_columns = set(
                introspection.get_primary_key_columns(cursor, table_name) or []
            )

            column_rows = []
            for field in description:
                relation = relations.get(field.name)
                foreign_key = None
                if relation:
                    target_column, target_table, on_delete = relation
                    foreign_key = {
                        "target_table": target_table,
                        "target_column": target_column,
                        "on_delete": _display(on_delete),
                    }

                try:
                    django_type = introspection.get_field_type(
                        field.type_code,
                        field,
                    )
                except (KeyError, TypeError):
                    django_type = "Unknown"

                column_rows.append(
                    {
                        "name": field.name,
                        "database_type": postgres_types.get(
                            field.name,
                            _display(field.type_code, "unknown"),
                        ),
                        "django_type": django_type,
                        "nullable_display": "Yes" if field.null_ok else "No",
                        "default_display": _display(field.default),
                        "primary_key": (
                            field.name in primary_key_columns
                            or getattr(field, "pk", False)
                        ),
                        "auto_increment": getattr(field, "is_autofield", False),
                        "foreign_key": foreign_key,
                    }
                )

            constraint_rows = []
            for constraint_name, details in sorted(constraints.items()):
                foreign_key = details.get("foreign_key")
                target_display = ""
                if foreign_key:
                    target_display = f"{foreign_key[0]}.{foreign_key[1]}"
                    relationships.append(
                        {
                            "name": constraint_name,
                            "from_table": table_name,
                            "from_columns": details.get("columns") or [],
                            "to_table": foreign_key[0],
                            "to_columns": [foreign_key[1]],
                        }
                    )

                columns = details.get("columns") or []
                constraint_rows.append(
                    {
                        "name": constraint_name,
                        "kind": _constraint_kind(details),
                        "columns_display": ", ".join(columns) or "—",
                        "target_display": target_display,
                        "index_type": _display(details.get("type"), ""),
                    }
                )

            row_count = _row_count(cursor, table_name, table_type)
            if row_count is not None:
                total_rows += row_count

            tables.append(
                {
                    "name": table_name,
                    "kind": table_kind_labels.get(table_type, table_type),
                    "model_label": model_labels.get(table_name, "—"),
                    "row_count_display": _display(row_count),
                    "column_count": len(column_rows),
                    "foreign_key_count": sum(
                        1 for column in column_rows if column["foreign_key"]
                    ),
                    "columns": column_rows,
                    "constraints": constraint_rows,
                    "application_table": table_name.startswith(
                        ("dictionary_", "auth_")
                    ),
                }
            )

    return {
        "backend": connection.vendor,
        "backend_label": connection.display_name,
        "table_count": len(tables),
        "relationship_count": len(relationships),
        "total_rows": total_rows,
        "tables": tables,
        "relationships": relationships,
    }
