#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JSON_MODE=false
SCAN_ROOT="$SCRIPT_DIR"

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        *)      SCAN_ROOT="$arg" ;;
    esac
done

if [[ "$JSON_MODE" == false ]]; then
    RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'
    BOLD='\033[1m'; RESET='\033[0m'
else
    RED=''; YELLOW=''; CYAN=''; BOLD=''; RESET=''
fi

check_stub() {
    local file="$1"
    python3 - "$file" <<'PYEOF'
import sys, ast

path = sys.argv[1]
try:
    tree = ast.parse(open(path).read())
except Exception:
    sys.exit(0)

functions = [
    n for n in ast.walk(tree)
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
]
if not functions:
    sys.exit(0)

def body_is_stub(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    if not body:
        return True
    for stmt in body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is ...:
            continue
        if isinstance(stmt, ast.Raise):
            exc = stmt.exc
            if exc and isinstance(exc, ast.Call):
                name = getattr(exc.func, 'id', None) or getattr(exc.func, 'attr', None)
                if name == 'NotImplementedError':
                    continue
        return False
    return True

all_stubs = all(body_is_stub(list(fn.body)) for fn in functions)
if all_stubs:
    print("STUB")
PYEOF
}

EMPTY_FILES=()
STUB_FILES=()
INIT_ONLY=()

SKIP_DIRS=(".git" "__pycache__" ".buildozer" "build" "dist" "bin" ".eggs" "*.egg-info")

PRUNE_EXPR=()
for d in "${SKIP_DIRS[@]}"; do
    PRUNE_EXPR+=(-name "$d" -o)
done
unset 'PRUNE_EXPR[${#PRUNE_EXPR[@]}-1]'

while IFS= read -r file; do
    rel="${file#$SCAN_ROOT/}"

    ml=$(grep -Evc '^\s*(#.*)?$' "$file" || true)

    if [[ "$ml" -eq 0 ]]; then
        EMPTY_FILES+=("$rel")
        continue
    fi

    if [[ "$(basename "$file")" == "__init__.py" && "$ml" -le 3 ]]; then
        INIT_ONLY+=("$rel")
        continue
    fi

    result=$(check_stub "$file")
    if [[ "$result" == "STUB" ]]; then
        STUB_FILES+=("$rel")
    fi

done < <(
    find "$SCAN_ROOT" \
        \( "${PRUNE_EXPR[@]}" \) -prune \
        -o -name "*.py" -print
)

if [[ "$JSON_MODE" == true ]]; then
    python3 - \
        "${EMPTY_FILES[@]+"${EMPTY_FILES[@]}"}" \
        "---stub---" \
        "${STUB_FILES[@]+"${STUB_FILES[@]}"}" \
        "---init---" \
        "${INIT_ONLY[@]+"${INIT_ONLY[@]}"}" \
        <<'PYEOF'
import sys, json

args = sys.argv[1:]
empty, stubs, inits = [], [], []
target = empty
for a in args:
    if a == "---stub---":   target = stubs;  continue
    if a == "---init---":   target = inits;  continue
    target.append(a)

print(json.dumps({"empty": empty, "stub": stubs, "init_only": inits}, indent=2))
PYEOF
    exit 0
fi

echo -e "\n${BOLD}FieldSnek stub / empty file report${RESET}"
echo -e "Scanned: ${CYAN}${SCAN_ROOT}${RESET}\n"

total=$(( ${#EMPTY_FILES[@]} + ${#STUB_FILES[@]} + ${#INIT_ONLY[@]} ))

if [[ "${#EMPTY_FILES[@]}" -gt 0 ]]; then
    echo -e "${RED}${BOLD}⬜ Empty files (${#EMPTY_FILES[@]})${RESET}"
    for f in "${EMPTY_FILES[@]}"; do echo -e "   ${RED}${RESET}  $f"; done
    echo
fi

if [[ "${#STUB_FILES[@]}" -gt 0 ]]; then
    echo -e "${YELLOW}${BOLD} Stub files (${#STUB_FILES[@]})${RESET}"
    for f in "${STUB_FILES[@]}"; do echo -e "   ${YELLOW}~${RESET}  $f"; done
    echo
fi

if [[ "${#INIT_ONLY[@]}" -gt 0 ]]; then
    echo -e "${CYAN}${BOLD} Bare __init__.py (${#INIT_ONLY[@]})${RESET}"
    for f in "${INIT_ONLY[@]}"; do echo -e "   ${CYAN}·${RESET}  $f"; done
    echo
fi

if [[ "$total" -eq 0 ]]; then
    echo -e "    No empty or stub files found."
else
    echo -e "${BOLD}Total flagged: $total${RESET}"
fi
echo
