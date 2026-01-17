#!/usr/bin/env python3
"""
Verify generated Next.js application structure and quality.
"""

import sys
from pathlib import Path
from typing import List, Tuple

def check_file_exists(path: Path, description: str) -> Tuple[bool, str]:
    """Check if a file exists."""
    if path.exists():
        return True, f"✓ {description}: {path}"
    else:
        return False, f"✗ {description} missing: {path}"

def verify_structure(app_dir: Path) -> List[Tuple[bool, str]]:
    """Verify the generated application structure."""
    checks = [
        # Configuration files
        (app_dir / "package.json", "package.json"),
        (app_dir / "tsconfig.json", "TypeScript config"),
        (app_dir / "tailwind.config.ts", "Tailwind config"),
        (app_dir / "postcss.config.js", "PostCSS config"),
        (app_dir / "next.config.js", "Next.js config"),

        # App directory
        (app_dir / "app" / "layout.tsx", "Root layout"),
        (app_dir / "app" / "page.tsx", "Landing page"),
        (app_dir / "app" / "globals.css", "Global styles"),

        # Library files
        (app_dir / "lib" / "design-tokens.ts", "Design tokens"),
        (app_dir / "lib" / "animation-presets.ts", "Animation presets"),
        (app_dir / "lib" / "utils.ts", "Utility functions"),
    ]

    results = []
    for path, description in checks:
        results.append(check_file_exists(path, description))

    return results

def verify_design_tokens(app_dir: Path) -> Tuple[bool, str]:
    """Verify design tokens are properly imported."""
    tokens_path = app_dir / "lib" / "design-tokens.ts"

    if not tokens_path.exists():
        return False, "✗ Design tokens file not found"

    content = tokens_path.read_text()

    # Check for required sections
    required = ["colors", "typography", "spacing", "borderRadius", "shadows"]
    missing = [s for s in required if s not in content]

    if missing:
        return False, f"✗ Design tokens missing sections: {', '.join(missing)}"

    return True, "✓ Design tokens complete"

def verify_typescript(app_dir: Path) -> Tuple[bool, str]:
    """Verify TypeScript configuration."""
    tsconfig_path = app_dir / "tsconfig.json"

    if not tsconfig_path.exists():
        return False, "✗ tsconfig.json not found"

    import json
    with open(tsconfig_path, 'r') as f:
        config = json.load(f)

    # Check strict mode
    if not config.get("compilerOptions", {}).get("strict"):
        return False, "✗ TypeScript strict mode not enabled"

    return True, "✓ TypeScript configured correctly"

def main():
    """Run all verification checks."""
    if len(sys.argv) < 2:
        print("Usage: python3 verify_generation.py <app_directory>")
        sys.exit(1)

    app_dir = Path(sys.argv[1])

    if not app_dir.exists():
        print(f"✗ Directory not found: {app_dir}")
        sys.exit(1)

    print(f"Verifying generated application: {app_dir}\n")

    # Run structure checks
    print("Checking file structure...")
    structure_results = verify_structure(app_dir)
    for success, message in structure_results:
        print(message)

    print("\nChecking design tokens...")
    tokens_success, tokens_message = verify_design_tokens(app_dir)
    print(tokens_message)

    print("\nChecking TypeScript configuration...")
    ts_success, ts_message = verify_typescript(app_dir)
    print(ts_message)

    # Summary
    print("\n" + "="*60)

    all_checks = structure_results + [(tokens_success, tokens_message), (ts_success, ts_message)]
    passed = sum(1 for success, _ in all_checks if success)
    total = len(all_checks)

    if passed == total:
        print(f"✓ All checks passed ({passed}/{total})")
        print("\nApplication ready for development!")
        print("Run: npm install && npm run dev")
        sys.exit(0)
    else:
        print(f"✗ Some checks failed ({passed}/{total} passed)")
        sys.exit(1)

if __name__ == "__main__":
    main()
