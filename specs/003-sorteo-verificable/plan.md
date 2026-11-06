# 003 · Sorteo verificable — Plan técnico

## Sprint 1: algoritmo y vectores

| Pieza | Dónde | Notas |
|---|---|---|
| Algoritmo de referencia | `specs/003-sorteo-verificable/referencia/sorteo_referencia.py` | Genera y verifica `vectores.json` |
| Implementación Java | `com.fairturn.domain.sorteo.AlgoritmoSorteo` | Clase pura, sin Spring; usa el puerto `GeneradorHash` |
| Adaptador de hash | `com.fairturn.infrastructure.hash.Sha256GeneradorHash` | `MessageDigest.getInstance("SHA-256")` |
| Pruebas Java | `src/test/.../AlgoritmoSorteoVectoresTest` | JUnit 5 parametrizado que lee `vectores.json` |
| Implementación Dart | `fairturn-app/lib/features/sorteo/domain/algoritmo_sorteo.dart` | Paquete `crypto` (`sha256.convert(utf8.encode(...))`) |
| Pruebas Dart | `fairturn-app/test/sorteo/algoritmo_sorteo_test.dart` | Lee una copia de `vectores.json` en `test/fixtures/` |

`vectores.json` se copia a `fairturn-app/test/fixtures/`. Si cambia, se actualiza en los dos repos en el mismo sprint.

## Sprint 3: protocolo completo

### Dominio
- Entidades: `Sorteo` (fase, plazos, semilla, orden), `Compromiso` (idParticipante, hash, secretoRevelado).
- Fases como enum con transiciones validadas: `COMPROMISO → REVELACION → CALCULADO`, y `REVELACION → REINICIADO`.
- Estrategia de asignación de turnos (patrón Strategy): `EstrategiaTurnos` con `SorteoVerificable` y `OrdenPorAcuerdo`.
- Eventos de dominio: `SorteoIniciado`, `CompromisoPublicado`, `SecretoRevelado`, `NoRevelo`, `SorteoReiniciado`, `SorteoEjecutado`.

### Casos de uso
`IniciarSorteo`, `PublicarCompromiso`, `RevelarSecreto`, `CerrarFasePorPlazo` (programado), `EjecutarSorteo`, `ObtenerVerificacion`, `GenerarRondas`.

### Persistencia (Flyway)
- `sorteo(id, tanda_id, fase, plazo_compromiso, plazo_revelacion, semilla, intento, creado_en)`
- `compromiso(id, sorteo_id, participante_id, hash, secreto, revelado_en)` — único por `(sorteo_id, participante_id)`
- `sorteo_orden(sorteo_id, posicion, participante_id)`

### App
- `features/sorteo/`: generar secreto con `Random.secure()`, guardarlo con clave `sorteo_<idTanda>_<intento>` en `flutter_secure_storage`, publicar compromiso, revelar y pantalla "Verificar sorteo" con las tres comprobaciones (R9).
- Al terminar el sorteo, borrar el secreto guardado.

### Pruebas
- Dominio: vectores + transiciones de fase + reinicio con menos de 2 revelaciones.
- Web: escenarios 200 / 403 / 409 / 422 de la spec.
- App: misma prueba de vectores y prueba del flujo de verificación con datos simulados.

## Riesgos

- **Diferencias Java/Dart** → vectores compartidos y comparación paso a paso.
- **El usuario pierde el secreto** (reinstala la app) → no podrá revelar; cuenta como `NO_REVELO`. Se avisa en la pantalla.
