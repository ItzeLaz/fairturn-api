# 003 · Sorteo verificable

**Estado:** borrador · **Sprints:** 1 (algoritmo y vectores) y 3 (protocolo completo)

## Objetivo

Que el orden de los turnos no lo decida ni lo manipule una sola persona, y que cualquier miembro pueda **recalcularlo en su propio celular** y obtener exactamente el mismo resultado que el servidor.

## Historias de usuario

- Como **PARTICIPANTE**, quiero aportar un secreto al sorteo y poder comprobar después cómo se calculó el orden, para confiar en que nadie lo manipuló.
- Como **ORGANIZADOR**, quiero iniciar el sorteo cuando el cupo esté completo, sin poder influir en el resultado.

## Fases del sorteo

```
COMPROMISO ──► REVELACION ──► CALCULADO
     ▲              │
     └── REINICIADO ┘   (si revelan menos de 2)
```

1. **Compromiso.** El ORGANIZADOR dueño inicia el sorteo (la tanda pasa de RECLUTANDO a SORTEO). Cada miembro genera un secreto **en su dispositivo**, lo guarda con `flutter_secure_storage` y envía solo su compromiso.
2. **Cierre de compromisos.** Cuando todos comprometieron o vence el plazo, el servidor publica todos los compromisos y pasa a REVELACION.
3. **Revelación.** Cada miembro envía su secreto. El servidor comprueba que `compromiso(idTanda, idParticipante, secreto)` coincida con lo publicado.
4. **Resultado.** Cuando todos revelaron o vence el plazo, el servidor calcula la semilla y el orden, genera las rondas y la tanda pasa a ACTIVA.
5. **Verificación.** Cualquier miembro descarga los datos públicos y la app recalcula todo.

## Algoritmo exacto

Esta sección es normativa: Java, Dart y el script de referencia deben implementarla **igual, byte por byte**.

### Convenciones

- **Codificación:** todo texto se convierte a bytes con **UTF-8**.
- **Separador:** el carácter `|` (U+007C). Ningún id ni secreto puede contenerlo; si lo contiene se rechaza con 422.
- **Hash:** SHA-256. Su resultado se expresa en **hexadecimal minúsculo de 64 caracteres**.
- **Ids:** UUID en su forma canónica en minúsculas (`a1000000-0000-4000-8000-000000000001`). El `idParticipante` es el claim `sub` del usuario.
- **Orden de ids:** comparación lexicográfica de las cadenas (`String.compareTo` en Java y Dart). Como los ids son ASCII, ambos lenguajes dan el mismo orden.
- **Secreto que genera la app:** 32 bytes de `Random.secure()` en hexadecimal minúsculo (64 caracteres). El algoritmo acepta cualquier texto UTF-8 sin `|`; los vectores incluyen acentos y emoji para probarlo.

### 1. Compromiso

```
compromiso = hex( SHA-256( UTF8( idTanda + "|" + idParticipante + "|" + secreto ) ) )
```

### 2. Semilla

Sea `R` la lista de miembros que **revelaron correctamente**, ordenada por `idParticipante`.

```
semilla = hex( SHA-256( UTF8( idTanda + "|" + secreto(R[0]) + "|" + secreto(R[1]) + ... ) ) )
```

Si `R` tiene menos de 2 miembros, no se calcula semilla y el sorteo se reinicia.

### 3. Entero de 4 bytes sin signo

```
u32(semilla, i) = primeros 4 bytes de SHA-256( UTF8( semilla + "|" + i ) )
                  interpretados como entero SIN SIGNO big-endian (0 .. 4 294 967 295)
```

`i` se escribe en decimal sin ceros a la izquierda. `semilla` es el texto hexadecimal, no los bytes crudos.

**Importante en Java:** `byte` tiene signo. Hay que usar `long` y la máscara `& 0xFF`:

```java
long r = ((long)(d[0] & 0xFF) << 24) | ((d[1] & 0xFF) << 16) | ((d[2] & 0xFF) << 8) | (d[3] & 0xFF);
```

En Dart (Android) `int` es de 64 bits y los bytes ya son 0–255, así que no hay problema. El vector "cuatro participantes" incluye un valor mayor que 2³¹ para detectar el error.

### 4. Permutación (Fisher–Yates determinista)

Sea `M` la lista de **todos los miembros** de la tanda (revelaran o no), ordenada por `idParticipante`, con `n` elementos.

```
para i desde n-1 hasta 1:
    j = u32(semilla, i) mod (i + 1)
    intercambiar M[i] y M[j]
```

El resultado es el orden de turnos: `M[0]` cobra en la ronda 1, `M[1]` en la ronda 2, etc.

Con grupos de hasta 20 personas, el sesgo del módulo es menor que 1 en 200 millones; se considera despreciable y se declara.

### Vectores de prueba

`vectores.json` tiene 4 casos generados por `referencia/sorteo_referencia.py`:

| Caso | Qué prueba |
|---|---|
| Cuatro participantes | Caso base; incluye un entero mayor que 2³¹ |
| Mínimo de dos | Límite inferior |
| Acentos, eñe y emoji | Codificación UTF-8 |
| Cinco miembros, uno no revela | Quien no revela no entra a la semilla, pero sí tiene turno |

Para cada caso se dan las entradas y lo esperado: compromisos, semilla, enteros `u32` intermedios y orden final. Las pruebas de **Java (JUnit)** y **Dart (`flutter test`)** leen el mismo archivo. Si un lenguaje falla, comparar primero los compromisos, luego la semilla y luego los enteros para encontrar el paso exacto que difiere.

Para regenerar o verificar: `python3 referencia/sorteo_referencia.py [--verificar]`.

## Reglas

- **R1.** Solo el ORGANIZADOR dueño puede iniciar el sorteo, y solo con la tanda en RECLUTANDO y el cupo completo.
- **R2.** Solo los miembros de la tanda pueden comprometer, revelar y ver la verificación.
- **R3.** Un miembro compromete y revela una sola vez por sorteo.
- **R4.** El servidor nunca recibe el secreto antes de la fase de REVELACION.
- **R5.** Un miembro que no comprometió o no reveló a tiempo queda fuera de la semilla, **conserva su turno** y se registra `NO_REVELO` en la bitácora, lo que afecta su historial.
- **R6.** Si revelan menos de 2 miembros, se registra `SORTEO_REINICIADO` y empieza un sorteo nuevo en COMPROMISO.
- **R7.** Los plazos de cada fase se cierran con una tarea programada (`@Scheduled`) usando el puerto `Reloj`.
- **R8.** El cálculo vive en el dominio (sin Spring) detrás del puerto `GeneradorHash`.
- **R9.** La pantalla "Verificar sorteo" comprueba: (a) que **mi compromiso aparece** en la lista publicada, (b) que cada secreto revelado coincide con su compromiso y (c) que la semilla y el orden recalculados son idénticos a los del servidor.

## Escenarios de aceptación

```gherkin
# language: es
Característica: Sorteo verificable

  Escenario: Iniciar el sorteo con el cupo completo
    Dado una tanda en RECLUTANDO con el cupo completo
    Cuando su organizador hace POST /api/tandas/{id}/iniciar-sorteo
    Entonces la respuesta es 200
    Y la tanda pasa a SORTEO y el sorteo a fase COMPROMISO

  Escenario: Iniciar el sorteo con cupo incompleto
    Dado una tanda en RECLUTANDO a la que le falta un miembro
    Cuando su organizador intenta iniciar el sorteo
    Entonces la respuesta es 409

  Escenario: Otro usuario intenta iniciar el sorteo
    Dado un ORGANIZADOR que no es dueño de la tanda
    Cuando intenta iniciar el sorteo
    Entonces la respuesta es 403

  Escenario: Publicar compromiso
    Dado un sorteo en fase COMPROMISO y un miembro que no ha comprometido
    Cuando envía un compromiso de 64 caracteres hexadecimales
    Entonces la respuesta es 200

  Escenario: Compromiso repetido
    Dado un miembro que ya publicó su compromiso
    Cuando intenta publicar otro
    Entonces la respuesta es 409

  Escenario: La revelación coincide con el compromiso
    Dado un sorteo en fase REVELACION y un miembro que publicó su compromiso
    Cuando envía un secreto cuyo compromiso coincide
    Entonces la respuesta es 200

  Escenario: La revelación no coincide
    Dado un miembro que publicó su compromiso
    Cuando envía un secreto cuyo compromiso no coincide
    Entonces la respuesta es 422 y la revelación no cuenta

  Escenario: Revelación fuera de fase
    Dado un sorteo que aún está en fase COMPROMISO
    Cuando un miembro intenta revelar su secreto
    Entonces la respuesta es 409

  Escenario: Usuario ajeno a la tanda
    Dado un PARTICIPANTE que no es miembro de la tanda
    Cuando intenta comprometer, revelar o ver la verificación
    Entonces la respuesta es 403

  Escenario: Resultado con un miembro que no revela
    Dado una tanda de 5 miembros donde 4 revelaron y vence el plazo
    Cuando el servidor calcula el resultado
    Entonces la semilla usa solo los 4 secretos revelados
    Y el orden incluye a los 5 miembros
    Y la bitácora registra NO_REVELO para el quinto
    Y la tanda pasa a ACTIVA con sus rondas generadas

  Escenario: Menos de dos revelaciones
    Dado que al vencer el plazo de revelación solo un miembro reveló
    Cuando el servidor cierra la fase
    Entonces el sorteo se reinicia en fase COMPROMISO
    Y la bitácora registra SORTEO_REINICIADO

  Escenario: Verificar en el dispositivo
    Dado un sorteo CALCULADO
    Cuando un miembro abre "Verificar sorteo"
    Entonces la app comprueba que su compromiso aparece en la lista
    Y recalcula compromisos, semilla y orden
    Y muestra "Coincide" si todo es idéntico al servidor

  Escenario: El secreto sobrevive al cierre de la app
    Dado un miembro que publicó su compromiso
    Cuando cierra y vuelve a abrir la app antes de revelar
    Entonces la app conserva su secreto y puede revelarlo
```

## Endpoints

| Método y endpoint | Rol | Respuestas |
|---|---|---|
| `POST /api/tandas/{id}/iniciar-sorteo` | ORGANIZADOR dueño | 200 · 403 · 409 |
| `POST /api/tandas/{id}/sorteo/compromiso` | Miembro | 200 · 400 · 403 · 409 |
| `POST /api/tandas/{id}/sorteo/revelacion` | Miembro | 200 · 403 · 409 · 422 |
| `GET /api/tandas/{id}/sorteo/verificacion` | Miembro | 200 · 403 |

Detalle de cuerpos y respuestas en `specs/openapi.yaml`.

## Limitaciones declaradas

- Quien revela al final puede decidir no revelar y así elegir entre dos resultados. Se mitiga con el registro `NO_REVELO` y el historial; no se impide del todo.
- El servidor es de confianza parcial: un miembro solo detecta que se omitió su compromiso si revisa la lista publicada. La pantalla de verificación lo hace automáticamente.

## Pendiente de decidir

- Duración de cada fase (propuesta: 24 h; en modo demostración, 2 min).
- Estrategia alternativa "orden por acuerdo" (patrón Strategy): se deja preparada la interfaz, sin pantalla en esta versión.
