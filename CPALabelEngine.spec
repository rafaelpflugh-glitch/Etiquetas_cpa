# -*- mode: python ; coding: utf-8 -*-

"""
CPA Label Engine
================

Build do programa principal + motor de etiquetas.

Estrutura final esperada:

CPALabelEngine\
│
├── CPALabelEngine.exe
├── gerar_etiquetas_pdf.exe
├── CPA_logo_completo.png
├── CPA_logo_simbolo.png
│
└── _internal\
    ├── ...
    └── motor\
        └── libreoffice\
            └── program\
                └── soffice.exe

Copyright (c) 2026 Rafael Pflug.
Todos os direitos reservados.
"""


from pathlib import Path

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_all


# ============================================================
# CAMINHOS
# ============================================================

BASE = Path(
    r"C:\Users\pflug\Etiquetas_Inbetta"
)

MOTOR = (
    BASE /
    "distribuicao" /
    "motor"
)

ICONE = (
    BASE /
    "CPA_LOGO_SIMBOLO.ico"
)


# ============================================================
# VALIDAÇÃO DOS ARQUIVOS PRINCIPAIS
# ============================================================

INTERFACE = (
    BASE /
    "interface_etiquetas.py"
)

MOTOR_SCRIPT = (
    MOTOR /
    "gerar_etiquetas_pdf.py"
)

LOGO_COMPLETO = (
    BASE /
    "CPA_logo_completo.png"
)

LOGO_SIMBOLO = (
    BASE /
    "CPA_logo_simbolo.png"
)

LIBREOFFICE_DIR = (
    MOTOR /
    "libreoffice"
)


# ============================================================
# LOGOS DA INTERFACE
#
# Os PNGs ficarão na raiz da distribuição:
#
#     CPALabelEngine\
#         CPALabelEngine.exe
#         gerar_etiquetas_pdf.exe
#         CPA_logo_completo.png
#         CPA_logo_simbolo.png
#
# ============================================================

logo_datas = [

    (
        str(LOGO_COMPLETO),
        "."
    ),

    (
        str(LOGO_SIMBOLO),
        "."
    ),

]


# ============================================================
# COLETA DO PyMuPDF
# ============================================================

pymupdf_datas, pymupdf_binaries, pymupdf_hiddenimports = (
    collect_all("pymupdf")
)


# ============================================================
# COLETA DO OpenPyXL
# ============================================================

openpyxl_datas, openpyxl_binaries, openpyxl_hiddenimports = (
    collect_all("openpyxl")
)


# ============================================================
# COLETA DO PILLOW
#
# A interface utiliza:
#
#     from PIL import Image, ImageTk
#
# Portanto o Pillow também entra explicitamente no build.
# ============================================================

pillow_datas, pillow_binaries, pillow_hiddenimports = (
    collect_all("PIL")
)


# ============================================================
# HIDDEN IMPORTS DO MOTOR
# ============================================================

motor_hiddenimports = []

motor_hiddenimports += pymupdf_hiddenimports
motor_hiddenimports += openpyxl_hiddenimports


# ============================================================
# DATAS DO MOTOR
# ============================================================

motor_datas = []

motor_datas += pymupdf_datas
motor_datas += openpyxl_datas


# ============================================================
# BINÁRIOS DO MOTOR
# ============================================================

motor_binaries = []

motor_binaries += pymupdf_binaries
motor_binaries += openpyxl_binaries


# ============================================================
# ============================================================
# BUILD DO MOTOR
# ============================================================
# ============================================================

motor_analysis = Analysis(

    [
        str(MOTOR_SCRIPT)
    ],

    pathex=[
        str(BASE),
        str(MOTOR)
    ],

    binaries=motor_binaries,

    datas=motor_datas,

    hiddenimports=motor_hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,

)


# ============================================================
# PYZ DO MOTOR
# ============================================================

motor_pyz = PYZ(
    motor_analysis.pure
)


# ============================================================
# EXE DO MOTOR
# ============================================================

motor_exe = EXE(

    motor_pyz,

    motor_analysis.scripts,

    motor_analysis.binaries,

    motor_analysis.datas,

    [],

    name="gerar_etiquetas_pdf",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    console=False,

)


# ============================================================
# ============================================================
# BUILD DA INTERFACE
# ============================================================
# ============================================================

interface_analysis = Analysis(

    [
        str(INTERFACE)
    ],

    pathex=[
        str(BASE)
    ],

    binaries=pillow_binaries,

    datas=(
        logo_datas
        + pillow_datas
    ),

    hiddenimports=pillow_hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,

)


# ============================================================
# PYZ DA INTERFACE
# ============================================================

interface_pyz = PYZ(
    interface_analysis.pure
)


# ============================================================
# EXE PRINCIPAL
# ============================================================

interface_exe = EXE(

    interface_pyz,

    interface_analysis.scripts,

    interface_analysis.binaries,

    interface_analysis.datas,

    [],

    name="CPALabelEngine",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    console=False,

    icon=str(ICONE),

)


# ============================================================
# ============================================================
# COLETA FINAL
# ============================================================
# ============================================================

coll = COLLECT(

    # --------------------------------------------------------
    # PROGRAMA PRINCIPAL
    # --------------------------------------------------------

    interface_exe,

    # --------------------------------------------------------
    # MOTOR
    #
    # Fica diretamente na raiz da distribuição.
    # --------------------------------------------------------

    motor_exe,

    # --------------------------------------------------------
    # BINÁRIOS E DATAS DA INTERFACE
    #
    # Inclui Pillow e os logos.
    # --------------------------------------------------------

    interface_analysis.binaries,

    interface_analysis.datas,

    # --------------------------------------------------------
    # BINÁRIOS E DATAS DO MOTOR
    #
    # Inclui PyMuPDF e OpenPyXL.
    # --------------------------------------------------------

    motor_analysis.binaries,

    motor_analysis.datas,

    # --------------------------------------------------------
    # LIBREOFFICE EMBARCADO
    #
    # Resultado:
    #
    # _internal\
    #     motor\
    #         libreoffice\
    #
    # --------------------------------------------------------

    Tree(

        str(LIBREOFFICE_DIR),

        prefix="motor/libreoffice"

    ),

    strip=False,

    upx=True,

    name="CPALabelEngine",

)