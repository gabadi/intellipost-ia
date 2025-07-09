#!/bin/bash

# Script de seguridad usando variables oficiales de Claude
# Usa CLAUDE_FILE_PATHS (oficial) en lugar de CLAUDE_FILE (inexistente)

# Obtener archivos de la variable oficial
FILES="${CLAUDE_FILE_PATHS:-}"

# Patrones de seguridad
if [[ "$FILES" =~ \.env ]]; then
    echo "🚫 ACCESO DENEGADO: Archivos .env contienen secretos sensibles" >&2
    exit 2
fi

if [[ "$FILES" =~ \.envrc ]]; then
    echo "🚫 ACCESO DENEGADO: Archivos .envrc contienen configuración sensible" >&2
    exit 2
fi

# Verificar comandos peligrosos (leer desde stdin)
HOOK_DATA=$(cat)
if echo "$HOOK_DATA" | grep -q 'echo.*\$'; then
    echo "🚫 ACCESO DENEGADO: No se permite leer variables de entorno por seguridad" >&2
    exit 2
fi

if echo "$HOOK_DATA" | grep -q 'printenv'; then
    echo "🚫 ACCESO DENEGADO: No se permite listar variables de entorno" >&2
    exit 2
fi

# Avisos contextuales
if [[ "$FILES" =~ config ]]; then
    echo "⚠️ AVISO: Leyendo archivo de configuración. Verificar que no contiene secretos." >&2
fi

# Permitir ejecución
exit 0
