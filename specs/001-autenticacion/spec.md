# 001 · Autenticación y roles

**Estado:** borrador · **Sprint:** 1 · **Responsable de la spec:** Itzel

## Objetivo

Que solo usuarios autenticados usen la API de Fairturn y que cada uno pueda hacer únicamente lo que su rol permite. La identidad la gestiona Keycloak; la API no guarda contraseñas.

## Roles

Se definen como **roles de realm** en Keycloak (realm `fairturn`).

| Rol | Quién es | Qué puede hacer (resumen) |
|---|---|---|
| `PARTICIPANTE` | Integrante de una o varias tandas | Unirse con código, aportar al sorteo, declarar sus pagos, confirmar los pagos que recibe en su ronda, abrir disputas y consultar bitácora e historial **solo de sus tandas** |
| `ORGANIZADOR` | Persona que crea y coordina una tanda | Crear tandas y sus reglas, generar códigos de invitación e iniciar el sorteo. **No recibe el dinero ni puede modificar el sorteo ni la bitácora** |
| `ARBITRO` | Mediador neutral | Ver y resolver **solo las disputas que se le asignan**; nunca de una tanda donde es miembro |
| `ADMIN` | Administrador del sistema | Habilitar organizadores, asignar árbitros, suspender cuentas y consultar indicadores |

Un ORGANIZADOR también puede ser integrante de su tanda; en ese caso tiene los mismos derechos y límites que cualquier participante en el sorteo y los pagos.

**Autorización por propiedad.** Además del rol, la API valida la relación del usuario con el recurso usando el claim `sub` del token. Un usuario no puede ver ni modificar recursos ajenos cambiando el id en la URL. Las reglas concretas se definen en la spec de cada funcionalidad (002 en adelante).

## Flujo de autenticación (OAuth 2.0 / OpenID Connect)

1. La app Flutter abre el login de Keycloak en el navegador del sistema con **Authorization Code + PKCE (S256)**, usando el cliente público `fairturn-app` y el redirect `com.fairturn.app:/oauthredirect`.
2. El usuario inicia sesión (o se registra) en Keycloak.
3. Keycloak redirige a la app con un código; la app lo intercambia por un **access token** (JWT) y un **refresh token**.
4. La app guarda los tokens con `flutter_secure_storage`.
5. En cada llamada a la API, la app envía `Authorization: Bearer <access_token>`.
6. La API (Spring Security como Resource Server) valida la firma del JWT con las llaves públicas de Keycloak (JWKS) y su vigencia.
7. La API lee los roles del claim `realm_access.roles` y los convierte en autoridades `ROLE_<ROL>` (por ejemplo `ROLE_ADMIN`).
8. Cada endpoint autoriza según el rol con `@PreAuthorize`.

## Reglas

- **R1.** La API no mantiene sesión (stateless); toda petición protegida necesita un token válido.
- **R2.** Son públicos solo: `/actuator/health`, `/swagger-ui/**` y `/v3/api-docs/**`. Todo lo demás requiere token.
- **R3.** Sin token, token mal formado, con firma inválida o vencido → `401 Unauthorized`.
- **R4.** Token válido sin el rol requerido → `403 Forbidden`.
- **R5.** Todo usuario que se registra por su cuenta recibe el rol `PARTICIPANTE` por defecto. Los demás roles los asigna un `ADMIN`.
- **R6.** La API identifica al usuario por el claim `sub` del token (no por el nombre de usuario, que puede cambiar).
- **R7.** `GET /api/tandas/mias` lo pueden usar `PARTICIPANTE` y `ORGANIZADOR`. Un usuario que solo tiene `ARBITRO` o `ADMIN` recibe 403.

## Escenarios de aceptación

```gherkin
# language: es
Característica: Autenticación y autorización por rol

  Antecedentes:
    Dado que Keycloak tiene el realm "fairturn" con los roles PARTICIPANTE, ORGANIZADOR, ARBITRO y ADMIN
    Y existen los usuarios "participante1" con rol PARTICIPANTE y "admin1" con rol ADMIN

  Escenario: Token válido en un endpoint protegido
    Dado que "participante1" inició sesión y tiene un access token vigente
    Cuando hace GET /api/tandas/mias con el header "Authorization: Bearer <token>"
    Entonces la respuesta es 200
    Y el cuerpo es una lista (puede estar vacía)

  Escenario: Petición sin token
    Cuando se hace GET /api/tandas/mias sin el header Authorization
    Entonces la respuesta es 401

  Escenario: Token vencido o alterado
    Dado un access token vencido o con la firma modificada
    Cuando se hace GET /api/tandas/mias con ese token
    Entonces la respuesta es 401

  Escenario: Rol insuficiente
    Dado que "participante1" inició sesión y tiene un access token vigente
    Cuando hace una petición a un endpoint que requiere el rol ADMIN
    Entonces la respuesta es 403

  Escenario: Rol suficiente
    Dado que "admin1" inició sesión y tiene un access token vigente
    Cuando hace una petición a un endpoint que requiere el rol ADMIN
    Entonces la respuesta es 200

  Escenario: Usuario nuevo recibe el rol PARTICIPANTE
    Dado que una persona se registra en la pantalla de registro de Keycloak como "nuevo1"
    Cuando inicia sesión desde la app
    Entonces su token incluye "PARTICIPANTE" en realm_access.roles
    Y no incluye ORGANIZADOR, ARBITRO ni ADMIN

  Escenario: Endpoint público de salud
    Cuando se hace GET /actuator/health sin token
    Entonces la respuesta es 200
    Y el cuerpo contiene "status": "UP"
```

> En el Sprint 1 el "endpoint que requiere ADMIN" es un endpoint temporal de prueba (propuesta: `/api/ping/admin`). Se elimina cuando existan endpoints reales de administración.

## Fuera de alcance (Sprint 1)

- Cierre de sesión en Keycloak desde la app y revocación de tokens.
- Recuperación de contraseña y verificación de correo.
- Pantallas para que un ADMIN asigne roles (Sprint 5).

## Pendiente de decidir

- **Emisor del token.** El emulador ve Keycloak en `http://10.0.2.2:8180`, la computadora en `http://localhost:8180` y el backend dentro de Docker en `http://keycloak:8080`, así que el claim `iss` puede no coincidir con el `issuer-uri` que valida Spring. El documento del proyecto propone dos soluciones: (a) fijar `KC_HOSTNAME` en Keycloak para que el emisor sea siempre el mismo, o (b) validar la firma con un `jwk-set-uri` interno. Responsable: Adrian. Registrar aquí la opción elegida.
