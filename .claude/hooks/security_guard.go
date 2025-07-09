package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strings"
)

type HookData struct {
	Tool struct {
		Name string `json:"name"`
		Args []struct {
			Name  string      `json:"name"`
			Value interface{} `json:"value"`
		} `json:"args"`
	} `json:"tool"`
}

type HookResponse struct {
	Continue       bool   `json:"continue"`
	StopReason     string `json:"stopReason,omitempty"`
	SuppressOutput bool   `json:"suppressOutput,omitempty"`
}

func main() {
	var data HookData
	if err := json.NewDecoder(os.Stdin).Decode(&data); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing JSON: %v\n", err)
		os.Exit(1)
	}

	// Verificar herramienta y argumentos
	toolName := data.Tool.Name

	// Patrones de seguridad
	dangerousPatterns := []struct {
		pattern string
		message string
	}{
		{`\.env`, "🚫 ACCESO DENEGADO: Archivos .env contienen secretos sensibles"},
		{`\.envrc`, "🚫 ACCESO DENEGADO: Archivos .envrc contienen configuración sensible"},
		{`echo.*\$\w+`, "🚫 ACCESO DENEGADO: No se permite leer variables de entorno por seguridad"},
		{`printenv`, "🚫 ACCESO DENEGADO: No se permite listar variables de entorno"},
		{`cat.*password`, "🚫 ACCESO DENEGADO: Posible intento de leer credenciales"},
		{`grep.*secret`, "🚫 ACCESO DENEGADO: Posible búsqueda de secretos"},
	}

	// Convertir argumentos a string para análisis
	argsStr := ""
	for _, arg := range data.Tool.Args {
		if str, ok := arg.Value.(string); ok {
			argsStr += str + " "
		}
	}

	// Verificar patrones peligrosos
	for _, dp := range dangerousPatterns {
		matched, _ := regexp.MatchString(dp.pattern, argsStr)
		if matched {
			response := HookResponse{
				Continue:       false,
				StopReason:     dp.message,
				SuppressOutput: false,
			}
			json.NewEncoder(os.Stdout).Encode(response)
			return
		}
	}

	// Análisis contextual inteligente
	if toolName == "Read" && strings.Contains(argsStr, "config") {
		fmt.Fprintf(os.Stderr, "⚠️ AVISO: Leyendo archivo de configuración. Verificar que no contiene secretos.\n")
	}

	if toolName == "Bash" && (strings.Contains(argsStr, "curl") || strings.Contains(argsStr, "wget")) {
		fmt.Fprintf(os.Stderr, "⚠️ AVISO: Descargando contenido externo. Verificar origen seguro.\n")
	}

	// Permitir ejecución
	response := HookResponse{
		Continue: true,
	}
	json.NewEncoder(os.Stdout).Encode(response)
}
