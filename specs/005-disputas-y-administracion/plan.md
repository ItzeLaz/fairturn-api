# 005 · Disputas, historial y administración — Plan técnico

## Dominio
- `Disputa`: pagoId, tandaId, abiertaPor, motivo, arbitroId, estado (State: `Abierta`, `EnRevision`, `Resuelta`), decision, motivoResolucion.
- `ReglaConflictoInteres` (servicio de dominio): un árbitro no puede ser miembro de la tanda.
- `HistorialCumplimiento`: valor calculado, no tabla propia.
- Puerto `GestorIdentidad`: `agregarRol`, `quitarRol`, `buscarUsuarios`, `listarUsuariosConRol`.
- Eventos: `DisputaAbierta`, `DisputaResuelta`.

## Casos de uso
`AbrirDisputa`, `AsignarArbitro` (automático y manual), `ListarMisDisputas`, `ObtenerDisputa`, `ResolverDisputa`, `ConsultarHistorial`, `CambiarRol`, `BuscarUsuarios`, `ConsultarIndicadores`.

## Infraestructura
- **Keycloak Admin API:** cliente confidencial `fairturn-api-admin` con *service account* y el rol `realm-management/manage-users`. Se usa el cliente REST de Spring (o `keycloak-admin-client`) en `infrastructure.identidad.KeycloakGestorIdentidad`. El secreto del cliente va en `.env`.
- **Historial:** consulta agregada sobre `pago`, `disputa`, `membresia` y `entrada_bitacora` (tipo `NO_REVELO`).

## Persistencia (Flyway)
- `V5__disputas.sql`: `disputa(id, pago_id, tanda_id, abierta_por, motivo, arbitro_sub, estado, decision, motivo_resolucion, abierta_en, resuelta_en)`; índice parcial único sobre `pago_id` donde `estado <> 'RESUELTA'`.

## Despliegue
- `Dockerfile` multi-stage (Maven → JRE 21), como en el documento del proyecto.
- `docker-compose.yml` final con `postgres`, `keycloak-db`, `keycloak` y `backend`; volúmenes con nombre; `restart: unless-stopped`; `depends_on` con `condition: service_healthy`.
- `.env.example` con todas las variables.
- Realm exportado actualizado con el cliente `fairturn-api-admin`.

## App
- `features/disputas/`: abrir disputa desde un pago; para ARBITRO, lista, detalle con evidencia y resolver.
- `features/perfil/`: mi historial y el de otros miembros desde el detalle de la tanda.
- `features/admin/`: buscar usuario, cambiar rol, asignar árbitro, indicadores.

## Pruebas
- Conflicto de interés en asignación automática y manual.
- Visibilidad por rol y propiedad en todos los endpoints.
- Historial con datos preparados.
- Recorrido completo con dos emuladores (guion del Anexo A.8).
