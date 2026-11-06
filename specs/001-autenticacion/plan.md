# 001 · Autenticación y roles — Plan técnico

Cómo se implementa [spec.md](spec.md).

## Componentes

| Componente | Tecnología | Responsable |
|---|---|---|
| Proveedor de identidad | Keycloak 26.8.1 en Docker (puerto 8180), realm `fairturn`, base `keycloak-db` propia | Adrian (parte A) |
| Realm versionado | `keycloak/realm-fairturn.json`, importado al arrancar el compose (solo si el realm no existe) | Adrian (parte A) |
| API protegida | Spring Boot 4.1 (Java 21) + Spring Security 7 OAuth2 Resource Server | Adrian (parte B) sobre la base de Noemi |
| Conversión de roles | `JwtAuthenticationConverter` que lee `realm_access.roles` → `ROLE_*` | Adrian (parte B) |
| Login en la app | Flutter + `flutter_appauth` (Authorization Code + PKCE) | Jorge |
| Almacenamiento de tokens | `flutter_secure_storage` | Jorge |
| Contrato | `specs/openapi.yaml` (Bearer JWT) | Itzel |

## Configuración de Keycloak

- Realm: `fairturn`
- Roles de realm: `PARTICIPANTE`, `ORGANIZADOR`, `ARBITRO`, `ADMIN`
- Rol por defecto en registro: `PARTICIPANTE`
- Cliente `fairturn-app`: público, Standard Flow (Authorization Code), PKCE S256, redirect `com.fairturn.app:/oauthredirect`
- Cliente de pruebas aparte con Direct Access Grants, solo para obtener tokens desde Postman/curl
- Usuarios de prueba: `participante1`…`participante4`, `organizador1`, `arbitro1`, `admin1`

## Configuración de la API

- `SecurityConfig`: `SessionCreationPolicy.STATELESS`, `@EnableMethodSecurity`, públicos solo `/actuator/health`, `/swagger-ui/**`, `/v3/api-docs/**`.
- Validación del JWT: base `issuer-uri: http://localhost:8180/realms/fairturn`; ajustar con `KC_HOSTNAME` o `jwk-set-uri` según la decisión de la spec.
- Swagger con springdoc-openapi 3.0; activar `springdoc.show-actuator: true` para que `/actuator/health` aparezca y coincida con el contrato.
- Respuestas de error: 401 sin token o token inválido; 403 con rol insuficiente.

## Orden de trabajo

1. Itzel: repos, `develop`, specs y contrato.
2. Adrian A: realm listo y exportado → avisa a Jorge.
3. Noemi: backend base fusionado → avisa a Adrian.
4. Adrian B: seguridad JWT y endpoints de prueba.
5. Jorge: conecta el login real con el realm.

## Cómo se prueba

- API: con curl o Postman usando tokens del cliente de pruebas (casos 401, 403, 200 de la spec).
- App: login con `participante1` y `organizador1` en el emulador; cerrar y reabrir la app conserva la sesión.
- Realm: `docker compose down -v` y `docker compose up -d` lo importa desde cero.

## Riesgos

- **`iss` distinto entre emulador, computadora y Docker** → `KC_HOSTNAME` o `jwk-set-uri` (ver spec).
- **La exportación parcial de la consola no incluye usuarios** → usar el comando de exportación de Keycloak o completar los usuarios en el JSON.
- **http en desarrollo** → `allowInsecureConnections` en AppAuth y tráfico no cifrado permitido solo en debug.
