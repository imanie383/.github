# Plantilla de Guia de Pruebas - Modulo Odoo

Esta plantilla define la estructura estandar para guias de prueba de modulos Odoo.
Claude debe usar esta estructura como referencia al generar la guia final.

---

## Estructura de Secciones

### 1. Encabezado

```markdown
# Guia de Pruebas del Modulo {MODULE_NAME} - Odoo v{VERSION}

## Indice

1. [Descripcion del Modulo](#descripcion-del-modulo)
2. [Estructura del Modulo](#estructura-del-modulo)
3. [Como Funciona](#como-funciona)
4. [Requisitos Previos](#requisitos-previos)
5. [Configuracion del Modulo](#configuracion-del-modulo)
6. [Crear Datos de Prueba](#crear-datos-de-prueba)
7. [Ejecutar Funcionalidades](#ejecutar-funcionalidades)
8. [Verificar Resultados](#verificar-resultados)
9. [Probar el Cron Automatico](#probar-el-cron-automatico)
10. [Resumen de Menus](#resumen-de-menus)
11. [Caso de Prueba Completo](#caso-de-prueba-completo)
12. [Troubleshooting](#troubleshooting)
13. [Glosario](#glosario)
```

---

### 2. Descripcion del Modulo

Incluir:
- Resumen de funcionalidad principal (del manifest summary/description)
- Caso de uso ideal
- Beneficios clave

```markdown
## Descripcion del Modulo

**{MODULE_NAME}** implementa {DESCRIPCION_FUNCIONALIDAD}.

### Funcionalidad principal

- {BULLET_POINT_1}
- {BULLET_POINT_2}
- {BULLET_POINT_3}

### Caso de uso ideal

{DESCRIPCION_CASO_USO}
```

---

### 3. Estructura del Modulo

Incluir:
- Arbol de directorios
- Tabla de modelos principales con descripcion

```markdown
## Estructura del Modulo

```
{module_name}/
├── models/
│   ├── {model_file_1}.py    # {descripcion}
│   └── {model_file_2}.py    # {descripcion}
├── wizard/
│   └── {wizard_file}.py     # {descripcion}
├── views/
├── data/
└── security/
```

### Modelos Principales

| Modelo | Descripcion |
|--------|-------------|
| `{model.name}` | {descripcion} |
```

---

### 4. Como Funciona

Incluir:
- Flujo de trabajo principal
- Diagrama de flujo ASCII si es posible
- Explicacion paso a paso

```markdown
## Como Funciona

### Flujo {nombre_flujo}

1. {paso_1}
2. {paso_2}
3. {paso_3}

### Diagrama de Flujo

```
┌─────────────────────┐
│  {estado_inicial}   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  {accion}           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  {resultado}        │
└─────────────────────┘
```
```

---

### 5. Requisitos Previos

Incluir:
- Modulos dependientes (del manifest)
- Configuraciones necesarias en Odoo
- Pasos de configuracion inicial

```markdown
## Requisitos Previos

### Paso 1: {Nombre_Requisito}

1. Navega a: **{Menu} → {Submenu} → {Opcion}**
2. {Instruccion}
3. Click en **Guardar**

### Paso 2: {Nombre_Requisito_2}

{Instrucciones}
```

---

### 6. Configuracion del Modulo

Incluir:
- Acceso a configuracion (si tiene res.config.settings)
- Opciones disponibles con explicacion
- Valores recomendados

```markdown
## Configuracion del Modulo

### Paso 1: Acceder a Ajustes

Navega a: **{Menu_Principal} → Configuracion → Ajustes**

### Paso 2: Localizar Seccion {Nombre_Seccion}

Busca la seccion **"{Nombre_Seccion}"** en los ajustes.

### Paso 3: Configurar Opciones

#### Opcion 1: {Nombre_Opcion}

- [ ] Marca esta casilla para {descripcion_funcionalidad}
- **{Campo_Relacionado}**: {Descripcion_campo}
```

---

### 7. Crear Datos de Prueba

Incluir:
- Pasos para crear registros de prueba
- Valores de ejemplo
- Tablas con datos sugeridos

```markdown
## Crear Datos de Prueba

### Crear {Nombre_Registro}

#### Paso 1: Acceder a {Vista}

Navega a: **{Menu} → {Submenu}**

#### Paso 2: Crear Nuevo Registro

Click en el boton **Nuevo**

#### Paso 3: Completar Datos

| Campo | Valor |
|-------|-------|
| {campo_1} | {valor_ejemplo} |
| {campo_2} | {valor_ejemplo} |
```

---

### 8. Ejecutar Funcionalidades

Incluir:
- Metodos para ejecutar la funcionalidad principal
- Desde vistas/botones
- Desde acciones masivas
- Configuracion de wizards

```markdown
## Ejecutar Funcionalidades

### Metodo 1: Desde {Vista/Modelo}

#### Paso 1: Ir a {Menu}

Navega a: **{Menu} → {Submenu}**

#### Paso 2: Seleccionar Registros

Marca el checkbox de los registros que deseas procesar.

#### Paso 3: Ejecutar Accion

Click en: **Accion → {Nombre_Accion}**

#### Paso 4: Configurar (Wizard)

| Campo | Descripcion |
|-------|-------------|
| {campo_wizard} | {descripcion} |

#### Paso 5: Confirmar

Click en el boton **{Nombre_Boton}**
```

---

### 9. Probar el Cron Automatico

Solo si el modulo tiene cron jobs.

```markdown
## Probar el Cron Automatico

### Acceder a Acciones Planificadas

Navega a: **Ajustes → Tecnico → Automatizacion → Acciones Planificadas**

> **Nota**: Necesitas activar el modo desarrollador.

### Localizar el Cron

Busca: **"{Nombre_Cron}"**

### Configuracion del Cron

| Campo | Valor por Defecto |
|-------|-------------------|
| Nombre | {nombre} |
| Frecuencia | {frecuencia} |
| Metodo | `{metodo}` |

### Ejecutar Manualmente

1. Abre el registro del cron
2. Click en el boton **"Ejecutar Manualmente"**
```

---

### 10. Resumen de Menus

Incluir:
- Tabla de menus principales
- Tabla de acciones disponibles

```markdown
## Resumen de Menus

### Menus Principales

| Funcionalidad | Ruta del Menu |
|---------------|---------------|
| {funcionalidad} | {Menu} → {Submenu} → {Opcion} |

### Acciones Disponibles

| Accion | Disponible en |
|--------|---------------|
| {nombre_accion} | {modelo} (Accion masiva) |
```

---

### 11. Caso de Prueba Completo

Incluir:
- Escenario de prueba con objetivo claro
- Datos iniciales en tabla
- Pasos de ejecucion numerados
- Calculos esperados
- Resultados esperados con tablas
- Checklist de verificacion

```markdown
## Caso de Prueba Completo

### Escenario de Prueba

**Objetivo**: {descripcion_objetivo}

### Datos Iniciales

| Parametro | Valor |
|-----------|-------|
| {parametro} | {valor} |

### Pasos de Ejecucion

#### 1. {Nombre_Paso}

```
{detalle_tecnico_o_valores}
```

#### 2. {Nombre_Paso_2}

{instrucciones}

### Resultados Esperados

#### En {Modelo/Vista}

| Campo | Valor Esperado |
|-------|----------------|
| {campo} | {valor} |

### Verificacion

- [ ] {item_verificacion_1}
- [ ] {item_verificacion_2}
- [ ] {item_verificacion_3}
```

---

### 12. Troubleshooting

Incluir problemas comunes basados en la funcionalidad.

```markdown
## Troubleshooting

### Problemas Comunes

#### {Descripcion_Problema}

**Causa**: {explicacion_causa}
**Solucion**:
1. {paso_solucion_1}
2. {paso_solucion_2}
```

---

### 13. Glosario

Incluir terminos tecnicos especificos del modulo.

```markdown
## Glosario

| Termino | Definicion |
|---------|------------|
| {termino} | {definicion} |
```

---

### 14. Contacto y Soporte (Footer)

```markdown
## Contacto y Soporte

**Desarrollador**: {author}
**Sitio Web**: {website}
**Version del Modulo**: {version}
**Licencia**: {license}

---

*Documento generado para Odoo v{odoo_version}*
*Modulo: {module_name} - {summary}*
```

---

## Notas para Claude

Al generar la guia:

1. **Adaptar al modulo**: No todas las secciones aplican a todos los modulos. Omitir secciones que no sean relevantes.

2. **Cron jobs**: Solo incluir seccion 9 si el modulo tiene cron jobs definidos en data/.

3. **Configuracion**: Solo incluir seccion 5 detallada si el modulo hereda de res.config.settings.

4. **Wizards**: Documentar todos los wizards encontrados en la seccion de "Ejecutar Funcionalidades".

5. **Diagramas**: Crear diagramas ASCII para flujos complejos basandose en el analisis del codigo.

6. **Casos de prueba**: Basar los casos en los tests existentes si los hay, o crear escenarios realistas.

7. **Idioma**: Mantener la guia en espanol, sin acentos en los encabezados markdown.

8. **Rutas de menu**: Deducir las rutas de menu de los menuitem en los XMLs de vistas.
