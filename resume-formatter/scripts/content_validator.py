#!/usr/bin/env python3
"""
Content Validator - Validate resume transformation quality

Compares source and target to ensure completeness and quality.

Usage:
    python content_validator.py <source_parsed.json> <target_resume.docx>
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

try:
    from docx import Document
except ImportError:
    print("Error: python-docx not installed. Run: pip install python-docx")
    exit(1)


class ContentValidator:
    """Validate resume transformation"""

    def __init__(self, source_data: Dict[str, Any], target_path: str):
        self.source = source_data
        self.target_path = Path(target_path)
        self.target_doc = Document(str(self.target_path))
        self.target_text = self._extract_target_text()
        self.issues = []

    def validate(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print(f"Validating: {self.target_path.name}")

        report = {
            'overall_score': 0.0,
            'completeness': {},
            'issues': [],
            'recommendations': []
        }

        # Check completeness
        report['completeness'] = self._check_completeness()

        # Check quality
        self._check_quality()

        # Calculate overall score
        scores = list(report['completeness'].values())
        report['overall_score'] = sum(scores) / len(scores) if scores else 0.0

        # Add issues and recommendations
        report['issues'] = self.issues

        return report

    def _extract_target_text(self) -> str:
        """Extract all text from target document"""
        paragraphs = [p.text for p in self.target_doc.paragraphs]
        tables = []
        for table in self.target_doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    tables.append(cell.text)

        return '\n'.join(paragraphs + tables)

    def _check_completeness(self) -> Dict[str, float]:
        """Check if all source content is in target"""
        completeness = {}

        # Personal info
        personal_fields = ['name', 'phone', 'email']
        personal_found = 0
        for field in personal_fields:
            value = self.source.get('personal_info', {}).get(field, {})
            if isinstance(value, dict):
                value = value.get('value', '')
            if value and value in self.target_text:
                personal_found += 1
            elif value:
                self.issues.append(f"Personal info '{field}' not found in target: {value}")

        completeness['personal_info'] = personal_found / len(personal_fields) if personal_fields else 0.0

        # Experience
        exp_count = len(self.source.get('experience', []))
        exp_found = 0
        for exp in self.source.get('experience', []):
            company = exp.get('company', '')
            if company and company in self.target_text:
                exp_found += 1
            elif company:
                self.issues.append(f"Experience company not found: {company}")

        completeness['experience'] = exp_found / exp_count if exp_count > 0 else 1.0

        # Education
        edu_count = len(self.source.get('education', []))
        edu_found = 0
        for edu in self.source.get('education', []):
            school = edu.get('school', '')
            if school and school in self.target_text:
                edu_found += 1

        completeness['education'] = edu_found / edu_count if edu_count > 0 else 0.8

        # Skills
        skills = self.source.get('skills', {}).get('technical', [])
        skill_found = 0
        for skill in skills[:10]:  # Check top 10
            value = skill.get('value', skill) if isinstance(skill, dict) else skill
            if value and value in self.target_text:
                skill_found += 1

        completeness['skills'] = skill_found / min(len(skills), 10) if skills else 0.8

        return completeness

    def _check_quality(self):
        """Check content quality"""
        # Check for placeholder text still remaining
        placeholders = ['OOO', 'XXX', '[Insert', '정보 없음', 'N/A']
        for placeholder in placeholders:
            if placeholder in self.target_text:
                self.issues.append(f"Placeholder text found: {placeholder}")

        # Check for encoding issues (garbled Korean text)
        if '�' in self.target_text:
            self.issues.append("Encoding issues detected (garbled characters)")

    def print_report(self, report: Dict[str, Any]):
        """Print validation report"""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)

        print(f"\nOverall Completeness: {report['overall_score']:.1%}")

        print("\nSection Completeness:")
        for section, score in report['completeness'].items():
            status = "✓" if score >= 0.9 else "⚠" if score >= 0.7 else "✗"
            print(f"  {status} {section}: {score:.1%}")

        if report['issues']:
            print(f"\nIssues Found ({len(report['issues'])}):")
            for issue in report['issues']:
                print(f"  ⚠ {issue}")
        else:
            print("\n✓ No issues found!")

        # Recommendations
        if report['overall_score'] < 0.9:
            print("\nRecommendations:")
            print("  - Review flagged missing content above")
            print("  - Verify critical fields (name, contact) are correct")
            print("  - Check for any truncated text")


def main():
    parser = argparse.ArgumentParser(description='Validate resume transformation')
    parser.add_argument('source_json', help='Path to source parsed JSON')
    parser.add_argument('target_resume', help='Path to target resume (.docx)')
    parser.add_argument('--output', '-o', help='Output JSON report', default=None)
    args = parser.parse_args()

    # Load source data
    with open(args.source_json, 'r', encoding='utf-8') as f:
        source = json.load(f)

    # Validate
    validator = ContentValidator(source, args.target_resume)
    report = validator.validate()

    # Print report
    validator.print_report(report)

    # Save if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nReport saved to: {args.output}")


if __name__ == '__main__':
    main()
