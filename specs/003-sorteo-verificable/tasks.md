# 003 · Sorteo verificable — Tareas

Marca con `[x]` al terminar y pon el enlace al PR o commit.

## Sprint 1 · Edward · `feature/algoritmo-sorteo`
- [ ] T01 Revisar y aprobar la sección "Algoritmo exacto" de `spec.md`
- [ ] T02 Ejecutar `python3 referencia/sorteo_referencia.py --verificar`
- [ ] T03 `AlgoritmoSorteo` en Java (dominio puro) + puerto `GeneradorHash`
- [ ] T04 Prueba JUnit parametrizada que lee `vectores.json`
- [ ] T05 `algoritmo_sorteo.dart` con el paquete `crypto`
- [ ] T06 Prueba Dart que lee la copia de `vectores.json`
- [ ] T07 `mvn test` y `flutter test` pasando con los 4 casos

## Sprint 3 · Responsable: ______
- [ ] T08 Migraciones `sorteo`, `compromiso`, `sorteo_orden`
- [ ] T09 Casos de uso `IniciarSorteo`, `PublicarCompromiso`, `RevelarSecreto`
- [ ] T10 Tarea programada de cierre de fases por plazo (puerto `Reloj`)
- [ ] T11 `EjecutarSorteo` + `GenerarRondas` y paso de la tanda a ACTIVA
- [ ] T12 Endpoints de compromiso, revelación y verificación
- [ ] T13 Eventos de dominio del sorteo hacia la bitácora
- [ ] T14 App: generar y guardar secreto, comprometer y revelar
- [ ] T15 App: pantalla "Verificar sorteo" (R9)
- [ ] T16 Pruebas de los escenarios 200 / 403 / 409 / 422

## Verificación final
- [ ] Backend y app producen el mismo orden con las mismas entradas
- [ ] El secreto sobrevive al cierre de la app
- [ ] `openapi.yaml` coincide con Swagger
- [ ] Rama fusionada a `develop`
