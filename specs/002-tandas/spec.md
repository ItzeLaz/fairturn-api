# 002 · Tandas y membresías

**Estado:** borrador · **Sprint:** 2

## Objetivo

Que un ORGANIZADOR cree tandas con reglas pactadas, invite con un código y que los participantes se unan, con **validación de propiedad**: nadie ve ni administra tandas ajenas cambiando el id en la URL.

## Historias de usuario

- Como **ORGANIZADOR**, quiero crear una tanda con monto, periodicidad y número de participantes para invitar a mi grupo.
- Como **ORGANIZADOR**, quiero generar un código de invitación para compartirlo por mensaje.
- Como **PARTICIPANTE**, quiero unirme a una tanda con un código para no depender de grupos de mensajería.
- Como **PARTICIPANTE**, quiero ver mis tandas y el detalle de cada una.

## Reglas pactadas de una tanda

| Campo | Tipo | Validación |
|---|---|---|
| `nombre` | texto | 3 a 60 caracteres |
| `monto` | decimal (MXN) | mayor que 0, máximo 2 decimales. Es lo que **cada miembro aporta por ronda** |
| `periodicidad` | enum | `SEMANAL`, `QUINCENAL`, `MENSUAL` |
| `numeroParticipantes` | entero | 2 a 20 (incluye al organizador si participa) |
| `plazoGraciaDias` | entero | 0 a 7 |
| `organizadorParticipa` | booleano | si es `true`, el organizador queda inscrito como miembro al crear |

Quien cobra en una ronda recibe `monto × (numeroParticipantes − 1)`.

**Modo demostración:** con el perfil `demo`, la configuración convierte cada periodicidad y el plazo de gracia a minutos (por ejemplo, `SEMANAL` = 3 min, 1 día de gracia = 1 min) para recorrer la tanda completa en la presentación.

## Ciclo de vida (patrón State)

```
BORRADOR → RECLUTANDO → SORTEO → ACTIVA → FINALIZADA
    │           │          │
    └───────────┴──────────┴──→ CANCELADA
```

| Estado | Qué significa | Cómo entra |
|---|---|---|
| `BORRADOR` | Recién creada | `POST /api/tandas` |
| `RECLUTANDO` | Acepta miembros | Al generar el primer código de invitación |
| `SORTEO` | Sorteo de turnos en curso (spec 003) | El organizador inicia el sorteo con cupo completo |
| `ACTIVA` | Rondas de pago en curso (spec 004) | El sorteo termina con resultado |
| `FINALIZADA` | Todas las rondas cerradas; solo lectura | Al cerrar la última ronda |
| `CANCELADA` | Ya no sigue; solo lectura | El organizador la cancela desde BORRADOR, RECLUTANDO o SORTEO |

Cada estado es una clase que decide qué operaciones permite. Una operación no permitida en el estado actual responde **409 Conflict**.

## Reglas

- **R1.** Solo un usuario con rol `ORGANIZADOR` puede crear tandas. El dueño es el `sub` de quien la crea.
- **R2. Propiedad del organizador.** Solo el dueño genera invitaciones, inicia el sorteo y cancela su tanda. Otro ORGANIZADOR recibe 403.
- **R3. Propiedad del miembro.** Solo los miembros (y el dueño) ven el detalle de una tanda. Otro usuario recibe 403. No se devuelve 404 para no revelar qué ids existen.
- **R4.** El código de invitación tiene 8 caracteres de `ABCDEFGHJKMNPQRSTUVWXYZ23456789` (sin 0/O, 1/I/L), vence a las 72 horas y se puede generar uno nuevo; el anterior deja de servir.
- **R5.** Solo se puede unir alguien a una tanda en `RECLUTANDO`, con cupo libre y si no es ya miembro. Si falla cualquiera, 409.
- **R6.** Un código inexistente o vencido responde 404.
- **R7.** Las reglas pactadas no cambian después de creada la tanda. En esta versión no hay endpoint de edición; para corregir, se cancela y se crea otra.
- **R8.** El primer request de cada usuario guarda o actualiza su registro local (`sub`, `preferred_username`, nombre) para mostrar nombres en la app.
- **R9.** Cada cambio relevante publica un evento de dominio (`TandaCreada`, `MiembroUnido`, `TandaCancelada`) para la bitácora de la spec 004.

## Escenarios de aceptación

```gherkin
# language: es
Característica: Tandas y membresías

  Escenario: Crear una tanda válida
    Dado que "organizador1" tiene el rol ORGANIZADOR
    Cuando hace POST /api/tandas con nombre, monto 500, periodicidad SEMANAL y 4 participantes
    Entonces la respuesta es 201
    Y la tanda queda en BORRADOR con "organizador1" como dueño

  Escenario: Un participante intenta crear una tanda
    Dado que "participante1" solo tiene el rol PARTICIPANTE
    Cuando hace POST /api/tandas
    Entonces la respuesta es 403

  Escenario: Datos inválidos
    Cuando el organizador crea una tanda con monto 0 o con 1 participante
    Entonces la respuesta es 400 con el detalle del campo inválido

  Escenario: Generar código de invitación
    Dado una tanda en BORRADOR de "organizador1"
    Cuando "organizador1" hace POST /api/tandas/{id}/invitaciones
    Entonces la respuesta es 201 con un código de 8 caracteres y su vencimiento
    Y la tanda pasa a RECLUTANDO

  Escenario: Otro organizador intenta generar un código
    Dado una tanda de "organizador1"
    Cuando otro ORGANIZADOR hace POST /api/tandas/{id}/invitaciones
    Entonces la respuesta es 403

  Escenario: Unirse con un código válido
    Dado una tanda en RECLUTANDO con cupo libre
    Cuando "participante1" hace POST /api/tandas/unirse con el código
    Entonces la respuesta es 200
    Y "participante1" aparece como miembro

  Escenario: Unirse dos veces
    Dado que "participante1" ya es miembro
    Cuando vuelve a usar el código
    Entonces la respuesta es 409

  Escenario: Cupo lleno
    Dado una tanda con el cupo completo
    Cuando otro participante usa el código
    Entonces la respuesta es 409

  Escenario: Código inválido o vencido
    Cuando un participante usa un código que no existe o venció
    Entonces la respuesta es 404

  Escenario: Ver una tanda ajena cambiando el id
    Dado que "participante2" no es miembro de la tanda X
    Cuando hace GET /api/tandas/{X}
    Entonces la respuesta es 403

  Escenario: Mis tandas
    Dado que "participante1" es miembro de 2 tandas
    Cuando hace GET /api/tandas/mias
    Entonces recibe exactamente esas 2 tandas

  Escenario: Cancelar una tanda activa
    Dado una tanda en ACTIVA
    Cuando su organizador intenta cancelarla
    Entonces la respuesta es 409
```

## Endpoints

| Método y endpoint | Rol | Respuestas |
|---|---|---|
| `POST /api/tandas` | ORGANIZADOR | 201 · 400 · 403 |
| `GET /api/tandas/mias` | PARTICIPANTE, ORGANIZADOR | 200 |
| `GET /api/tandas/{id}` | Miembros y dueño | 200 · 403 |
| `POST /api/tandas/{id}/invitaciones` | ORGANIZADOR dueño | 201 · 403 · 409 |
| `POST /api/tandas/unirse` | PARTICIPANTE | 200 · 404 · 409 |
| `POST /api/tandas/{id}/cancelar` | ORGANIZADOR dueño | 200 · 403 · 409 |

`POST /api/tandas/{id}/cancelar` no está en la tabla de endpoints del documento del proyecto; se agrega porque el estado CANCELADA necesita una forma de alcanzarse. **Confirmar con el equipo.**

## Fuera de alcance

- Editar reglas pactadas, salir de una tanda o expulsar miembros.
- Compartir el código directo a WhatsApp (se copia al portapapeles).
