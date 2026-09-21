
import pytest

from validaciones import validar_fecha_opcional


def test_fecha_valida():
    resultado = validar_fecha_opcional("25/09/2026")

    assert resultado == "25/09/2026"


def test_fecha_vacia():
    resultado = validar_fecha_opcional("")

    assert resultado == ""


def test_fecha_invalida():
    with pytest.raises(ValueError):
        validar_fecha_opcional("40/09/2026")


def test_fecha_bisiesta():
    resultado = validar_fecha_opcional("29/02/2024")

    assert resultado == "29/02/2024"


def test_fecha_bisiesta_invalida():
    with pytest.raises(ValueError):
        validar_fecha_opcional("29/02/2025")