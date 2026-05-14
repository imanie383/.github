---
name: standup-skill
description: Genera el texto del stand-up (standup, daily, daily standup) del equipo para los lunes y miércoles. Úsala cuando el usuario pida preparar el stand, el daily, el texto del stand-up, o quiera saber qué hizo ayer y qué hará hoy. También úsala si el usuario dice "ayúdame con el stand", "prepara el stand de hoy", "qué reporto hoy", o cualquier variación relacionada con el reporte diario. Usa curl con token de GitLab — el token se resuelve automáticamente sin pedírselo al usuario en cada sesión.
---
 
# Standup Skill
 
Genera el texto del stand-up de un miembro del equipo basándose en su actividad reciente en GitLab (work items y merge requests) del proyecto `ircanada/ircodoo`.
 
Usa `curl` con un Personal Access Token de GitLab para las consultas. El token se resuelve automáticamente — no hay que pedírselo al usuario en cada sesión.
 
---
 
## Paso 1 – Resolver el token de GitLab
 
Buscar el token en este orden de prioridad:
 
### 1a. Variable de entorno
```bash
echo $GITLAB_TOKEN
```
 
### 1b. Archivo ~/.env
```bash
grep GITLAB_TOKEN ~/.env 2>/dev/null | cut -d= -f2
```
 
### 1c. Archivo dedicado
```bash
cat ~/.gitlab_token 2>/dev/null
```
 
Si ninguno devuelve un token, pedírselo al usuario y sugerirle que lo guarde para no volver a pedirlo:
 
```bash
# Guardar para futuras sesiones (recomendado)
echo 'GITLAB_TOKEN=glpat-xxxxxxxxxxxx' >> ~/.env && chmod 600 ~/.env
```
 
Cómo obtener el token: **GitLab → Avatar → Edit Profile → Access Tokens** → crear con scope `api`.
 
Una vez resuelto el token, usarlo en todas las llamadas como `-H "PRIVATE-TOKEN: $GITLAB_TOKEN"`.
 
---
 
## Paso 2 – Obtener el username del usuario
 
### 2a. Detectar automáticamente desde la API
```bash
curl -s "https://gitlab.com/api/v4/user" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" | jq -r '.username'
```
 
Si el usuario ya proporcionó su username en el mensaje, usar ese directamente.
 
### 2b. Confirmar si hay ambigüedad
 
Si el username detectado no coincide con lo que el usuario espera, preguntarle.
 
---
 
## Paso 3 – Calcular fechas del stand
 
El stand se da **lunes y miércoles**. Usar la fecha actual del sistema (`date +%Y-%m-%d`).
 
| Día del stand | "Ayer" cubre                     |
|---------------|----------------------------------|
| Lunes         | Viernes anterior (incluye finde) |
| Miércoles     | Martes                           |
| Otro día      | Día anterior                     |
 
Calcular `DATE_AFTER` (inicio del rango) y `DATE_BEFORE` (hoy) en formato `YYYY-MM-DD`.
 
---
 
## Paso 4 – Obtener actividad de GitLab vía curl
 
Base URL: `https://gitlab.com/api/v4`  
Proyecto: `ircanada/ircodoo` (URL-encoded: `ircanada%2Fircodoo`)
 
### 4a. Resolver el user ID a partir del username
 
```bash
curl -s "https://gitlab.com/api/v4/users?username=$USERNAME" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" | jq -r '.[0].id'
```
 
### 4b. Obtener eventos del usuario en el rango de fechas
 
```bash
curl -s "https://gitlab.com/api/v4/users/$USER_ID/events?after=$DATE_AFTER&before=$DATE_BEFORE&per_page=100" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"
```
 
Filtrar eventos relevantes por `action_name`:
- `pushed` → commits/pushes
- `commented on` → comentarios en issues o MRs
- `opened` → issues o MRs abiertos
- `closed` → issues o MRs cerrados
- `merged` → MRs mezclados
- `approved` → MRs aprobados
Y por `target_type`:
- `Issue` → work item / issue
- `MergeRequest` → merge request
- `Note` → comentario (revisar `note.noteable_type`)
### 4c. Obtener MRs asignados al usuario con actividad reciente
 
```bash
curl -s "https://gitlab.com/api/v4/projects/ircanada%2Fircodoo/merge_requests?assignee_username=$USERNAME&state=opened&updated_after=$DATE_AFTER" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"
```
 
### 4d. Obtener issues/work items asignados al usuario
 
```bash
curl -s "https://gitlab.com/api/v4/projects/ircanada%2Fircodoo/issues?assignee_username=$USERNAME&state=opened&updated_after=$DATE_AFTER" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"
```
 
---
 
## Paso 5 – Interpretar y agrupar la actividad
 
### Bloque "Ayer" (actividad en el rango de fechas)
- Commits/pushes a branches
- Issues comentados, cerrados o actualizados
- MRs creados, comentados, aprobados o mezclados
- Revisiones técnicas realizadas
### Bloque "Hoy" (inferido del estado actual)
- MRs abiertos asignados al usuario → "Continuar con MR !X"
- Issues abiertos asignados → "Continuar con issue #X"
- Si hay MRs esperando revisión → mencionarlo como pendiente
### Detectar bloqueantes
Marcar como bloqueante cuando:
- Un MR está abierto pero sin reviewer asignado
- Un MR tiene comentarios sin resolver de otra persona
- Un issue está en espera de respuesta externa
---
 
## Paso 6 – Formatear el texto del stand
 
Usa el nombre real del usuario si lo conoces; si no, usa el username.
 
```
[Nombre]:
- [ISSUE#NUMBER]: [Actividad de ayer 1] (link si aplica)
- [ISSUE#NUMBER]: [Actividad de ayer 2]
  - Sub-detalle si hay varios items del mismo contexto
Hoy:
- [ISSUE#NUMBER]: [Plan 1]
- [ISSUE#NUMBER]: [Plan 2]
Bloqueantes (solo si los hay):
- [ISSUE#NUMBER]: Esperando revisión de X en MR !N
```
 
### Reglas de formato
- Empezar cada item con el número de issue o MR (`#NNN` o `!NNN`), seguido de dos puntos y la descripción.
- Links: `texto (https://gitlab.com/ircanada/ircodoo/-/issues/NNN)` o solo `#NNN` / `!NNN` si el contexto es claro.
- Si hay varios issues/MRs del mismo módulo o cliente, agrúpalos con sub-bullets bajo ese nombre.
- Si no hubo actividad detectable: *"No se encontró actividad en GitLab para este período. ¿Quieres agregar algo manualmente?"*
- El idioma del output debe coincidir con el idioma en que el usuario hizo la solicitud (español o inglés).
### Ejemplo de output
 
```
jqbeltran2:
- IRC:
  - #4221: revisado y comentado.
  - #4255: revisado y comentado.
  - !342: MR creado con fix para #4221.
- villagroup:
  - !1258: pendiente respuesta de Hugo para continuar.
Hoy:
- #4221: continuar con revisión de issues IRC pendientes.
- !1258: dar seguimiento al MR de villagroup.
Bloqueantes:
- !1258: esperando respuesta de Hugo (villagroup).
```
 
---
 
## Manejo de errores
 
| Error | Acción |
|-------|--------|
| Token no encontrado | Pedirlo al usuario y sugerir guardarlo en `~/.env` |
| 401 | Token inválido o expirado — pedir uno nuevo |
| 403 | El usuario no tiene permisos en `ircanada/ircodoo` |
| 404 | Verificar que el username exista en GitLab |
| Timeout / sin conexión | Verificar conectividad del contenedor a `gitlab.com` |
| Sin datos | Indicar que no hubo actividad y ofrecer completar manualmente |
 
---
 
## Instalación de jq (si no está disponible)
 
```bash
docker exec -it -u root NAMES bash
apt install -y jq
```
 
---
 
## Configuración inicial de glab (opcional)
 
`glab` se puede usar para autenticarse una vez y derivar el token, pero en este entorno Docker las llamadas a la API de GitLab se hacen directamente con `curl` por compatibilidad de red. `glab` sigue siendo útil para el login inicial y para obtener el username con `glab api /user | jq -r '.username'` si la conectividad lo permite.
 
Para instalar `glab`:
 
```bash
docker exec -it -u root NAMES bash
curl -L \
  https://gitlab.com/gitlab-org/cli/-/releases/v1.97.0/downloads/glab_1.97.0_linux_amd64.deb \
  -o glab_latest.deb
apt install -y ./glab_latest.deb
```
 
Autenticarse:
 
```bash
glab auth login --hostname gitlab.com --token
# Pegar el token cuando lo solicite
# Verificar: glab auth status
```
 
---
 
## Notas
 
- Para el stand del **lunes**: el rango cubre desde el viernes; mencionar si hubo actividad el fin de semana o indicar que no aplica.
- `jq` debe estar instalado en el contenedor para parsear las respuestas JSON.
