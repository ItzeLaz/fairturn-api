#!/usr/bin/env python3
"""
Implementación de referencia de la bitácora encadenada de Fairturn.

Genera ../vectores-bitacora.json con una cadena íntegra y la misma cadena
con una entrada alterada. Java y Dart deben dar los mismos hashes y detectar
la misma primera entrada alterada. Solo usa la biblioteca estándar.

Uso:
    python3 bitacora_referencia.py              # genera el archivo
    python3 bitacora_referencia.py --verificar  # recalcula y compara
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

SEP = "|"
HASH_INICIAL = "0" * 64


def hash_entrada(hash_previo: str, tipo: str, contenido: str, marca: str) -> str:
    texto = hash_previo + SEP + tipo + SEP + contenido + SEP + marca
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def encadenar(entradas: list) -> list:
    previo = HASH_INICIAL
    cadena = []
    for n, e in enumerate(entradas, start=1):
        h = hash_entrada(previo, e["tipo"], e["contenido"], e["marcaDeTiempo"])
        cadena.append({"secuencia": n, **e, "hashPrevio": previo, "hash": h})
        previo = h
    return cadena


def verificar(cadena: list) -> dict:
    previo = HASH_INICIAL
    for e in cadena:
        recalculado = hash_entrada(previo, e["tipo"], e["contenido"], e["marcaDeTiempo"])
        if e["hashPrevio"] != previo or e["hash"] != recalculado:
            return {"integra": False, "primeraAlterada": e["secuencia"]}
        previo = e["hash"]
    return {"integra": True, "primeraAlterada": None}


ENTRADAS = [
    {"tipo": "TANDA_CREADA",
     "contenido": '{"idTanda":"7f3c2a10-5b1e-4c8d-9a2f-0e6b4d8c1a01","monto":"500.00","periodicidad":"SEMANAL","numeroParticipantes":4}',
     "marcaDeTiempo": "2026-11-06T22:15:30.123Z"},
    {"tipo": "MIEMBRO_UNIDO",
     "contenido": '{"idParticipante":"a1000000-0000-4000-8000-000000000002"}',
     "marcaDeTiempo": "2026-11-06T22:16:02.004Z"},
    {"tipo": "PAGO_DECLARADO",
     "contenido": '{"idPago":"e5000000-0000-4000-8000-000000000001","referencia":"Depósito | 09:15 · Ana"}',
     "marcaDeTiempo": "2026-11-13T15:15:00.000Z"},
    {"tipo": "PAGO_CONFIRMADO",
     "contenido": '{"idPago":"e5000000-0000-4000-8000-000000000001"}',
     "marcaDeTiempo": "2026-11-13T18:40:12.500Z"},
]


def construir() -> dict:
    integra = encadenar(ENTRADAS)
    alterada = copy.deepcopy(integra)
    # Simula a alguien que cambia en la base el monto de la primera entrada
    # sin recalcular hashes.
    alterada[0]["contenido"] = alterada[0]["contenido"].replace('"500.00"', '"50.00"')
    # Y a alguien que, además, recalcula el hash de la entrada 3 para ocultar
    # un cambio: la cadena se rompe en la 4.
    reconstruida = copy.deepcopy(integra)
    reconstruida[2]["contenido"] = reconstruida[2]["contenido"].replace("Ana", "Luis")
    reconstruida[2]["hash"] = hash_entrada(reconstruida[2]["hashPrevio"], reconstruida[2]["tipo"],
                                           reconstruida[2]["contenido"], reconstruida[2]["marcaDeTiempo"])
    return {
        "version": 1,
        "algoritmo": "Ver specs/004-pagos-y-bitacora/spec.md, seccion 'Encadenamiento exacto'",
        "hashInicial": HASH_INICIAL,
        "casos": [
            {"nombre": "cadena integra", "cadena": integra, "esperado": verificar(integra)},
            {"nombre": "contenido alterado en la entrada 1", "cadena": alterada, "esperado": verificar(alterada)},
            {"nombre": "entrada 3 alterada con su hash recalculado", "cadena": reconstruida, "esperado": verificar(reconstruida)},
        ],
    }


def main() -> None:
    destino = Path(__file__).resolve().parent.parent / "vectores-bitacora.json"
    resultado = construir()
    if "--verificar" in sys.argv:
        ok = json.loads(destino.read_text(encoding="utf-8")) == resultado
        print("vectores-bitacora.json coincide" if ok else "vectores-bitacora.json NO coincide")
        sys.exit(0 if ok else 1)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for c in resultado["casos"]:
        print(f"- {c['nombre']}: {c['esperado']}")
    print(f"Escrito: {destino}")


if __name__ == "__main__":
    main()
