# 002 · Tandas y membresías — Plan técnico

## Dominio (`com.fairturn.domain.tanda`)
- `Tanda`: id, dueño (`sub`), reglas pactadas (objeto de valor `ReglasPactadas`), estado, creadoEn.
- `Membresia`: tandaId, participanteId (`sub`), unidoEn.
- `CodigoInvitacion`: tandaId, código, venceEn, activo.
- **Patrón State:** interfaz `EstadoTanda` con `invitar()`, `unir()`, `iniciarSorteo()`, `activar()`, `finalizar()`, `cancelar()`. Clases `Borrador`, `Reclutando`, `EnSorteo`, `Activa`, `Finalizada`, `Cancelada`. Lo no permitido lanza `TransicionNoPermitida` → 409.
- Puertos: `TandaRepositorio`, `MembresiaRepositorio`, `GeneradorCodigo`, `Reloj`.

## Casos de uso (`application`)
`CrearTanda`, `GenerarInvitacion`, `UnirseATanda`, `ListarMisTandas`, `ObtenerTanda`, `CancelarTanda`, `RegistrarUsuarioLocal`.

Cada caso de uso recibe el `sub` del usuario autenticado y valida propiedad **dentro del caso de uso**, no solo en el controlador.

## Persistencia (Flyway)
- `V2__usuarios_y_tandas.sql`:
  - `usuario(sub PK, username, nombre, actualizado_en)`
  - Ajustar `tanda`: `dueno_sub`, `monto NUMERIC(12,2)`, `periodicidad`, `numero_participantes`, `plazo_gracia_dias`, `estado`
  - `membresia(tanda_id, participante_sub, unido_en)` con PK compuesta
  - `codigo_invitacion(codigo PK, tanda_id, vence_en, activo)`

## Web
- `TandaController` con `@PreAuthorize` por rol y DTOs (`CrearTandaRequest`, `TandaResumen`, `TandaDetalle`, `InvitacionResponse`, `UnirseRequest`).
- MapStruct para entidad ↔ DTO.
- `@RestControllerAdvice` que convierte excepciones del dominio a `ProblemDetail` (400 / 403 / 404 / 409).

## App (`features/tandas/`)
- Organizador: crear tanda, ver código y copiarlo.
- Participante: unirse con código, lista "Mis tandas", detalle con miembros y estado.
- Menú distinto por rol (ya existe desde el Sprint 1).

## Pruebas
- Unitarias del patrón State: todas las transiciones válidas e inválidas.
- Integración web: cada escenario de la spec, incluido cambiar el id en la URL con otro usuario.
