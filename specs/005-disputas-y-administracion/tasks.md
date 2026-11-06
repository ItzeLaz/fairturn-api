# 005 · Disputas, historial y administración — Tareas

Responsables por definir en el Sprint Planning.

## Disputas
- [ ] T01 Migración `V5__disputas.sql` — ______
- [ ] T02 `AbrirDisputa` + asignación automática con conflicto de interés — ______
- [ ] T03 `ListarMisDisputas`, `ObtenerDisputa` con evidencia — ______
- [ ] T04 `ResolverDisputa` y efecto en el pago — ______

## Historial y administración
- [ ] T05 `ConsultarHistorial` con regla de visibilidad — ______
- [ ] T06 Cliente `fairturn-api-admin` en Keycloak + adaptador `GestorIdentidad` — ______
- [ ] T07 `CambiarRol`, `BuscarUsuarios`, asignación manual de árbitro — ______
- [ ] T08 Indicadores de tandas y disputas — ______

## App
- [ ] T09 Abrir disputa y pantallas del árbitro — ______
- [ ] T10 Pantalla de historial — ______
- [ ] T11 Pantallas del administrador — ______

## Cierre
- [ ] T12 `Dockerfile` multi-stage y servicio `backend` en el compose — ______
- [ ] T13 `.env.example` completo y realm exportado actualizado — ______
- [ ] T14 README con instrucciones completas — ______
- [ ] T15 Pruebas de todos los escenarios — ______
- [ ] T16 Ensayo de la demostración con dos emuladores (video) — ______
- [ ] T17 `release/1.0.0` → `main` con tag `v1.0.0` y de vuelta a `develop` — ______

## Verificación final
- [ ] Un árbitro solo ve sus disputas y no puede mediar en una tanda donde es miembro
- [ ] `docker compose up -d --build` levanta todo desde cero
- [ ] Los datos sobreviven a `docker compose down` + `up`
- [ ] La sesión de la app y los secretos sobreviven al cerrar la app
- [ ] Recorrido de demostración completo con dos emuladores
