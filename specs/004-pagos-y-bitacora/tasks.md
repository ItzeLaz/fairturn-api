# 004 · Pagos, mora y bitácora — Tareas

Responsables por definir en el Sprint Planning.

- [ ] T01 Migración `V4__rondas_pagos_bitacora.sql` — ______
- [ ] T02 `CadenaBitacora` en Java con prueba de `vectores-bitacora.json` — ______
- [ ] T03 `CadenaBitacora` en Dart con la misma prueba — ______
- [ ] T04 Suscriptor de eventos → entrada de bitácora (misma transacción) — ______
- [ ] T05 Generación de rondas y pagos PENDIENTE al activar la tanda — ______
- [ ] T06 `DeclararPago` + `POST /api/rondas/{id}/pagos` — ______
- [ ] T07 `ConfirmarPago` + `PATCH /api/pagos/{id}/confirmar` — ______
- [ ] T08 `DetectarMora` programado con puerto `Reloj` — ______
- [ ] T09 Cierre de ronda y paso de la tanda a FINALIZADA — ______
- [ ] T10 `GET` de rondas, pagos, bitácora y verificación — ______
- [ ] T11 App: rondas, declarar y confirmar pagos — ______
- [ ] T12 App: bitácora, verificación local y último hash guardado — ______
- [ ] T13 Pruebas de los escenarios de la spec — ______
- [ ] T14 Demostración de alteración con `psql` (captura) — ______

## Verificación final
- [ ] Quien paga no puede confirmarse a sí mismo; solo el receptor confirma
- [ ] Cada evento relevante genera su entrada en la bitácora
- [ ] Alterar una entrada en la base hace que la verificación señale la primera entrada alterada
- [ ] La mora se registra al vencer el plazo de gracia (probado con el puerto Reloj)
- [ ] Rama fusionada a `develop`
