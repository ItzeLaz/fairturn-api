# Fairturn API

Backend de **Fairturn**, una app para organizar tandas **sin depender de la palabra de una sola persona**:

- 🎲 **El sorteo lo puede comprobar cualquiera.** Compromiso y revelación: cada miembro recalcula el orden en su celular.
- 💸 **El organizador nunca tiene el dinero.** Se paga directo a quien cobra; quien paga declara y quien recibe confirma.
- 🔗 **El registro no se reescribe sin que se note.** Bitácora encadenada con hashes.
- ⚖️ **Un árbitro neutral** resuelve las disputas con la evidencia registrada.

> Fairturn no custodia ni mueve dinero. Registra, verifica y hace visible lo que ocurre.

## Repositorios

| Repo | Contenido |
|---|---|
| `fairturn-api` (este) | API REST en Spring Boot, specs, contrato OpenAPI y Docker Compose (PostgreSQL + Keycloak) |
| `fairturn-app` | App Android en Flutter |

## Stack

| Pieza | Tecnología |
|---|---|
| API | Spring Boot 4.1 · Java 21 · Spring Security 7 (Resource Server) · arquitectura hexagonal |
| Datos | PostgreSQL 17 · Spring Data JPA · Flyway · MapStruct |
| Identidad | Keycloak 26.8.1 · OAuth 2.0 / OIDC · JWT |
| App | Flutter · flutter_bloc · flutter_appauth (PKCE) · flutter_secure_storage |
| Contrato | OpenAPI 3 · springdoc-openapi (Swagger) |
| Despliegue | Docker · Docker Compose |

> Versiones tomadas del documento del proyecto; se confirman al iniciar el Sprint 1.

## Roles

| Rol | Puede |
|---|---|
| `PARTICIPANTE` | Unirse con código, aportar al sorteo, declarar y confirmar pagos, abrir disputas, ver bitácora e historial de sus tandas |
| `ORGANIZADOR` | Crear tandas, generar códigos e iniciar el sorteo. **No recibe dinero ni altera el sorteo o la bitácora** |
| `ARBITRO` | Ver y resolver solo sus disputas asignadas, nunca de una tanda donde es miembro |
| `ADMIN` | Habilitar organizadores, asignar árbitros y ver indicadores |

## Estructura del repositorio

```
fairturn-api/
├── specs/                              Especificaciones (SDD)
│   ├── openapi.yaml                    Contrato completo; cada operación indica su sprint
│   ├── 001-autenticacion/              Sprint 1
│   ├── 002-tandas/                     Sprint 2
│   ├── 003-sorteo-verificable/         Sprint 1 (algoritmo) y 3 (protocolo)
│   │   ├── vectores.json               Casos de prueba compartidos Java/Dart
│   │   └── referencia/                 Script Python de referencia
│   ├── 004-pagos-y-bitacora/           Sprint 4
│   │   ├── vectores-bitacora.json
│   │   └── referencia/
│   └── 005-disputas-y-administracion/  Sprint 5
├── keycloak/                           Realm exportado (Sprint 1)
├── src/main/java/com/fairturn/         Arquitectura hexagonal
│   ├── domain/                         Entidades, reglas y puertos (sin Spring)
│   ├── application/                    Casos de uso
│   ├── infrastructure/                 JPA, seguridad, Keycloak, tareas programadas
│   └── web/                            Controladores REST y DTOs
├── docker-compose.yml
└── .env.example
```

Cada carpeta de spec tiene `spec.md` (qué y criterios de aceptación), `plan.md` (cómo) y `tasks.md` (tareas del sprint).

## Sprints

| # | Sprint | Spec | Entregables principales |
|---|---|---|---|
| 1 | Base y seguridad | 001, 003 (algoritmo) | Gitflow, Spring + PostgreSQL, realm de Keycloak, endpoints protegidos, login en Flutter, algoritmo del sorteo con vectores |
| 2 | Tandas y membresías | 002 | CRUD de tandas con propiedad, códigos de invitación, patrón State |
| 3 | Sorteo verificable | 003 | Compromiso, revelación, pantalla "Verificar sorteo", generación de rondas |
| 4 | Pagos y bitácora | 004 | Doble confirmación, mora, bitácora encadenada con verificación |
| 5 | Disputas y cierre | 005 | Disputas con árbitro, historial, administración, Docker Compose completo, pruebas |

## Cómo trabajamos (SDD)

1. **Especificar:** `spec.md` con reglas y escenarios Gherkin.
2. **Contrato:** actualizar `specs/openapi.yaml`.
3. **Planificar:** `plan.md` y `tasks.md`.
4. **Implementar** en una rama `feature/*`.
5. **Validar:** pruebas de aceptación, de contrato y de roles; PR aprobado.

**Definition of Done:** el código cumple la spec, pasan las pruebas de aceptación y de roles, el contrato coincide con Swagger y la rama se fusionó a `develop`.

## Gitflow

| Rama | Para qué | Sale de | Se fusiona en |
|---|---|---|---|
| `main` | Versiones entregadas, con tag (`v1.0.0`) | — | — |
| `develop` | Integración del trabajo del sprint (rama por defecto) | `main` | `main` (vía `release/*`) |
| `feature/<tema>` | Una historia o tarea | `develop` | `develop` |
| `release/<versión>` | Preparar una entrega | `develop` | `main` y `develop` |
| `hotfix/<tema>` | Corregir algo urgente en `main` | `main` | `main` y `develop` |

**Nombres de ramas:** minúsculas y guiones, en español. Ejemplos: `feature/backend-base`, `feature/login-flutter`, `release/1.0.0`.

### Reglas

1. **Nadie sube directo a `main` ni a `develop`.** Están protegidas: todo entra por pull request.
2. Cada PR necesita **al menos una aprobación** de otra persona del equipo.
3. Antes de abrir el PR, actualiza tu rama con `develop` y verifica que compila y pasan las pruebas.
4. Después de fusionar, borra la rama `feature/*`.
5. Versionado semántico: una versión por sprint cerrado.

### Flujo diario

```bash
git checkout develop
git pull
git checkout -b feature/mi-tarea
# ... trabajar y hacer commits ...
git push -u origin feature/mi-tarea
# abrir el pull request a develop en GitHub
```

## Commits: Conventional Commits

Formato: `tipo: descripción corta en minúsculas`

| Tipo | Cuándo | Ejemplo |
|---|---|---|
| `feat` | Funcionalidad nueva | `feat: agrega endpoint de mis tandas` |
| `fix` | Corrección de un error | `fix: corrige validación del token vencido` |
| `docs` | Documentación o specs | `docs: agrega spec de autenticación` |
| `test` | Pruebas | `test: agrega vectores del sorteo` |
| `refactor` | Cambio interno sin cambiar comportamiento | `refactor: separa conversor de roles` |
| `chore` | Configuración, dependencias, Docker | `chore: agrega servicio postgres al compose` |

## Cómo levantar el sistema

> Se completa conforme avanzan los sprints. El objetivo final (Sprint 5) es:

**Requisitos:** Docker Desktop, Git, Flutter SDK y Android Studio con al menos un emulador (dos para la demostración).

```bash
git clone https://github.com/ItzeLaz/fairturn-api.git
cd fairturn-api
cp .env.example .env          # ajustar credenciales
docker compose up -d --build  # postgres, keycloak-db, keycloak y backend
docker compose ps
```

| Servicio | URL |
|---|---|
| API | http://localhost:8080 |
| Swagger | http://localhost:8080/swagger-ui.html |
| Salud | http://localhost:8080/actuator/health |
| Keycloak | http://localhost:8180 |

Desde el emulador de Android, la computadora se alcanza en `10.0.2.2` (API en `http://10.0.2.2:8080`, Keycloak en `http://10.0.2.2:8180`).

**Usuarios de prueba:** `participante1` a `participante4`, `organizador1`, `arbitro1`, `admin1`. Contraseñas en el realm importado.

**Detener:** `docker compose down`. Los datos se conservan en los volúmenes `postgres_data` y `keycloak_data`. Usa `docker compose down -v` solo si quieres borrarlos.

## Evidencias para la bitácora

- Nombre de las capturas: `S<sprint>_<nombre>_<n>.png` (ej. `S1_itzel_1.png`), con fecha y hora visibles.
- Cada captura lleva un pie de una línea con lo que demuestra y el enlace al PR o commit.
