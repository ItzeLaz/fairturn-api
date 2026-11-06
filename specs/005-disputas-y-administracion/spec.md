# 005 · Disputas, historial y administración

**Estado:** borrador · **Sprint:** 5 (cierre)

> Si el equipo trabaja con 4 sprints, como en el documento del proyecto, esta spec se hace dentro del Sprint 4 sin cambiar su contenido.

## Objetivo

Dar una salida a los desacuerdos sobre pagos con un **árbitro neutral** que decide con la evidencia registrada, mostrar un **historial de cumplimiento** explicable y dar al ADMIN las herramientas para habilitar organizadores, asignar árbitros y ver indicadores. Además, dejar el sistema **desplegable con un solo comando**.

## Historias de usuario

- Como **PARTICIPANTE**, quiero abrir una disputa si dicen que no pagué o si no me confirman un pago, para que un árbitro lo revise.
- Como **ARBITRO**, quiero ver las pruebas registradas de una disputa y resolverla para dar una decisión imparcial.
- Como **PARTICIPANTE**, quiero ver mi historial de cumplimiento y el de los miembros de mis tandas.
- Como **ADMIN**, quiero habilitar organizadores y asignar árbitros para controlar quién puede crear tandas y mediar.
- Como **ADMIN**, quiero ver indicadores sencillos del sistema.

## Disputas

### Estados (patrón State)

```
ABIERTA ──(árbitro asignado)──► EN_REVISION ──resolver──► RESUELTA
```

### Reglas

- **R1. Quién abre.** El pagador o el receptor del pago, con un motivo de 10 a 500 caracteres.
- **R2. Cuándo.** Solo sobre un pago `DECLARADO` (el receptor dice que no lo recibió, o el pagador reclama que no se lo confirman), o sobre un pago `PENDIENTE` con mora registrada (el receptor lo reporta sin pagar). En otro estado, 409. Un pago solo tiene una disputa abierta a la vez.
- **R3.** Al abrirla, el pago pasa a `EN_DISPUTA`.
- **R4. Asignación automática.** Se asigna al usuario con rol `ARBITRO` que tenga menos disputas sin resolver y que **no sea miembro de esa tanda**. La disputa pasa a `EN_REVISION`. Si no hay árbitro disponible, queda `ABIERTA` y el ADMIN la asigna a mano.
- **R5. Conflicto de interés.** Un árbitro nunca puede ser asignado, ni de forma automática ni manual, a una disputa de una tanda en la que es miembro (409).
- **R6.** Un ARBITRO solo ve y resuelve **sus** disputas asignadas (403 para las demás).
- **R7. Resolución.** El árbitro decide `PAGO_VALIDO` (el pago pasa a `CONFIRMADO`) o `PAGO_NO_VALIDO` (pasa a `NO_VALIDADO`), con un motivo obligatorio. La decisión es final en esta versión.
- **R8. Evidencia.** El detalle de la disputa incluye el pago, su referencia, las fechas y las entradas de la bitácora relacionadas con ese pago.
- **R9.** Abrir y resolver generan `DISPUTA_ABIERTA` y `DISPUTA_RESUELTA` en la bitácora.

## Historial de cumplimiento

Contadores simples **derivados de la bitácora** y de los pagos, sin puntuaciones opacas:

| Indicador | Cómo se calcula |
|---|---|
| `pagosTotales` | Pagos donde el usuario fue pagador y llegaron a estado final |
| `pagosPuntuales` | De esos, los declarados antes de `fechaLimiteGracia` |
| `porcentajePuntual` | `pagosPuntuales / pagosTotales × 100`, un decimal; `null` si no hay pagos |
| `moras` | Pagos con mora registrada |
| `tandasCompletadas` | Tandas `FINALIZADA` donde fue miembro |
| `disputasPerdidas` | Disputas resueltas en su contra: como pagador si `PAGO_NO_VALIDO`, como receptor si `PAGO_VALIDO` |
| `noRevelaciones` | Veces que no reveló su secreto en un sorteo |

- **R10.** Un usuario ve su propio historial y el de quienes comparten al menos una tanda con él. Cualquier otro caso, 403.

## Administración

- **R11.** Solo `ADMIN`. Cambiar roles: agregar o quitar `ORGANIZADOR` o `ARBITRO`. `PARTICIPANTE` y `ADMIN` no se cambian desde la API.
- **R12.** Los roles viven en Keycloak; la API los cambia con la Admin API de Keycloak a través del puerto `GestorIdentidad`. El cambio aplica cuando el usuario renueva su token.
- **R13.** Indicadores: número de tandas por estado y número de disputas por estado.
- **R14.** Suspender cuentas (mencionado en el documento del proyecto) queda **fuera de este sprint**; se puede hacer desde la consola de Keycloak.

## Cierre del proyecto

- **R15.** `docker compose up -d --build` levanta desde cero `postgres`, `keycloak-db`, `keycloak` y `backend`.
- **R16.** Los datos sobreviven a `docker compose down` + `up` y al reinicio del equipo (volúmenes `postgres_data` y `keycloak_data`, `restart: unless-stopped`).
- **R17.** El README explica cómo levantar el sistema y correr la app en dos emuladores.
- **R18.** Se fusiona `release/1.0.0` a `main` con el tag `v1.0.0` y de vuelta a `develop`.

## Escenarios de aceptación

```gherkin
# language: es
Característica: Disputas, historial y administración

  Escenario: El receptor abre una disputa sobre un pago declarado
    Dado un pago DECLARADO cuyo receptor es "participante2"
    Cuando "participante2" hace POST /api/pagos/{id}/disputa con un motivo
    Entonces la respuesta es 201
    Y el pago pasa a EN_DISPUTA
    Y la disputa se asigna a "arbitro1" y queda EN_REVISION

  Escenario: Un tercero intenta abrir una disputa
    Dado un participante que no es pagador ni receptor del pago
    Cuando intenta abrir una disputa
    Entonces la respuesta es 403

  Escenario: Disputa sobre un pago ya confirmado
    Dado un pago CONFIRMADO
    Cuando su pagador intenta abrir una disputa
    Entonces la respuesta es 409

  Escenario: Conflicto de interés
    Dado que "arbitro1" es miembro de la tanda X
    Cuando se abre una disputa en la tanda X
    Entonces la disputa no se asigna a "arbitro1"

  Escenario: Asignación manual con conflicto de interés
    Dado que "arbitro1" es miembro de la tanda X
    Cuando el ADMIN intenta asignarle una disputa de la tanda X
    Entonces la respuesta es 409

  Escenario: El árbitro solo ve sus disputas
    Dado que "arbitro1" tiene 2 disputas asignadas y existe otra asignada a otro árbitro
    Cuando "arbitro1" hace GET /api/disputas
    Entonces recibe solo sus 2 disputas

  Escenario: Resolver a favor del pagador
    Dado una disputa EN_REVISION asignada a "arbitro1"
    Cuando "arbitro1" la resuelve como PAGO_VALIDO con un motivo
    Entonces la respuesta es 200
    Y el pago pasa a CONFIRMADO
    Y el receptor suma una disputa perdida

  Escenario: Ver historial de alguien sin tandas en común
    Dado que "participante1" y "participante4" no comparten ninguna tanda
    Cuando "participante1" consulta el historial de "participante4"
    Entonces la respuesta es 403

  Escenario: Habilitar a un organizador
    Dado que "admin1" tiene el rol ADMIN
    Cuando agrega el rol ORGANIZADOR a "participante3"
    Entonces la respuesta es 200
    Y al renovar su token "participante3" puede crear tandas

  Escenario: Un participante intenta cambiar roles
    Cuando "participante1" hace PATCH /api/admin/usuarios/{id}/rol
    Entonces la respuesta es 403

  Escenario: Los datos sobreviven al reinicio
    Dado una tanda creada y el sistema levantado con Docker Compose
    Cuando se ejecuta docker compose down y luego docker compose up -d
    Entonces la tanda y los usuarios siguen existiendo
```

## Endpoints

| Método y endpoint | Rol | Respuestas |
|---|---|---|
| `POST /api/pagos/{id}/disputa` | Pagador o receptor | 201 · 400 · 403 · 409 |
| `GET /api/disputas` | ARBITRO | 200 |
| `GET /api/disputas/{id}` | ARBITRO asignado | 200 · 403 |
| `PATCH /api/disputas/{id}/resolver` | ARBITRO asignado | 200 · 400 · 403 · 409 |
| `GET /api/usuarios/{id}/historial` | El propio usuario o alguien con tanda en común | 200 · 403 |
| `PATCH /api/admin/usuarios/{id}/rol` | ADMIN | 200 · 400 · 403 · 404 |
| `PATCH /api/admin/disputas/{id}/arbitro` | ADMIN | 200 · 403 · 409 |
| `GET /api/admin/usuarios` | ADMIN | 200 · 403 |
| `GET /api/indicadores/tandas` | ADMIN | 200 · 403 |
| `GET /api/indicadores/disputas` | ADMIN | 200 · 403 |

`GET /api/disputas/{id}`, `PATCH /api/admin/disputas/{id}/arbitro` y `GET /api/admin/usuarios` no están en el documento del proyecto: se agregan para ver la evidencia, asignar a mano cuando no hay árbitro y buscar usuarios. **Confirmar con el equipo.**

## Fuera de alcance

- Apelaciones, suspender cuentas desde la API, panel web de administración y notificaciones push.
