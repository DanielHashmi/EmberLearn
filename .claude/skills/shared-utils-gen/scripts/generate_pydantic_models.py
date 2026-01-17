#!/usr/bin/env python3
"""Generate Pydantic models from OpenAPI contract specifications."""

import os
import yaml
from typing import Dict, Any


def parse_openapi_schema(contract_path: str) -> Dict[str, Any]:
    """Parse OpenAPI YAML file and extract schemas."""
    with open(contract_path, 'r') as f:
        spec = yaml.safe_load(f)

    return spec.get('components', {}).get('schemas', {})


def map_openapi_type_to_python(openapi_type: str, format: str = None) -> str:
    """Map OpenAPI types to Python/Pydantic types."""
    type_map = {
        'string': 'str',
        'integer': 'int',
        'number': 'float',
        'boolean': 'bool',
        'array': 'list',
        'object': 'dict',
    }

    if format == 'uuid':
        return 'UUID'
    elif format == 'date-time':
        return 'datetime'

    return type_map.get(openapi_type, 'Any')


def generate_pydantic_model(model_name: str, schema: Dict[str, Any]) -> str:
    """Generate Pydantic model class from OpenAPI schema."""
    required_fields = schema.get('required', [])
    properties = schema.get('properties', {})

    code = f"class {model_name}(BaseModel):\n"

    # Add docstring if description exists
    if 'description' in schema:
        code += f'    """{schema["description"]}"""\n'

    # Generate fields
    for field_name, field_spec in properties.items():
        field_type = map_openapi_type_to_python(
            field_spec.get('type', 'string'),
            field_spec.get('format')
        )

        # Handle arrays
        if field_spec.get('type') == 'array':
            items_type = map_openapi_type_to_python(
                field_spec.get('items', {}).get('type', 'str')
            )
            field_type = f'list[{items_type}]'

        # Handle optional fields
        if field_name not in required_fields:
            field_type = f'Optional[{field_type}]'
            default = ' = None'
        else:
            default = ''

        # Add field description as comment
        description = field_spec.get('description', '')
        comment = f'  # {description}' if description else ''

        # Add example if present
        example = field_spec.get('example')
        if example and not description:
            comment = f'  # Example: {example}'

        code += f"    {field_name}: {field_type}{default}{comment}\n"

    code += "\n"
    return code


def generate_models_file(schemas: Dict[str, Any], output_path: str):
    """Generate complete models.py file with all Pydantic models."""
    header = '''"""
Pydantic models for API request/response validation.

Auto-generated from OpenAPI contract specifications.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


'''

    models_code = header

    # Generate all models
    for model_name, schema in schemas.items():
        models_code += generate_pydantic_model(model_name, schema)

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(models_code)

    return len(schemas)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_pydantic_models.py <contracts-dir>")
        print("Example: python generate_pydantic_models.py specs/001-hackathon-iii/contracts")
        sys.exit(1)

    contracts_dir = sys.argv[1]
    agent_api_path = os.path.join(contracts_dir, "agent-api.yaml")

    if not os.path.exists(agent_api_path):
        print(f"Error: {agent_api_path} not found")
        sys.exit(1)

    # Parse OpenAPI spec
    schemas = parse_openapi_schema(agent_api_path)

    # Generate Pydantic models
    output_path = "backend/shared/models.py"
    num_models = generate_models_file(schemas, output_path)

    print(f"✓ Generated {num_models} Pydantic models in {output_path}")


if __name__ == "__main__":
    main()
