# 004 · Pagos, mora y bitácora — Plan técnico

## Dominio
- `Ronda`: tandaId, numero, receptorId, fechas, estado.
- `Pago`: rondaId, pagadorId, referencia, estado (patrón State: `Pendiente`, `Declarado`, `Confirmado`, `EnDisputa`, `NoValidado`), moraRegistrada, declaradoEn, confirmadoEn.
- `EntradaBitacora`: tandaId, secuencia, tipo, contenido, marcaDeTiempo, hashPrevio, hash.
- `CadenaBitacora` (servicio de dominio puro): `calcularHash(...)` y `verificar(List<EntradaBitacora>)`. Usa el puerto `GeneradorHash`, el mismo del sorteo.
- Eventos de dominio: `PagoDeclarado`, `PagoConfirmado`, `MoraRegistrada`, `TandaFinalizada`.

## Casos de uso
`ListarRondas`, `ListarPagosDeRonda`, `DeclararPago`, `ConfirmarPago`, `DetectarMora` (programado), `CerrarRondaSiCorresponde`, `RegistrarEnBitacora` (suscriptor de eventos), `ObtenerBitacora`, `VerificarBitacora`.

## Bitácora: detalles de implementación
- El suscriptor usa `@TransactionalEventListener(phase = BEFORE_COMMIT)` para que la entrada se guarde en la misma transacción que el cambio. Si falla la bitácora, falla la operación.
- **Concurrencia:** para agregar una entrada se bloquea la fila de la tanda (`SELECT … FOR UPDATE`) y se lee la última entrada. La restricción única `(tanda_id, secuencia)` evita dos entradas con la misma posición.
- `contenido` se serializa una sola vez con Jackson y se guarda como texto. `marcaDeTiempo` se formatea con `DateTimeFormatter.ISO_INSTANT` truncado a milisegundos (siempre 3 decimales).

## Persistencia (Flyway)
- `V4__rondas_pagos_bitacora.sql`:
  - `ronda(id, tanda_id, numero, receptor_sub, fecha_inicio, fecha_vencimiento, fecha_limite_gracia, estado)`
  - `pago(id, ronda_id, pagador_sub, referencia, estado, mora_registrada, declarado_en, confirmado_en)`
  - `entrada_bitacora(id, tanda_id, secuencia, tipo, contenido TEXT, marca_tiempo TEXT, hash_previo CHAR(64), hash CHAR(64))`, único `(tanda_id, secuencia)`

## App
- `features/pagos/`: lista de rondas, declarar pago, "Pagos recibidos" con botón Confirmar.
- `features/bitacora/` (dentro de tandas): lista de entradas, "Verificar bitácora" que recalcula en el teléfono con los mismos vectores, y guardado del último hash visto en `flutter_secure_storage`.

## Pruebas
- `CadenaBitacora` en Java y Dart con `vectores-bitacora.json`.
- Mora con `Reloj` simulado.
- Escenarios 200 / 403 / 409 de la spec.
- Demostración: alterar una fila con `psql` y verificar que se detecta (captura para la bitácora del sprint).
