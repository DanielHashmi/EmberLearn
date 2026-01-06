#!/usr/bin/env python3
"""Generate SQLAlchemy models from data-model.md specification."""

import os
import re
import sys
from pathlib import Path


def parse_data_model(data_model_path: str) -> list[dict]:
    """Parse data-model.md and extract entity definitions."""
    with open(data_model_path, 'r') as f:
        content = f.read()

    entities = []

    # Find all entity sections (## 1. EntityName format)
    entity_pattern = r'## \d+\.\s+(\w+)\n\n\*\*Purpose\*\*:\s*(.+?)\n\n.*?\n\n\| Field \| Type \| Constraints \| Description \|\n\|.*?\n((?:\|.+?\n)+)'

    for match in re.finditer(entity_pattern, content, re.DOTALL):
        entity_name = match.group(1)
        purpose = match.group(2).strip()
        fields_table = match.group(3)

        fields = []
        for field_row in fields_table.strip().split('\n'):
            if field_row.startswith('|'):
                parts = [p.strip() for p in field_row.split('|')[1:-1]]
                if len(parts) >= 4 and parts[0] != '------':
                    field_name = parts[0].strip('`')
                    field_type = parts[1]
                    constraints = parts[2]
                    description = parts[3]
                    fields.append({
                        'name': field_name,
                        'type': field_type,
                        'constraints': constraints,
                        'description': description
                    })

        entities.append({
            'name': entity_name,
            'purpose': purpose,
            'fields': fields
        })

    return entities


def map_sql_type_to_sqlalchemy(sql_type: str) -> str:
    """Map SQL type to SQLAlchemy column type."""
    sql_type = sql_type.upper()

    if 'INTEGER' in sql_type or 'INT' in sql_type:
        return 'Integer'
    elif 'VARCHAR' in sql_type:
        match = re.search(r'\((\d+)\)', sql_type)
        if match:
            return f'String({match.group(1)})'
        return 'String(255)'
    elif 'TEXT' in sql_type:
        return 'Text'
    elif 'TIMESTAMP' in sql_type or 'DATETIME' in sql_type:
        return 'DateTime'
    elif 'UUID' in sql_type:
        return 'UUID'
    elif 'BOOLEAN' in sql_type or 'BOOL' in sql_type:
        return 'Boolean'
    elif 'DECIMAL' in sql_type or 'NUMERIC' in sql_type:
        return 'Numeric'
    elif 'FLOAT' in sql_type:
        return 'Float'
    elif 'ENUM' in sql_type:
        # Extract enum values
        match = re.search(r"ENUM\((.*?)\)", sql_type)
        if match:
            values = [v.strip("'\"") for v in match.group(1).split(',')]
            return f"Enum({', '.join(repr(v) for v in values)}, name='{values[0]}_enum')"
        return 'String(50)'
    else:
        return 'String(255)'


def parse_constraints(constraints: str) -> dict:
    """Parse constraints column into Python dict."""
    result = {
        'primary_key': 'PRIMARY KEY' in constraints.upper(),
        'unique': 'UNIQUE' in constraints.upper(),
        'nullable': 'NOT NULL' not in constraints.upper(),
        'autoincrement': 'AUTO INCREMENT' in constraints.upper(),
        'default': None,
        'foreign_key': None
    }

    # Extract default value
    default_match = re.search(r'DEFAULT\s+(.+?)(?:,|$)', constraints, re.IGNORECASE)
    if default_match:
        result['default'] = default_match.group(1).strip()

    # Extract foreign key
    fk_match = re.search(r'FOREIGN KEY.*?REFERENCES\s+(\w+)\((\w+)\)', constraints, re.IGNORECASE)
    if fk_match:
        result['foreign_key'] = (fk_match.group(1), fk_match.group(2))

    return result


def generate_sqlalchemy_model(entity: dict) -> str:
    """Generate SQLAlchemy model class code."""
    class_name = entity['name']
    table_name = class_name.lower()

    # Start class definition
    code = f'''class {class_name}(Base):
    """
    {entity['purpose']}
    """
    __tablename__ = '{table_name}'

'''

    # Generate columns
    for field in entity['fields']:
        field_name = field['name']
        sql_type = field['type']
        sa_type = map_sql_type_to_sqlalchemy(sql_type)
        constraints = parse_constraints(field['constraints'])

        # Build column definition
        col_parts = [f"Column({sa_type}"]

        if constraints['primary_key']:
            col_parts.append("primary_key=True")
        if not constraints['nullable']:
            col_parts.append("nullable=False")
        if constraints['unique']:
            col_parts.append("unique=True")
        if constraints['autoincrement']:
            col_parts.append("autoincrement=True")
        if constraints['default']:
            default_val = constraints['default']
            if default_val.upper() == 'NOW()':
                col_parts.append("server_default=func.now()")
            elif default_val.upper() == 'GEN_RANDOM_UUID()':
                col_parts.append("server_default=text('gen_random_uuid()')")
            else:
                col_parts.append(f"default={repr(default_val)}")
        if constraints['foreign_key']:
            fk_table, fk_col = constraints['foreign_key']
            col_parts.append(f"ForeignKey('{fk_table.lower()}.{fk_col}')")

        col_def = ", ".join(col_parts) + ")"

        code += f"    {field_name} = {col_def}\n"

    code += "\n"
    return code


def generate_models_file(entities: list[dict], output_path: str):
    """Generate complete models.py file."""
    header = '''"""
SQLAlchemy ORM models for EmberLearn database.

Auto-generated from data-model.md specification.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, Numeric, String, Text, func, text
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


'''

    # Generate all model classes
    models_code = header
    for entity in entities:
        models_code += generate_sqlalchemy_model(entity) + "\n"

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(models_code)

    return len(entities)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_models.py <data-model.md path>")
        sys.exit(1)

    data_model_path = sys.argv[1]

    if not os.path.exists(data_model_path):
        print(f"Error: {data_model_path} not found")
        sys.exit(1)

    # Parse data model
    entities = parse_data_model(data_model_path)

    # Generate models.py
    output_path = "backend/database/models.py"
    num_models = generate_models_file(entities, output_path)

    print(f"✓ Generated {num_models} models in {output_path}")


if __name__ == "__main__":
    main()
