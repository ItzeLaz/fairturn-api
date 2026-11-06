#!/usr/bin/env python3
"""
Implementación de referencia del sorteo verificable de Fairturn.

Es la "tercera implementación" independiente: sirve para generar los
resultados esperados de vectores.json. Java y Dart deben producir
exactamente lo mismo. Solo usa la biblioteca estándar.

Uso:
    python3 sorteo_referencia.py              # genera ../vectores.json
    python3 sorteo_referencia.py --verificar  # recalcula y compara con ../vectores.json
"""
import hashlib
import json
import sys
from pathlib import Path

SEP = "|"


def sha256_hex(texto: str) -> str:
    """SHA-256 del texto codificado en UTF-8, en hexadecimal minúsculo."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def compromiso(id_tanda: str, id_participante: str, secreto: str) -> str:
    for valor in (id_tanda, id_participante, secreto):
        if SEP in valor:
            raise ValueError("Ningún valor puede contener el separador '|'")
    return sha256_hex(id_tanda + SEP + id_participante + SEP + secreto)


def semilla(id_tanda: str, revelaciones: dict) -> str:
    """revelaciones: {idParticipante: secreto} solo de quienes revelaron."""
    if len(revelaciones) < 2:
        raise ValueError("Se necesitan al menos 2 revelaciones; el sorteo se reinicia")
    partes = [id_tanda] + [revelaciones[p] for p in sorted(revelaciones)]
    return sha256_hex(SEP.join(partes))


def entero_u32(semilla_hex: str, i: int) -> int:
    """Primeros 4 bytes de SHA-256(semilla|i) como entero sin signo big-endian."""
    digest = hashlib.sha256((semilla_hex + SEP + str(i)).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big", signed=False)


def permutacion(semilla_hex: str, miembros: list) -> list:
    """Fisher-Yates determinista sobre los miembros ordenados por id."""
    orden = sorted(miembros)
    for i in range(len(orden) - 1, 0, -1):
        j = entero_u32(semilla_hex, i) % (i + 1)
        orden[i], orden[j] = orden[j], orden[i]
    return orden


# ---------------------------------------------------------------- casos
CASOS = [
    {
        "nombre": "cuatro participantes, todos revelan",
        "idTanda": "7f3c2a10-5b1e-4c8d-9a2f-0e6b4d8c1a01",
        "participantes": [
            {"id": "a1000000-0000-4000-8000-000000000001", "secreto": "3f9a1c7e5b2d4f6a8c0e1b3d5f7a9c2e4b6d8f0a1c3e5b7d9f2a4c6e8b0d1f3a"},
            {"id": "a1000000-0000-4000-8000-000000000002", "secreto": "c4e6a8b0d2f4a6c8e0b2d4f6a8c0e2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6"},
            {"id": "a1000000-0000-4000-8000-000000000003", "secreto": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"},
            {"id": "a1000000-0000-4000-8000-000000000004", "secreto": "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"},
        ],
    },
    {
        "nombre": "minimo de dos participantes",
        "idTanda": "7f3c2a10-5b1e-4c8d-9a2f-0e6b4d8c1a02",
        "participantes": [
            {"id": "b2000000-0000-4000-8000-000000000001", "secreto": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
            {"id": "b2000000-0000-4000-8000-000000000002", "secreto": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
        ],
    },
    {
        "nombre": "secreto con acentos y enie (prueba UTF-8)",
        "idTanda": "7f3c2a10-5b1e-4c8d-9a2f-0e6b4d8c1a03",
        "participantes": [
            {"id": "c3000000-0000-4000-8000-000000000001", "secreto": "mañana ahorramos más 💰"},
            {"id": "c3000000-0000-4000-8000-000000000002", "secreto": "canción-azúcar-pingüino"},
            {"id": "c3000000-0000-4000-8000-000000000003", "secreto": "Ñandú áéíóú ÁÉÍÓÚ"},
        ],
    },
    {
        "nombre": "cinco miembros, uno no revela (sigue teniendo turno)",
        "idTanda": "7f3c2a10-5b1e-4c8d-9a2f-0e6b4d8c1a04",
        "participantes": [
            {"id": "d4000000-0000-4000-8000-000000000001", "secreto": "1111111111111111111111111111111111111111111111111111111111111111"},
            {"id": "d4000000-0000-4000-8000-000000000002", "secreto": None},
            {"id": "d4000000-0000-4000-8000-000000000003", "secreto": "3333333333333333333333333333333333333333333333333333333333333333"},
            {"id": "d4000000-0000-4000-8000-000000000004", "secreto": "4444444444444444444444444444444444444444444444444444444444444444"},
            {"id": "d4000000-0000-4000-8000-000000000005", "secreto": "5555555555555555555555555555555555555555555555555555555555555555"},
        ],
    },
]


def calcular(caso: dict) -> dict:
    id_tanda = caso["idTanda"]
    miembros = [p["id"] for p in caso["participantes"]]
    revelaciones = {p["id"]: p["secreto"] for p in caso["participantes"] if p["secreto"] is not None}
    s = semilla(id_tanda, revelaciones)
    n = len(miembros)
    return {
        "nombre": caso["nombre"],
        "entrada": {
            "idTanda": id_tanda,
            "participantes": caso["participantes"],
        },
        "esperado": {
            "compromisos": {pid: compromiso(id_tanda, pid, sec) for pid, sec in revelaciones.items()},
            "semilla": s,
            "enterosU32": {str(i): entero_u32(s, i) for i in range(n - 1, 0, -1)},
            "orden": permutacion(s, miembros),
        },
    }


def main() -> None:
    destino = Path(__file__).resolve().parent.parent / "vectores.json"
    resultado = {
        "version": 1,
        "algoritmo": "Ver specs/003-sorteo-verificable/spec.md, seccion 'Algoritmo exacto'",
        "casos": [calcular(c) for c in CASOS],
    }
    if "--verificar" in sys.argv:
        guardado = json.loads(destino.read_text(encoding="utf-8"))
        ok = guardado == resultado
        print("vectores.json coincide" if ok else "vectores.json NO coincide")
        sys.exit(0 if ok else 1)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for c in resultado["casos"]:
        print(f"- {c['nombre']}")
        print(f"  semilla: {c['esperado']['semilla']}")
        print(f"  orden:   {c['esperado']['orden']}")
    print(f"Escrito: {destino}")


if __name__ == "__main__":
    main()
