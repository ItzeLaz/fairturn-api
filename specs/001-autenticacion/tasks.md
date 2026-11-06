# 001 · Autenticación y roles — Tareas

Marca con `[x]` al terminar y pon el enlace al PR o commit.

## Itzel · `feature/estructura-y-specs`
- [ ] T01 Repos `fairturn-api` y `fairturn-app` con `main` y `develop`
- [ ] T02 Colaboradores invitados y protección de ramas (o regla en README)
- [ ] T03 `spec.md`, `plan.md` y `tasks.md` de autenticación
- [ ] T04 `specs/openapi.yaml` inicial con Bearer JWT
- [ ] T05 README con Gitflow y Conventional Commits

## Adrian · parte A `feature/keycloak-realm`
- [ ] T06 Servicios `keycloak` y `keycloak-db` en `docker-compose.yml`
- [ ] T07 Realm `fairturn` con roles, cliente `fairturn-app` (PKCE S256) y usuarios de prueba
- [ ] T08 Registro habilitado con `PARTICIPANTE` por defecto
- [ ] T09 Realm exportado a `keycloak/realm-fairturn.json` e importación probada con `down -v`
- [ ] T10 Datos de conexión enviados a Jorge

## Adrian · parte B `feature/seguridad-jwt`
- [ ] T11 `JwtAuthenticationConverter` (`realm_access.roles` → `ROLE_*`)
- [ ] T12 `SecurityConfig` stateless con `@EnableMethodSecurity`
- [ ] T13 Decisión sobre el emisor documentada en `spec.md`
- [ ] T14 Endpoints de prueba por rol y `GET /api/tandas/mias` para PARTICIPANTE y ORGANIZADOR (puede devolver `[]`)
- [ ] T15 Pruebas 401 / 403 / 200

## Jorge · `feature/login-flutter`
- [ ] T16 Proyecto Flutter con dependencias y estructura `features/auth`
- [ ] T17 BLoC de autenticación y pantalla de login
- [ ] T18 Login real con Keycloak y tokens en `flutter_secure_storage`
- [ ] T19 Inicio distinto por rol
- [ ] T20 Sesión conservada al cerrar y reabrir la app

## Verificación final
- [ ] Todos los escenarios de `spec.md` comprobados
- [ ] `openapi.yaml` coincide con Swagger
- [ ] Ramas fusionadas a `develop`
