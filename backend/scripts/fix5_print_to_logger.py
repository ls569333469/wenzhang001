"""Fix-5: Batch replace print() → logger in backend services"""
import re
import sys
from pathlib import Path

# Files to process and their existing logger status
FILES = {
    "app/services/google_sheets_source.py": {
        "has_logger": False,
        "logger_name": "google_sheets",
        "import_line": "from app.core.config import get_logger",
        "add_after": "Credentials = None",
        "logger_init": 'logger = get_logger("google_sheets")',
    },
    "app/services/material_sheet.py": {
        "has_logger": False,
        "logger_name": "material_sheet",
        "import_line": "from app.core.config import get_logger",
        "logger_init": 'logger = get_logger("material_sheet")',
    },
    "app/services/material_fetcher/chaincatcher.py": {
        "has_logger": False,
        "logger_name": "chaincatcher",
        "import_line": "from app.core.config import get_logger",
        "logger_init": 'logger = get_logger("chaincatcher")',
    },
    "app/services/material_analyzer.py": {
        "has_logger": False,
        "logger_name": "material_analyzer",
        "import_line": "from app.core.config import get_logger",
        "logger_init": 'logger = get_logger("material_analyzer")',
    },
    "app/core/llm.py": {
        "has_logger": True,  # Already has logger
    },
    "app/core/config.py": {
        "has_logger": False,  # Uses print inline, special case
        "skip": True,
    },
}

BASE = Path(__file__).parent.parent

def classify_print(line: str) -> str:
    """Determine log level based on print content"""
    stripped = line.strip()
    lower = stripped.lower()
    if "error" in lower or "fail" in lower or "exception" in lower:
        return "error"
    elif "warn" in lower or "异常" in lower:
        return "warning"
    elif "debug" in lower or "DEBUG" in stripped:
        return "debug"
    else:
        return "info"

def convert_print_to_logger(line: str, indent: str) -> str:
    """Convert a print() line to logger call"""
    # Extract content from print(...)
    match = re.match(r'^(\s*)print\((.+)\)\s*$', line.rstrip())
    if not match:
        return line
    
    indent = match.group(1)
    content = match.group(2)
    level = classify_print(line)
    
    # Handle f-strings: print(f"...") → logger.info(...)
    if content.startswith('f"') or content.startswith("f'"):
        return f'{indent}logger.{level}({content})\n'
    
    # Handle regular strings: print("...") → logger.info("...")
    return f'{indent}logger.{level}({content})\n'

def process_file(filepath: Path, config: dict) -> int:
    """Process a single file, return count of replacements"""
    if config.get("skip"):
        return 0
    
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    count = 0
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("print(") and stripped.endswith(")"):
            new_line = convert_print_to_logger(line + "\n", "")
            new_lines.append(new_line.rstrip("\n"))
            count += 1
        else:
            new_lines.append(line)
    
    if count > 0:
        # Add logger import if needed
        if not config.get("has_logger"):
            import_line = config.get("import_line", "from app.core.config import get_logger")
            logger_init = config.get("logger_init", f'logger = get_logger("{filepath.stem}")')
            
            # Find where to add import
            new_content = "\n".join(new_lines)
            
            # Check if import already exists
            if "get_logger" not in new_content:
                # Add import after last import line
                import_added = False
                final_lines = []
                last_import_idx = 0
                for i, l in enumerate(new_lines):
                    if l.strip().startswith("import ") or l.strip().startswith("from "):
                        last_import_idx = i
                
                for i, l in enumerate(new_lines):
                    final_lines.append(l)
                    if i == last_import_idx and not import_added:
                        final_lines.append(import_line)
                        final_lines.append("")
                        final_lines.append(logger_init)
                        import_added = True
                
                new_lines = final_lines
        
        filepath.write_text("\n".join(new_lines), encoding="utf-8")
    
    return count

# Process files with existing logger (llm.py)
def process_llm():
    """Special handling for llm.py - already has logger"""
    fp = BASE / "app" / "core" / "llm.py"
    content = fp.read_text(encoding="utf-8")
    # Replace [LLM DEBUG] prints with logger.debug
    content = re.sub(
        r'(\s+)print\(f"\[LLM DEBUG\](.*?)"\)',
        r'\1logger.debug(f"[LLM]\2")',
        content
    )
    # Replace [LLM ERROR] prints
    content = re.sub(
        r'(\s+)print\(f"\[LLM ERROR\](.*?)"\)',
        r'\1logger.error(f"[LLM]\2")',
        content
    )
    fp.write_text(content, encoding="utf-8")
    return content.count("logger.debug") + content.count("logger.error")

# Main
total = 0
for rel_path, config in FILES.items():
    fp = BASE / rel_path
    if not fp.exists():
        print(f"  ⚠️ {rel_path} not found, skipping")
        continue
    
    if rel_path == "app/core/llm.py":
        n = process_llm()
        print(f"  ✅ {rel_path}: {n} print→logger (special)")
        total += n
    else:
        n = process_file(fp, config)
        print(f"  ✅ {rel_path}: {n} print→logger")
        total += n

print(f"\n{'='*40}")
print(f"  Fix-5 完成: {total} 处 print() → logger")
print(f"{'='*40}")
