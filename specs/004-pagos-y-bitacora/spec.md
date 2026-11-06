# 004 · Pagos, mora y bitácora

**Estado:** borrador · **Sprint:** 4 · Al terminar este sprint el núcleo del sistema queda completo.

## Objetivo

Registrar cada pago con **doble confirmación** (quien paga declara, quien cobra confirma), detectar la **mora** y guardar todo en una **bitácora encadenada con hashes** que revela cualquier alteración.

> Fairturn no mueve dinero. El dinero circula fuera del sistema; aquí solo se declara, se confirma y queda constancia.

## Historias de usuario

- Como **PARTICIPANTE**, quiero ver las rondas de mi tanda, quién cobra y cuándo.
- Como **PARTICIPANTE**, quiero declarar mi pago de la ronda y que quien cobra lo confirme, para que quede constancia de ambas partes.
- Como **PARTICIPANTE** receptor, quiero confirmar los pagos que recibí.
- Como **PARTICIPANTE**, quiero verificar la integridad de la bitácora para saber que nadie alteró el registro.

## Rondas

Se generan al terminar el sorteo (spec 003), una por miembro, en el orden del resultado.

| Campo | Valor |
|---|---|
| `numero` | 1 … n |
| `receptor` | `orden[numero − 1]` |
| `fechaInicio` | fecha de activación + (numero − 1) × periodo |
| `fechaVencimiento` | fechaInicio + periodo |
| `fechaLimiteGracia` | fechaVencimiento + plazo de gracia |
| `estado` | `PROGRAMADA` → `EN_CURSO` → `CERRADA` |

Al activar la tanda se crea un **pago PENDIENTE** por cada miembro que no es el receptor de esa ronda. Una ronda se cierra cuando todos sus pagos están en un estado final (`CONFIRMADO` o `NO_VALIDADO`). La tanda pasa a `FINALIZADA` cuando se cierra la última ronda.

## Estados del pago (patrón State)

```
PENDIENTE ──declarar──► DECLARADO ──confirmar──► CONFIRMADO
    │                       │
    │ (con mora)            │ disputa
    └──────────► EN_DISPUTA ◄┘ ──resolver──► CONFIRMADO | NO_VALIDADO
```

La apertura y resolución de disputas se especifican en la spec 005.

## Reglas

- **R1.** Solo un miembro que **no** es el receptor de la ronda declara su pago, una vez, con una referencia de texto (3 a 140 caracteres). No se puede declarar en una ronda `PROGRAMADA`.
- **R2.** Solo el **receptor** de la ronda confirma un pago, y solo si está `DECLARADO`. Quien paga nunca puede confirmarse a sí mismo (403).
- **R3.** El ORGANIZADOR no tiene ningún permiso especial sobre pagos ajenos.
- **R4. Mora.** Una tarea programada (`@Scheduled`, puerto `Reloj`) revisa los pagos `PENDIENTE`. Si `ahora > fechaLimiteGracia`, marca `moraRegistrada = true` y registra `MORA_REGISTRADA` en la bitácora, una sola vez por pago. El pago se puede declarar después, pero ya no cuenta como puntual.
- **R5. Pago puntual** = declarado antes de `fechaLimiteGracia`.
- **R6.** Toda operación de esta spec publica un evento de dominio; un suscriptor lo convierte en una entrada de la bitácora (patrón Observer). Ningún caso de uso escribe en la bitácora directamente.
- **R7.** La bitácora es **solo de inserción**: no hay endpoint ni caso de uso que modifique o borre entradas.
- **R8.** Solo los miembros de la tanda ven sus rondas, pagos y bitácora (403 para los demás).

## Encadenamiento exacto de la bitácora

Esta sección es normativa: Java, Dart y el script de referencia deben coincidir byte por byte.

```
hash = hex( SHA-256( UTF8( hashPrevio + "|" + tipo + "|" + contenido + "|" + marcaDeTiempo ) ) )
```

- **Una cadena por tanda.** `secuencia` empieza en 1.
- **`hashPrevio` de la entrada 1:** 64 ceros (`000…000`).
- **`tipo`:** nombre del evento en mayúsculas (lista abajo).
- **`contenido`:** texto JSON **guardado tal cual** en la base. Para verificar se usa el texto guardado; **nunca se vuelve a serializar**, porque Java y Dart pueden ordenar o espaciar el JSON distinto. Puede contener `|`: no hay ambigüedad porque los demás campos tienen formato fijo.
- **`marcaDeTiempo`:** texto UTC ISO-8601 con exactamente 3 decimales y `Z`, por ejemplo `2026-11-06T22:15:30.123Z`. Se guarda como texto, no como `timestamp`, para que no cambie al leerlo.
- **Hash:** hexadecimal minúsculo de 64 caracteres.

**Verificación:** recorrer por `secuencia`; en cada entrada comprobar que `hashPrevio` sea igual al `hash` de la anterior (o a los 64 ceros) y que el hash recalculado sea igual al guardado. La primera entrada que falle es la que se reporta.

Si alguien altera una entrada y también recalcula su hash para ocultarlo, la cadena se rompe en la **siguiente**, y esa es la que se reporta. `vectores-bitacora.json` incluye los dos casos.

**Último hash en el teléfono.** La app guarda, por tanda, la `secuencia` y el `hash` de la última entrada que vio. Al volver a consultar, si esa entrada ya no tiene el mismo hash, muestra una alerta aunque la cadena nueva sea internamente correcta. Así detecta una reconstrucción completa hecha después de su última consulta.

### Tipos de entrada

`TANDA_CREADA`, `MIEMBRO_UNIDO`, `TANDA_CANCELADA`, `SORTEO_INICIADO`, `COMPROMISO_PUBLICADO`, `SECRETO_REVELADO`, `NO_REVELO`, `SORTEO_REINICIADO`, `SORTEO_EJECUTADO`, `PAGO_DECLARADO`, `PAGO_CONFIRMADO`, `MORA_REGISTRADA`, `DISPUTA_ABIERTA`, `DISPUTA_RESUELTA`, `TANDA_FINALIZADA`.

## Escenarios de aceptación

```gherkin
# language: es
Característica: Pagos con doble confirmación, mora y bitácora

  Escenario: Declarar un pago
    Dado una ronda EN_CURSO cuyo receptor es "participante2"
    Y un pago PENDIENTE de "participante1"
    Cuando "participante1" hace POST /api/rondas/{id}/pagos con una referencia
    Entonces la respuesta es 201 y el pago queda DECLARADO
    Y se agrega PAGO_DECLARADO a la bitácora

  Escenario: El receptor intenta declarar en su propia ronda
    Cuando "participante2" intenta declarar un pago en la ronda donde él cobra
    Entonces la respuesta es 403

  Escenario: Declarar dos veces
    Dado un pago ya DECLARADO
    Cuando su pagador intenta declararlo otra vez
    Entonces la respuesta es 409

  Escenario: El receptor confirma un pago declarado
    Dado un pago DECLARADO de una ronda cuyo receptor es el usuario autenticado
    Cuando hace PATCH /api/pagos/{id}/confirmar
    Entonces la respuesta es 200 y el pago pasa a CONFIRMADO
    Y se agrega PAGO_CONFIRMADO a la bitácora

  Escenario: Quien confirma no es el receptor
    Dado un participante que no es el receptor de esa ronda
    Cuando intenta confirmar el pago
    Entonces la respuesta es 403

  Escenario: Quien paga intenta confirmarse a sí mismo
    Cuando el pagador intenta confirmar su propio pago
    Entonces la respuesta es 403

  Escenario: Confirmar un pago no declarado
    Dado un pago PENDIENTE
    Cuando el receptor intenta confirmarlo
    Entonces la respuesta es 409

  Escenario: Se registra la mora
    Dado un pago PENDIENTE y un reloj simulado después de fechaLimiteGracia
    Cuando corre la tarea de mora
    Entonces el pago queda con moraRegistrada
    Y se agrega MORA_REGISTRADA a la bitácora una sola vez

  Escenario: Bitácora íntegra
    Dado una tanda con varias entradas en su bitácora
    Cuando un miembro hace GET /api/tandas/{id}/bitacora/verificar
    Entonces la respuesta es 200 con "integra": true

  Escenario: Bitácora alterada
    Dado que alguien modificó en la base el contenido de la entrada 3
    Cuando un miembro verifica la bitácora
    Entonces la respuesta indica "integra": false y "primeraAlterada": 3

  Escenario: La app detecta una reconstrucción
    Dado que la app guardó el hash de la entrada 5
    Y después alguien reconstruyó toda la cadena con otro contenido
    Cuando el miembro vuelve a abrir la bitácora
    Entonces la app avisa que el historial cambió desde su última consulta

  Escenario: Usuario ajeno a la tanda
    Cuando un usuario que no es miembro consulta rondas, pagos o bitácora
    Entonces la respuesta es 403
```

## Endpoints

| Método y endpoint | Rol | Respuestas |
|---|---|---|
| `GET /api/tandas/{id}/rondas` | Miembros | 200 · 403 |
| `GET /api/rondas/{id}/pagos` | Miembros | 200 · 403 |
| `POST /api/rondas/{id}/pagos` | Miembro pagador (no receptor) | 201 · 400 · 403 · 409 |
| `PATCH /api/pagos/{id}/confirmar` | Receptor de la ronda | 200 · 403 · 409 |
| `GET /api/tandas/{id}/bitacora` | Miembros | 200 · 403 |
| `GET /api/tandas/{id}/bitacora/verificar` | Miembros | 200 · 403 |

`GET /api/rondas/{id}/pagos` no está en el documento del proyecto; se agrega para la pantalla "Pagos recibidos". **Confirmar con el equipo.**

## Limitaciones declaradas

- El sistema no puede obligar a pagar; deja evidencia, registra la mora y da acceso a un árbitro.
- Quien controle la base podría reconstruir toda la cadena antes de que alguien la consulte. Mejora futura: anclar el último hash fuera del sistema.
