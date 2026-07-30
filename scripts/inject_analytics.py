#!/usr/bin/env python3
"""Inject Vercel Web Analytics script into all HTML files."""

from __future__ import annotations

import pathlib
import sys


def inject_analytics(html_path: pathlib.Path) -> bool:
    """
    Inject Vercel Analytics script into an HTML file.
    
    Returns True if the file was modified, False otherwise.
    """
    content = html_path.read_text(errors="ignore")
    
    # Check if analytics already injected
    if "/_vercel/insights/script.js" in content or "window.va" in content:
        return False
    
    # The Vercel Analytics script for vanilla JavaScript/HTML
    analytics_script = """<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
"""
    
    # Find the closing head tag and inject before it
    if "</head>" in content:
        content = content.replace("</head>", f"{analytics_script}</head>", 1)
        html_path.write_text(content)
        return True
    
    return False


def main() -> None:
    """Inject Vercel Analytics into all HTML files in public directory."""
    project_root = pathlib.Path(__file__).resolve().parents[1]
    public_dir = project_root / "public"
    
    if not public_dir.exists():
        print(f"ERROR: public directory not found at {public_dir}", file=sys.stderr)
        sys.exit(1)
    
    html_files = sorted(public_dir.rglob("*.html"))
    if not html_files:
        print("WARNING: No HTML files found in public directory", file=sys.stderr)
        sys.exit(0)
    
    modified_count = 0
    for html_file in html_files:
        if inject_analytics(html_file):
            modified_count += 1
    
    print(f"VERCEL ANALYTICS: Injected analytics script into {modified_count} of {len(html_files)} HTML files")


if __name__ == "__main__":
    main()
