---
name: odoo-module-test-guide
description: Analiza modulos de Odoo y genera guias de prueba detalladas en formato markdown. Este skill debe usarse cuando el usuario solicite crear documentacion de pruebas, guias de testing, o documentacion tecnica para un modulo Odoo. Triggers incluyen frases como "genera guia de pruebas", "documenta el modulo", "crea testing guide", "analiza el modulo X".
---

# Odoo Module Test Guide Generator

## Overview

Este skill analiza la estructura de cualquier modulo de Odoo y genera una guia de pruebas completa en formato markdown. Combina analisis automatizado mediante script con comprension contextual de Claude para producir documentacion util y precisa.

## Workflow

### Paso 1: Obtener la Ruta del Modulo

Solicitar al usuario la ruta absoluta del modulo Odoo a analizar. El modulo debe tener un archivo `__manifest__.py` valido.

Ejemplo de ruta: `/home/user/odoo/addons/mi_modulo`

### Paso 2: Ejecutar el Script de Analisis

Ejecutar el script `analyze_module.py` para extraer informacion estructurada:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_module.py /ruta/al/modulo --pretty
```

El script genera un JSON con:
- **manifest**: Metadatos del modulo (nombre, version, dependencias, autor)
- **models**: Modelos con campos, metodos y relaciones
- **wizards**: Transient models con sus campos y metodos
- **views**: Vistas, menus y acciones definidas en XML
- **data**: Cron jobs y configuraciones iniciales
- **security**: Reglas de acceso y grupos
- **tests**: Clases y metodos de prueba existentes
- **summary**: Estadisticas del modulo

### Paso 3: Leer Archivos Clave del Modulo

Despues del analisis automatico, leer los archivos Python principales para comprender:

1. **Logica de negocio**: Metodos principales y su proposito
2. **Flujos de trabajo**: Como interactuan los modelos
3. **Configuraciones**: Opciones disponibles en res.config.settings
4. **Wizards**: Flujo de los asistentes transaccionales

Priorizar archivos con mas metodos y campos segun el resumen del script.

### Paso 4: Analizar Vistas XML

Leer archivos XML en `views/` para identificar:

1. **Rutas de menu**: Navegacion del usuario en Odoo
2. **Acciones disponibles**: Botones y acciones masivas
3. **Campos visibles**: Que ve el usuario en formularios y listas

### Paso 5: Generar la Guia

Usar la plantilla en `references/guide_template.md` como estructura base. Adaptar las secciones segun el modulo:

#### Secciones Obligatorias

1. **Descripcion del Modulo**: Basada en manifest summary/description
2. **Estructura del Modulo**: Arbol de directorios y tabla de modelos
3. **Como Funciona**: Flujos principales con diagramas ASCII
4. **Requisitos Previos**: Dependencias y configuraciones necesarias
5. **Resumen de Menus**: Tabla de navegacion
6. **Caso de Prueba Completo**: Escenario end-to-end
7. **Troubleshooting**: Problemas comunes
8. **Glosario**: Terminos tecnicos del modulo

#### Secciones Condicionales

- **Configuracion del Modulo**: Solo si hereda `res.config.settings`
- **Probar el Cron Automatico**: Solo si tiene cron jobs en `data/`
- **Crear Datos de Prueba**: Adaptar segun el tipo de modulo

### Paso 6: Guardar la Guia

Guardar el archivo markdown generado como:

```
{module_name}_testing_guide.md
```

En el directorio del modulo o donde el usuario especifique.

## Estructura de Salida

La guia generada debe seguir este formato:

```markdown
# Guia de Pruebas del Modulo {Nombre} - Odoo v{Version}

## Indice
[enlaces a secciones]

## Descripcion del Modulo
[funcionalidad principal, caso de uso]

## Estructura del Modulo
[arbol de directorios, tabla de modelos]

## Como Funciona
[flujos con diagramas ASCII]

## Requisitos Previos
[dependencias, configuraciones]

## Configuracion del Modulo
[si aplica: res.config.settings]

## Crear Datos de Prueba
[pasos para crear registros de prueba]

## Ejecutar Funcionalidades
[metodos, wizards, acciones]

## Verificar Resultados
[donde ver los resultados]

## Probar el Cron Automatico
[si aplica: cron jobs]

## Resumen de Menus
[tabla de navegacion]

## Caso de Prueba Completo
[escenario end-to-end con datos y verificaciones]

## Troubleshooting
[problemas comunes y soluciones]

## Glosario
[terminos tecnicos]

## Contacto y Soporte
[autor, version, licencia]
```

## Recursos del Skill

### scripts/analyze_module.py

Script Python que extrae informacion estructurada del modulo:

- Parsea `__manifest__.py` para metadatos
- Analiza archivos Python con AST para modelos y metodos
- Parsea XMLs para vistas, menus y cron jobs
- Lee CSV de seguridad para permisos
- Genera JSON estructurado

**Uso:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_module.py /ruta/modulo --pretty
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_module.py /ruta/modulo -o analisis.json
```

### references/guide_template.md

Plantilla de referencia con la estructura completa de secciones y ejemplos de formato. Consultar para:

- Formato de tablas
- Estructura de diagramas ASCII
- Ejemplos de checklist de verificacion
- Formato de pasos numerados

## Notas de Estilo

1. **Idioma**: Generar guías en español
2. **Tablas**: Usar formato markdown estándar
3. **Código**: Usar bloques de código con syntax highlighting
4. **Diagramas**: ASCII art con caracteres box-drawing (─│┌┐└┘├┤┬┴┼)
5. **Rutas de menú**: Formato **Menú → Submenú → Opción**
