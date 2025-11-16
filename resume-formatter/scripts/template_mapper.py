#!/usr/bin/env python3
"""
Template Mapper - Map extracted content to target template

Maps extracted resume content to a target template while preserving quality.

Usage:
    python template_mapper.py <parsed.json> <template.docx> [--output mapped.docx]
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any

try:
    from docx import Document
except ImportError:
    print("Error: python-docx not installed. Run: pip install python-docx")
    exit(1)


class TemplateMapper:
    """Map extracted content to template"""

    # Field name mappings
    FIELD_MAPPINGS = {
        '성명': 'personal_info.name',
        'Name': 'personal_info.name',
        '이름': 'personal_info.name',
        '연락처': 'personal_info.contact',
        'Phone': 'personal_info.phone',
        '전화': 'personal_info.phone',
        'Email': 'personal_info.email',
        '주소': 'personal_info.address',
        'Address': 'personal_info.address',
        '경력사항': 'experience',
        'Experience': 'experience',
        '학력사항': 'education',
        'Education': 'education',
        '핵심역량': 'skills.technical',
        'Skills': 'skills.technical',
    }

    def __init__(self, extracted_data: Dict[str, Any], template_path: str):
        self.data = extracted_data
        self.template_path = Path(template_path)
        self.doc = Document(str(self.template_path))

    def map(self, output_path: str):
        """Map content to template and save"""
        print(f"Mapping content to template: {self.template_path.name}")

        # Process tables (common in Korean templates)
        if self.doc.tables:
            self._map_tables()

        # Process paragraphs
        self._map_paragraphs()

        # Save
        self.doc.save(output_path)
        print(f"Saved mapped resume to: {output_path}")

    def _map_tables(self):
        """Map content to table-based template"""
        for table in self.doc.tables:
            for row in table.rows:
                if len(row.cells) < 2:
                    continue

                field_name = row.cells[0].text.strip()
                field_path = self._resolve_field_path(field_name)

                if field_path:
                    value = self._get_value(field_path)
                    if value:
                        row.cells[1].text = str(value)
                        print(f"  Mapped: {field_name} -> {value}")

    def _map_paragraphs(self):
        """Map content to paragraph-based template"""
        # Placeholder for paragraph-based templates
        # Would detect placeholder text and replace with actual content
        pass

    def _resolve_field_path(self, field_name: str) -> str:
        """Resolve field name to data path"""
        # Exact match
        if field_name in self.FIELD_MAPPINGS:
            return self.FIELD_MAPPINGS[field_name]

        # Partial match
        for key, path in self.FIELD_MAPPINGS.items():
            if key.lower() in field_name.lower():
                return path

        return None

    def _get_value(self, field_path: str) -> Any:
        """Get value from extracted data by path"""
        parts = field_path.split('.')
        value = self.data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

            if value is None:
                return None

        # Handle different value types
        if isinstance(value, dict) and 'value' in value:
            return value['value']
        elif isinstance(value, list) and value:
            # For experience/education, format list
            return self._format_list(value, field_path)
        else:
            return value

    def _format_list(self, items: list, field_path: str) -> str:
        """Format list items for display"""
        if 'experience' in field_path:
            # Format experience entries
            result = []
            for exp in items[:3]:  # Limit to top 3
                company = exp.get('company', 'Unknown Company')
                title = exp.get('title', 'Position')
                dates = f"{exp.get('start_date', '')} ~ {exp.get('end_date', '')}"
                result.append(f"{dates} {company} / {title}")
            return '\n'.join(result)
        elif 'skills' in field_path:
            # Format skills
            skills = [s.get('value', s) if isinstance(s, dict) else s for s in items]
            return ', '.join(skills[:10])  # Top 10 skills
        else:
            return ', '.join(str(item) for item in items)


def main():
    parser = argparse.ArgumentParser(description='Map extracted content to template')
    parser.add_argument('extracted_json', help='Path to parsed resume JSON')
    parser.add_argument('template', help='Path to template file (.docx)')
    parser.add_argument('--output', '-o', help='Output file', required=True)
    args = parser.parse_args()

    # Load extracted data
    with open(args.extracted_json, 'r', encoding='utf-8') as f:
        extracted = json.load(f)

    # Map to template
    mapper = TemplateMapper(extracted, args.template)
    mapper.map(args.output)


if __name__ == '__main__':
    main()
