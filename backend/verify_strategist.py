import sys
import os
from dotenv import load_dotenv, find_dotenv

with open("debug.log", "w") as f:
    f.write(f"CWD: {os.getcwd()}\n")
    f.write(f".env found: {find_dotenv()}\n")
    loaded = load_dotenv(verbose=True) 
    f.write(f"Dotenv loaded: {loaded}\n")
    f.write(f"ARK_API_KEY in env: {os.environ.get('ARK_API_KEY')}\n")

# Add backend to path to allow imports
sys.path.append(os.getcwd())

try:
    from app.agents.strategist import strategist_agent
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Other Error during import: {e}")
    sys.exit(1)

# Mock state
state = {
    "raw_input": "Test input",
    "mode": "mimeng",
    "api_config": {},
    "references": []
}

try:
    result = strategist_agent(state)
    with open("debug.log", "a") as f:
        f.write(f"\nResult: {result}\n")
except Exception as e:
    with open("debug.log", "a") as f:
        f.write(f"\nRuntime Error: {e}\n")
