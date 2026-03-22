from sqlalchemy import ColumnElement


def ilike_partial(column: ColumnElement[str], value: str) -> ColumnElement[bool]:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return column.ilike(f"%{escaped}%", escape="\\")
