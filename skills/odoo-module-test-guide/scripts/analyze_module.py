#!/usr/bin/env python3
"""
Odoo Module Analyzer

Analyzes an Odoo module structure and extracts information for generating
testing guides. Outputs structured JSON with module metadata, models,
views, wizards, cron jobs, and security configuration.

Usage:
    python analyze_module.py /path/to/odoo/module [--output output.json]
"""

import argparse
import ast
import csv
import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def parse_manifest(module_path: Path) -> dict:
    """Parse __manifest__.py and extract module metadata."""
    manifest_path = module_path / "__manifest__.py"
    if not manifest_path.exists():
        return {}

    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Dict):
                return ast.literal_eval(content)
    except (SyntaxError, ValueError):
        pass

    return {}


def extract_models_from_file(file_path: Path) -> list:
    """Extract model definitions from a Python file."""
    models = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return models

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            model_info = {
                "class_name": node.name,
                "file": str(file_path.name),
                "line": node.lineno,
                "model_name": None,
                "inherit": [],
                "description": None,
                "fields": [],
                "methods": [],
                "is_transient": False,
            }

            # Check base classes
            for base in node.bases:
                if isinstance(base, ast.Attribute):
                    base_name = f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr
                    if "TransientModel" in base_name:
                        model_info["is_transient"] = True

            # Extract class body
            for item in node.body:
                # _name assignment
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "_name" and isinstance(item.value, ast.Constant):
                                model_info["model_name"] = item.value.value
                            elif target.id == "_inherit":
                                if isinstance(item.value, ast.Constant):
                                    model_info["inherit"] = [item.value.value]
                                elif isinstance(item.value, ast.List):
                                    model_info["inherit"] = [
                                        e.value for e in item.value.elts if isinstance(e, ast.Constant)
                                    ]
                            elif target.id == "_description" and isinstance(item.value, ast.Constant):
                                model_info["description"] = item.value.value

                # Field definitions
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and isinstance(item.value, ast.Call):
                            if isinstance(item.value.func, ast.Attribute):
                                func_name = item.value.func.attr
                                if func_name in [
                                    "Char", "Text", "Integer", "Float", "Boolean",
                                    "Date", "Datetime", "Binary", "Html", "Selection",
                                    "Many2one", "One2many", "Many2many", "Monetary",
                                ]:
                                    field_info = {
                                        "name": target.id,
                                        "type": func_name,
                                        "line": item.lineno,
                                    }
                                    # Extract field attributes
                                    for kw in item.value.keywords:
                                        if kw.arg in ["string", "help", "comodel_name", "inverse_name", "related"]:
                                            if isinstance(kw.value, ast.Constant):
                                                field_info[kw.arg] = kw.value.value
                                        elif kw.arg in ["compute", "store", "readonly", "required"]:
                                            if isinstance(kw.value, ast.Constant):
                                                field_info[kw.arg] = kw.value.value
                                            elif isinstance(kw.value, ast.Name):
                                                field_info[kw.arg] = kw.value.id == "True"

                                    # For relational fields, get comodel from first positional arg
                                    if func_name in ["Many2one", "One2many", "Many2many"] and item.value.args:
                                        if isinstance(item.value.args[0], ast.Constant):
                                            field_info["comodel_name"] = item.value.args[0].value

                                    model_info["fields"].append(field_info)

                # Method definitions
                if isinstance(item, ast.FunctionDef):
                    decorators = []
                    for dec in item.decorator_list:
                        if isinstance(dec, ast.Attribute):
                            decorators.append(f"@api.{dec.attr}")
                        elif isinstance(dec, ast.Name):
                            decorators.append(f"@{dec.id}")

                    # Get docstring
                    docstring = ast.get_docstring(item)

                    method_info = {
                        "name": item.name,
                        "line": item.lineno,
                        "decorators": decorators,
                        "docstring": docstring[:200] if docstring else None,
                        "is_public": not item.name.startswith("_") or item.name.startswith("__"),
                    }
                    model_info["methods"].append(method_info)

            # Only add if it looks like an Odoo model
            if model_info["model_name"] or model_info["inherit"]:
                models.append(model_info)

    return models


def analyze_models_directory(module_path: Path) -> list:
    """Analyze all Python files in models/ directory."""
    models_dir = module_path / "models"
    all_models = []

    if models_dir.exists():
        for py_file in models_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                all_models.extend(extract_models_from_file(py_file))

    return all_models


def analyze_wizards_directory(module_path: Path) -> list:
    """Analyze all Python files in wizard/ directory."""
    wizard_dir = module_path / "wizard"
    wizards = []

    if wizard_dir.exists():
        for py_file in wizard_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                models = extract_models_from_file(py_file)
                for model in models:
                    model["is_wizard"] = True
                wizards.extend(models)

    return wizards


def parse_xml_files(directory: Path) -> list:
    """Parse XML files and extract records, menus, and actions."""
    results = []

    if not directory.exists():
        return results

    for xml_file in directory.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            file_info = {
                "file": xml_file.name,
                "records": [],
                "menus": [],
                "actions": [],
                "views": [],
                "crons": [],
            }

            # Handle both <odoo> and <openerp> root elements
            data_elements = root.findall(".//record") + root.findall(".//menuitem")

            for record in root.iter("record"):
                record_info = {
                    "id": record.get("id"),
                    "model": record.get("model"),
                }

                # Extract specific fields based on model type
                if record.get("model") == "ir.ui.view":
                    name_field = record.find(".//field[@name='name']")
                    model_field = record.find(".//field[@name='model']")
                    inherit_field = record.find(".//field[@name='inherit_id']")

                    view_info = {
                        "id": record.get("id"),
                        "name": name_field.text if name_field is not None else None,
                        "model": model_field.text if model_field is not None else None,
                        "inherits": inherit_field.get("ref") if inherit_field is not None else None,
                    }
                    file_info["views"].append(view_info)

                elif record.get("model") == "ir.actions.act_window":
                    name_field = record.find(".//field[@name='name']")
                    res_model = record.find(".//field[@name='res_model']")

                    action_info = {
                        "id": record.get("id"),
                        "name": name_field.text if name_field is not None else None,
                        "res_model": res_model.text if res_model is not None else None,
                    }
                    file_info["actions"].append(action_info)

                elif record.get("model") == "ir.cron":
                    name_field = record.find(".//field[@name='name']")
                    model_field = record.find(".//field[@name='model_id']")
                    code_field = record.find(".//field[@name='code']")
                    interval_field = record.find(".//field[@name='interval_number']")
                    interval_type = record.find(".//field[@name='interval_type']")

                    cron_info = {
                        "id": record.get("id"),
                        "name": name_field.text if name_field is not None else None,
                        "code": code_field.text if code_field is not None else None,
                        "interval": f"{interval_field.text if interval_field is not None else '?'} {interval_type.text if interval_type is not None else '?'}",
                    }
                    file_info["crons"].append(cron_info)

                else:
                    file_info["records"].append(record_info)

            # Handle menuitem elements
            for menu in root.iter("menuitem"):
                menu_info = {
                    "id": menu.get("id"),
                    "name": menu.get("name"),
                    "parent": menu.get("parent"),
                    "action": menu.get("action"),
                    "sequence": menu.get("sequence"),
                    "groups": menu.get("groups"),
                }
                file_info["menus"].append(menu_info)

            results.append(file_info)

        except ET.ParseError:
            results.append({"file": xml_file.name, "error": "XML parse error"})

    return results


def analyze_security(module_path: Path) -> dict:
    """Analyze security/ir.model.access.csv."""
    security_dir = module_path / "security"
    access_file = security_dir / "ir.model.access.csv"
    security_info = {"access_rules": [], "groups": []}

    if access_file.exists():
        with open(access_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                security_info["access_rules"].append(dict(row))

    # Check for security rules XML
    if security_dir.exists():
        for xml_file in security_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                for record in tree.iter("record"):
                    if record.get("model") in ["ir.rule", "res.groups"]:
                        security_info["groups"].append({
                            "id": record.get("id"),
                            "model": record.get("model"),
                        })
            except ET.ParseError:
                pass

    return security_info


def analyze_tests(module_path: Path) -> dict:
    """Analyze tests/ directory structure."""
    tests_dir = module_path / "tests"
    test_info = {"test_files": [], "test_classes": [], "test_methods": []}

    if not tests_dir.exists():
        return test_info

    for py_file in tests_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            test_info["test_files"].append(py_file.name)

            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        test_info["test_classes"].append({
                            "name": node.name,
                            "file": py_file.name,
                        })
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                                docstring = ast.get_docstring(item)
                                test_info["test_methods"].append({
                                    "name": item.name,
                                    "class": node.name,
                                    "docstring": docstring[:100] if docstring else None,
                                })
            except SyntaxError:
                pass

    return test_info


def get_directory_structure(module_path: Path) -> dict:
    """Get the directory structure of the module."""
    structure = {"directories": [], "files": []}

    for item in sorted(module_path.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            structure["directories"].append(item.name)
        else:
            structure["files"].append(item.name)

    return structure


def analyze_module(module_path: str) -> dict:
    """Main function to analyze an Odoo module."""
    path = Path(module_path).resolve()

    if not path.exists():
        return {"error": f"Module path does not exist: {module_path}"}

    if not (path / "__manifest__.py").exists():
        return {"error": f"Not a valid Odoo module (missing __manifest__.py): {module_path}"}

    result = {
        "module_path": str(path),
        "module_name": path.name,
        "manifest": parse_manifest(path),
        "structure": get_directory_structure(path),
        "models": analyze_models_directory(path),
        "wizards": analyze_wizards_directory(path),
        "views": parse_xml_files(path / "views"),
        "data": parse_xml_files(path / "data"),
        "security": analyze_security(path),
        "tests": analyze_tests(path),
    }

    # Summary statistics
    result["summary"] = {
        "total_models": len(result["models"]),
        "total_wizards": len(result["wizards"]),
        "total_fields": sum(len(m["fields"]) for m in result["models"]),
        "total_methods": sum(len(m["methods"]) for m in result["models"]),
        "total_views": sum(len(v["views"]) for v in result["views"]),
        "total_menus": sum(len(v["menus"]) for v in result["views"]),
        "total_crons": sum(len(d["crons"]) for d in result["data"]),
        "total_tests": len(result["tests"]["test_methods"]),
        "has_config_settings": any(
            "res.config.settings" in (m.get("inherit") or []) for m in result["models"]
        ),
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Analyze an Odoo module and extract structural information."
    )
    parser.add_argument("module_path", help="Path to the Odoo module directory")
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: stdout)",
        default=None
    )
    parser.add_argument(
        "--pretty", "-p",
        help="Pretty print JSON output",
        action="store_true"
    )

    args = parser.parse_args()

    result = analyze_module(args.module_path)

    indent = 2 if args.pretty else None
    json_output = json.dumps(result, indent=indent, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
