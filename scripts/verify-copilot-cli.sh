#!/bin/bash
# Verify GitHub Copilot CLI Implementation

echo "=========================================="
echo "GitHub Copilot CLI Implementation Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        return 1
    fi
}

count=0
total=0

echo -e "${BLUE}=== Custom Instructions ===${NC}"
total=$((total + 1))
check_file ".github/copilot-instructions.md" && count=$((count + 1))

echo ""
echo -e "${BLUE}=== Path-Specific Instructions ===${NC}"
for file in ".github/instructions/mcp-servers.instructions.md" \
            ".github/instructions/cli-dashboard.instructions.md" \
            ".github/instructions/tests.instructions.md"; do
    total=$((total + 1))
    check_file "$file" && count=$((count + 1))
done

echo ""
echo -e "${BLUE}=== Custom Agents ===${NC}"
for file in ".github/agents/mcp-server-developer.md" \
            ".github/agents/financial-analyst.md" \
            ".github/agents/cli-dashboard-developer.md" \
            ".github/agents/test-engineer.md"; do
    total=$((total + 1))
    check_file "$file" && count=$((count + 1))
done

echo ""
echo -e "${BLUE}=== Agent Skills ===${NC}"
for skill in "financial-data-validation" \
             "mcp-server-debugging" \
             "technical-analysis-implementation" \
             "cli-dashboard-testing"; do
    total=$((total + 1))
    check_file ".github/skills/$skill/SKILL.md" && count=$((count + 1))
done

echo ""
echo -e "${BLUE}=== Hooks Configuration ===${NC}"
total=$((total + 1))
check_file ".github/hooks/hooks.json" && count=$((count + 1))

echo ""
echo -e "${BLUE}=== Hook Scripts (Bash) ===${NC}"
for script in "check-env-vars.sh" \
              "log-prompt.sh" \
              "pre-tool-validation.sh" \
              "post-tool-check.sh" \
              "error-handler.sh"; do
    total=$((total + 1))
    check_file "scripts/$script" && count=$((count + 1))
done

echo ""
echo -e "${BLUE}=== Hook Scripts (PowerShell) ===${NC}"
for script in "check-env-vars.ps1" \
              "log-prompt.ps1" \
              "pre-tool-validation.ps1" \
              "post-tool-check.ps1" \
              "error-handler.ps1"; do
    total=$((total + 1))
    check_file "scripts/$script" && count=$((count + 1))
done

echo ""
echo -e "${BLUE}=== Primary Agent Instructions ===${NC}"
total=$((total + 1))
check_file "AGENTS.md" && count=$((count + 1))

echo ""
echo -e "${BLUE}=== Documentation ===${NC}"
total=$((total + 1))
check_file "COPILOT_CLI_USAGE.md" && count=$((count + 1))
total=$((total + 1))
check_file ".github/COPILOT_CLI_IMPLEMENTATION.md" && count=$((count + 1))
total=$((total + 1))
check_file ".env.example" && count=$((count + 1))

echo ""
echo -e "${BLUE}=== Logs Directory ===${NC}"
total=$((total + 1))
check_dir "logs" && count=$((count + 1))

if [ -d "logs" ]; then
    for log in "copilot-sessions.log" "prompts.log" "tool-usage.log"; do
        total=$((total + 1))
        check_file "logs/$log" && count=$((count + 1))
    done
fi

echo ""
echo "=========================================="
echo -e "Summary: ${GREEN}$count/$total${NC} files present"
echo "=========================================="

if [ $count -eq $total ]; then
    echo -e "${GREEN}✓ All GitHub Copilot CLI features implemented!${NC}"
    exit 0
else
    missing=$((total - count))
    echo -e "${RED}✗ $missing file(s) missing${NC}"
    exit 1
fi
