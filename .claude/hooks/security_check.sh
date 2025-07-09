#!/bin/bash

# Script wrapper para security_guard.go
# Recibe información del hook de Claude y la envía al script Go

# Crear JSON con la información del archivo
cat << EOF | go run .claude/hooks/security_guard.go
{
  "tool": {
    "name": "${CLAUDE_TOOL:-Read}",
    "args": [
      {
        "name": "file_path",
        "value": "${CLAUDE_FILE:-unknown}"
      }
    ]
  }
}
EOF
