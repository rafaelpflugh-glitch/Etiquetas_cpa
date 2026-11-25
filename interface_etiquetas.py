#!/usr/bin/env python3

"""
CPA Label Engine
================

Sistema de geração de etiquetas para impressão.

Copyright (c) 2026 Rafael Pflug.
Todos os direitos reservados.

Projeto: Grupo CPA - Soluções Inteligentes
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


# ============================================================
# IDENTIFICAÇÃO / COPYRIGHT
# ============================================================

APP_NAME = "CPA Label Engine"
APP_VERSION = "1.0.0"

APP_COPYRIGHT = (
    "Copyright (c) 2026 Rafael Pflug. Todos os direitos reservados."
)

APP_COMPANY = "Grupo CPA - Soluções Inteligentes"


# ============================================================
# PILLOW
# ============================================================

try:
    from PIL import Image, ImageTk

    PILLOW_DISPONIVEL = True

except ImportError:

    PILLOW_DISPONIVEL = False


# ============================================================
# DIRETÓRIOS
# ============================================================

if getattr(sys, "frozen", False):

    BASE_DIR = Path(sys.executable).resolve().parent
    INTERNAL_DIR = BASE_DIR / "_internal"
    MODO_EMPACOTADO = True

else:

    BASE_DIR = Path(__file__).resolve().parent
    INTERNAL_DIR = BASE_DIR
    MODO_EMPACOTADO = False


# ============================================================
# ASSETS / LOGOS
# ============================================================

def localizar_asset(nome: str) -> Path | None:

    """
    Localiza um arquivo visual da CPA.

    Desenvolvimento:
        procura primeiro na Área de Trabalho.

    Distribuição:
        procura dentro de assets junto ao programa.
    """

    candidatos = []

    # --------------------------------------------------------
    # DISTRIBUIÇÃO
    # --------------------------------------------------------

    if MODO_EMPACOTADO:

        candidatos.extend([
        INTERNAL_DIR / "assets" / nome,
        INTERNAL_DIR / nome,
        BASE_DIR / "assets" / nome,
        BASE_DIR / nome,
    ])

    # --------------------------------------------------------
    # DESENVOLVIMENTO
    # --------------------------------------------------------

    else:

        desktop = Path.home() / "Desktop"

        candidatos.extend([
            desktop / nome,
            BASE_DIR / "assets" / nome,
            BASE_DIR / nome,
        ])

    for caminho in candidatos:

        try:

            if caminho.exists() and caminho.is_file():

                return caminho.resolve()

        except Exception:

            pass

    return None


LOGO_COMPLETO = localizar_asset(
    "CPA_logo_completo.png"
)

LOGO_SIMBOLO = localizar_asset(
    "CPA_logo_simbolo.png"
)


# ============================================================
# FUNÇÃO DE CARREGAMENTO DE LOGO COM ALTA QUALIDADE
# ============================================================

def carregar_logo_redimensionado(
    caminho: Path,
    max_width: int,
    max_height: int
):
    """
    Carrega um PNG e redimensiona mantendo proporção.

    A imagem original nunca é alterada.

    Quando Pillow está disponível, utiliza uma redução
    progressiva antes da redução final com LANCZOS.

    A transparência original é preservada sempre que possível.

    Fallback:
        utiliza o PhotoImage nativo do Tkinter.
    """

    if caminho is None:
        return None

    # --------------------------------------------------------
    # PILLOW
    # --------------------------------------------------------

    if PILLOW_DISPONIVEL:

        try:

            imagem = Image.open(caminho)

            if imagem.mode not in ("RGBA", "RGB"):

                imagem = imagem.convert("RGBA")

            largura, altura = imagem.size

            if largura <= 0 or altura <= 0:
                return None

            # ------------------------------------------------
            # CÁLCULO DE PROPORÇÃO
            # ------------------------------------------------

            fator = min(
                max_width / largura,
                max_height / altura,
                1.0
            )

            nova_largura = max(
                1,
                int(round(largura * fator))
            )

            nova_altura = max(
                1,
                int(round(altura * fator))
            )

            # ------------------------------------------------
            # REDUÇÃO PROGRESSIVA
            # ------------------------------------------------

            while (
                imagem.width > nova_largura * 2
                or imagem.height > nova_altura * 2
            ):

                largura_intermediaria = max(
                    nova_largura,
                    int(imagem.width * 0.5)
                )

                altura_intermediaria = max(
                    nova_altura,
                    int(imagem.height * 0.5)
                )

                imagem = imagem.resize(
                    (
                        largura_intermediaria,
                        altura_intermediaria
                    ),
                    Image.Resampling.BOX
                )

            # ------------------------------------------------
            # REDUÇÃO FINAL
            # ------------------------------------------------

            if (
                imagem.width != nova_largura
                or imagem.height != nova_altura
            ):

                imagem = imagem.resize(
                    (
                        nova_largura,
                        nova_altura
                    ),
                    Image.Resampling.LANCZOS
                )

            # ------------------------------------------------
            # GARANTE ALPHA CORRETO
            # ------------------------------------------------

            if imagem.mode != "RGBA":

                imagem = imagem.convert("RGBA")

            return ImageTk.PhotoImage(imagem)

        except Exception:

            pass

    # --------------------------------------------------------
    # FALLBACK TKINTER
    # --------------------------------------------------------

    try:

        imagem = tk.PhotoImage(
            file=str(caminho)
        )

        largura = imagem.width()
        altura = imagem.height()

        if largura <= 0 or altura <= 0:
            return None

        fator = min(
            max_width / largura,
            max_height / altura,
            1.0
        )

        if fator < 1:

            reducao = max(
                1,
                int(round(1 / fator))
            )

            imagem = imagem.subsample(
                reducao,
                reducao
            )

        return imagem

    except Exception:

        return None


# ============================================================
# LOCALIZAÇÃO DO MOTOR
# ============================================================

def localizar_motor() -> Path | None:

    if MODO_EMPACOTADO:

        candidatos = [

            BASE_DIR /
            "gerar_etiquetas_pdf.exe",

            INTERNAL_DIR /
            "motor" /
            "gerar_etiquetas_pdf.exe",

            BASE_DIR /
            "motor" /
            "gerar_etiquetas_pdf.exe",

            BASE_DIR /
            "distribuicao" /
            "motor" /
            "gerar_etiquetas_pdf.exe",

        ]

    else:

        candidatos = [

            BASE_DIR /
            "gerar_etiquetas_pdf.py",

            BASE_DIR /
            "motor" /
            "gerar_etiquetas_pdf.py",

            BASE_DIR /
            "distribuicao" /
            "motor" /
            "gerar_etiquetas_pdf.py",

        ]

    for caminho in candidatos:

        try:

            if caminho.exists() and caminho.is_file():

                return caminho.resolve()

        except Exception:

            pass

    return None


# ============================================================
# LOCALIZAÇÃO DO LIBREOFFICE
# ============================================================

def localizar_libreoffice() -> Path | None:

    candidatos = [

        INTERNAL_DIR /
        "motor" /
        "libreoffice" /
        "program" /
        "soffice.exe",

        BASE_DIR /
        "motor" /
        "libreoffice" /
        "program" /
        "soffice.exe",

        BASE_DIR /
        "distribuicao" /
        "motor" /
        "libreoffice" /
        "program" /
        "soffice.exe",

        BASE_DIR /
        "_internal" /
        "motor" /
        "libreoffice" /
        "program" /
        "soffice.exe",

    ]

    for caminho in candidatos:

        try:

            if caminho.exists() and caminho.is_file():

                return caminho.resolve()

        except Exception:

            pass

    # --------------------------------------------------------
    # LOCAIS PADRÃO DO WINDOWS
    # --------------------------------------------------------

    caminhos_windows = [

        Path(
            os.environ.get(
                "PROGRAMFILES",
                r"C:\Program Files"
            )
        )
        / "LibreOffice"
        / "program"
        / "soffice.exe",

        Path(
            os.environ.get(
                "PROGRAMFILES(X86)",
                r"C:\Program Files (x86)"
            )
        )
        / "LibreOffice"
        / "program"
        / "soffice.exe",

        Path(
            os.environ.get(
                "LOCALAPPDATA",
                ""
            )
        )
        / "Programs"
        / "LibreOffice"
        / "program"
        / "soffice.exe",

    ]

    for caminho in caminhos_windows:

        try:

            if caminho.exists() and caminho.is_file():

                return caminho.resolve()

        except Exception:

            pass

    # --------------------------------------------------------
    # PATH
    # --------------------------------------------------------

    try:

        resultado = subprocess.run(
            ["where", "soffice.exe"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt"
                else 0
            )
        )

        if resultado.returncode == 0:

            for linha in resultado.stdout.splitlines():

                linha = linha.strip()

                if linha:

                    caminho = Path(linha)

                    if caminho.exists():

                        return caminho.resolve()

    except Exception:

        pass

    return None


# ============================================================
# PYTHON
# ============================================================

def localizar_python() -> Path | None:

    if not MODO_EMPACOTADO:

        caminho = Path(sys.executable)

        if caminho.exists():

            return caminho

    python_commands = [

        "python.exe",
        "python",
        "py.exe",
        "py",

    ]

    for comando in python_commands:

        try:

            resultado = subprocess.run(
                [
                    comando,
                    "--version"
                ],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if os.name == "nt"
                    else 0
                )
            )

            if resultado.returncode == 0:

                return Path(comando)

        except Exception:

            pass

    local_appdata = os.environ.get(
        "LOCALAPPDATA",
        ""
    )

    caminhos = [

        Path(local_appdata)
        / "Programs"
        / "Python"
        / "Python311"
        / "python.exe",

        Path(local_appdata)
        / "Programs"
        / "Python"
        / "Python312"
        / "python.exe",

        Path(local_appdata)
        / "Programs"
        / "Python"
        / "Python313"
        / "python.exe",

        Path(local_appdata)
        / "Programs"
        / "Python"
        / "Python314"
        / "python.exe",

    ]

    for caminho in caminhos:

        if caminho.exists():

            return caminho

    return None


# ============================================================
# CONFIGURAÇÃO
# ============================================================

APPDATA = os.environ.get("APPDATA")

if APPDATA:

    CONFIG_DIR = Path(APPDATA) / "CPA"

else:

    CONFIG_DIR = Path.home() / ".cpa"


CONFIG_FILE = (
    CONFIG_DIR /
    "cpa_label_engine_config.json"
)


# ============================================================
# CORES
# ============================================================

BG = "#0B1118"
BG_PANEL = "#131C25"
BG_PANEL_2 = "#19242F"
BG_SELECTED = "#1C3044"
BORDER = "#2A3948"
BORDER_SELECTED = "#3D6B91"

TEXT = "#F1F4F7"
TEXT_SECONDARY = "#B4C0CB"
TEXT_MUTED = "#788694"

ACCENT = "#4C8FBD"
ACCENT_HOVER = "#5FA4D3"

SUCCESS = "#55B88A"
ERROR = "#D86E76"
WARNING = "#C9A85C"

WHITE = "#FFFFFF"


# ============================================================
# FONTES
# ============================================================

FONT_BRAND = (
    "Segoe UI",
    22,
    "bold"
)

FONT_TITLE = (
    "Segoe UI",
    11,
    "bold"
)

FONT_SUBTITLE = (
    "Segoe UI",
    9
)

FONT_SECTION = (
    "Segoe UI",
    10,
    "bold"
)

FONT_NORMAL = (
    "Segoe UI",
    10
)

FONT_SMALL = (
    "Segoe UI",
    8
)

FONT_FOOTER = (
    "Segoe UI",
    7
)

FONT_BUTTON = (
    "Segoe UI",
    10,
    "bold"
)

FONT_FORMAT = (
    "Segoe UI",
    12,
    "bold"
)


# ============================================================
# PRESETS
# ============================================================

PRESETS = {

    "100 × 100 mm": {

        "largura": 100,
        "altura": 100,
        "descricao": "Etiqueta quadrada"

    },

    "100 × 60 mm": {

        "largura": 100,
        "altura": 60,
        "descricao": "Etiqueta horizontal"

    },

}


# ============================================================
# APLICAÇÃO
# ============================================================

class CPALabelEngine(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(APP_NAME)

        self.geometry(
            "760x720"
        )

        self.minsize(
            700,
            670
        )

        self.configure(
            bg=BG
        )

        self.resizable(
            True,
            True
        )

        self.excel_path = None

        self.formato_atual = (
            "100 × 100 mm"
        )

        self.output_dir = (
            self._carregar_pasta_destino()
        )

        self.status_var = tk.StringVar(
            value="Selecione um arquivo Excel."
        )

        self.arquivo_var = tk.StringVar(
            value="Nenhum arquivo selecionado"
        )

        if self.output_dir is not None:

            destino_inicial = str(
                self.output_dir
            )

        else:

            destino_inicial = (
                "Nenhuma pasta selecionada"
            )

        self.destino_var = tk.StringVar(
            value=destino_inicial
        )

        self.formato_var = tk.StringVar(
            value=self.formato_atual
        )

        # ----------------------------------------------------
        # REFERÊNCIAS DOS LOGOS
        # ----------------------------------------------------

        self.logo_completo_img = None
        self.logo_simbolo_img = None

        # ----------------------------------------------------
        # SPLASH
        # ----------------------------------------------------

        self.withdraw()

        self._mostrar_splash()

        self._build_interface()

        self._carregar_arquivo_excel()

        self.after(
            3000,
            self._finalizar_splash
        )


    # ========================================================
    # SPLASH
    # ========================================================

    def _mostrar_splash(self):

        self.splash = tk.Toplevel(self)

        self.splash.overrideredirect(True)

        self.splash.configure(
            bg=BG
        )

        largura = 900
        altura = 430

        largura_tela = (
            self.splash.winfo_screenwidth()
        )

        altura_tela = (
            self.splash.winfo_screenheight()
        )

        x = (
            largura_tela - largura
        ) // 2

        y = (
            altura_tela - altura
        ) // 2

        self.splash.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

        self.splash.update_idletasks()

        # ----------------------------------------------------
        # LOGO COMPLETO
        # ----------------------------------------------------

        if LOGO_COMPLETO is not None:

            try:

                self.logo_completo_img = (
                    carregar_logo_redimensionado(
                        LOGO_COMPLETO,
                        820,
                        350
                    )
                )

                if self.logo_completo_img is not None:

                    tk.Label(
                        self.splash,
                        image=self.logo_completo_img,
                        bg=BG,
                        bd=0
                    ).pack(
                        expand=True
                    )

                else:

                    raise RuntimeError(
                        "Não foi possível carregar o logo."
                    )

            except Exception:

                tk.Label(
                    self.splash,
                    text="CPA",
                    bg=BG,
                    fg=TEXT,
                    font=(
                        "Segoe UI",
                        42,
                        "bold"
                    )
                ).pack(
                    expand=True
                )

        else:

            tk.Label(
                self.splash,
                text="CPA",
                bg=BG,
                fg=TEXT,
                font=(
                    "Segoe UI",
                    42,
                    "bold"
                )
            ).pack(
                expand=True
            )


    def _finalizar_splash(self):

        try:

            if self.splash.winfo_exists():

                self.splash.destroy()

        except Exception:

            pass

        self.deiconify()

        self.lift()

        self.focus_force()


    # ========================================================
    # CONFIGURAÇÃO
    # ========================================================

    def _carregar_configuracao(self):

        try:

            if not CONFIG_FILE.exists():

                return {}

            with open(
                CONFIG_FILE,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(
                    arquivo
                )

            if isinstance(dados, dict):

                return dados

        except Exception:

            pass

        return {}


    def _salvar_configuracao(self):

        try:

            CONFIG_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            dados = {}

            if self.output_dir is not None:

                dados["output_dir"] = str(
                    self.output_dir
                )

            if self.excel_path is not None:

                dados["excel_path"] = str(
                    self.excel_path
                )

            with open(
                CONFIG_FILE,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    dados,
                    arquivo,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception:

            pass


    def _carregar_pasta_destino(self):

        dados = self._carregar_configuracao()

        pasta = dados.get(
            "output_dir"
        )

        if not pasta:

            return None

        try:

            caminho = Path(pasta)

            if (
                caminho.exists()
                and caminho.is_dir()
            ):

                return caminho

        except Exception:

            pass

        return None


    def _carregar_arquivo_excel(self):

        dados = self._carregar_configuracao()

        arquivo = dados.get(
            "excel_path"
        )

        if not arquivo:

            return

        try:

            caminho = Path(arquivo)

            if (
                caminho.exists()
                and caminho.is_file()
            ):

                self.excel_path = caminho

                self.arquivo_var.set(
                    caminho.name
                )

                self._set_status(
                    "Último arquivo Excel recuperado.",
                    "normal"
                )

        except Exception:

            pass


    # ========================================================
    # INTERFACE
    # ========================================================

    def _build_interface(self):

        header = tk.Frame(
            self,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=42,
            pady=(25, 13)
        )

        marca_frame = tk.Frame(
            header,
            bg=BG
        )

        marca_frame.pack(
            side="left"
        )

        # ----------------------------------------------------
        # LOGO/SÍMBOLO CPA
        # ----------------------------------------------------

        if LOGO_SIMBOLO is not None:

            try:

                self.logo_simbolo_img = (
                    carregar_logo_redimensionado(
                        LOGO_SIMBOLO,
                        58,
                        58
                    )
                )

                if self.logo_simbolo_img is not None:

                    tk.Label(
                        marca_frame,
                        image=self.logo_simbolo_img,
                        bg=BG,
                        bd=0
                    ).pack(
                        side="left",
                        padx=(0, 14)
                    )

            except Exception:

                pass

        # ----------------------------------------------------
        # TEXTOS DO PROGRAMA
        # ----------------------------------------------------

        textos_marca = tk.Frame(
            marca_frame,
            bg=BG
        )

        textos_marca.pack(
            side="left"
        )

        tk.Label(
            textos_marca,
            text="CPA",
            bg=BG,
            fg=TEXT,
            font=FONT_BRAND
        ).pack(
            anchor="w"
        )

        tk.Label(
            textos_marca,
            text="LABEL ENGINE",
            bg=BG,
            fg=ACCENT,
            font=FONT_TITLE
        ).pack(
            anchor="w",
            pady=(0, 2)
        )

        tk.Label(
            textos_marca,
            text="Geração de etiquetas para impressão",
            bg=BG,
            fg=TEXT_SECONDARY,
            font=FONT_SUBTITLE
        ).pack(
            anchor="w"
        )

        # ----------------------------------------------------
        # SOBRE
        # ----------------------------------------------------

        tk.Button(
            header,
            text="Sobre",
            command=self.mostrar_sobre,
            bg=BG_PANEL_2,
            fg=TEXT_SECONDARY,
            activebackground=BORDER,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            font=FONT_NORMAL
        ).pack(
            side="right",
            anchor="n",
            pady=4
        )

        self._build_flow()

        content = tk.Frame(
            self,
            bg=BG
        )

        content.pack(
            fill="both",
            expand=True,
            padx=42,
            pady=(0, 5)
        )

        self._build_excel_section(content)
        self._build_format_section(content)
        self._build_destination_section(content)
        self._build_action_section(content)
        self._build_status_section(content)
        self._build_footer()


    # ========================================================
    # SOBRE
    # ========================================================

    def mostrar_sobre(self):

        janela = tk.Toplevel(self)

        janela.title(
            f"Sobre - {APP_NAME}"
        )

        janela.configure(
            bg=BG
        )

        janela.resizable(
            False,
            False
        )

        largura = 500
        altura = 480

        self.update_idletasks()

        x = (
            self.winfo_x()
            + (
                self.winfo_width()
                - largura
            ) // 2
        )

        y = (
            self.winfo_y()
            + (
                self.winfo_height()
                - altura
            ) // 2
        )

        janela.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

        janela.transient(self)

        container = tk.Frame(
            janela,
            bg=BG_PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        container.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        logo_sobre = None

        if LOGO_COMPLETO is not None:

            try:

                logo_sobre = (
                    carregar_logo_redimensionado(
                        LOGO_COMPLETO,
                        420,
                        145
                    )
                )

                if logo_sobre is not None:

                    janela.logo_sobre = logo_sobre

                    tk.Label(
                        container,
                        image=logo_sobre,
                        bg=BG_PANEL,
                        bd=0
                    ).pack(
                        pady=(22, 20)
                    )

                else:

                    raise RuntimeError(
                        "Logo não pôde ser carregado."
                    )

            except Exception:

                tk.Label(
                    container,
                    text="CPA",
                    bg=BG_PANEL,
                    fg=TEXT,
                    font=(
                        "Segoe UI",
                        25,
                        "bold"
                    )
                ).pack(
                    pady=(28, 0)
                )

        else:

            tk.Label(
                container,
                text="CPA",
                bg=BG_PANEL,
                fg=TEXT,
                font=(
                    "Segoe UI",
                    25,
                    "bold"
                )
            ).pack(
                pady=(28, 0)
            )

            tk.Label(
                container,
                text="LABEL ENGINE",
                bg=BG_PANEL,
                fg=ACCENT,
                font=(
                    "Segoe UI",
                    11,
                    "bold"
                )
            ).pack(
                pady=(0, 18)
            )

        tk.Label(
            container,
            text=(
                "Sistema desenvolvido para facilitar a "
                "geração de etiquetas a partir de arquivos "
                "Excel, produzindo arquivos PDF prontos "
                "para impressão."
            ),
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 10),
            justify="center",
            wraplength=390
        ).pack(
            padx=30,
            pady=(0, 22)
        )

        tk.Frame(
            container,
            bg=BORDER,
            height=1
        ).pack(
            fill="x",
            padx=55,
            pady=(0, 20)
        )

        tk.Label(
            container,
            text=APP_COMPANY,
            bg=BG_PANEL,
            fg=TEXT,
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            justify="center",
            wraplength=390
        ).pack(
            padx=25,
            pady=(0, 8)
        )

        tk.Label(
            container,
            text="Desenvolvido por Rafael Pflug",
            bg=BG_PANEL,
            fg=ACCENT,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        ).pack(
            pady=(0, 6)
        )

        tk.Label(
            container,
            text=APP_COPYRIGHT,
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=FONT_SMALL,
            justify="center",
            wraplength=400
        ).pack(
            pady=(0, 4)
        )

        tk.Label(
            container,
            text=f"Versão {APP_VERSION}",
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=FONT_SMALL
        ).pack(
            pady=(0, 15)
        )

        fechar = tk.Button(
            container,
            text="FECHAR",
            command=janela.destroy,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            padx=30,
            pady=8,
            cursor="hand2",
            font=FONT_BUTTON
        )

        fechar.pack(
            pady=(0, 18)
        )

        janela.bind(
            "<Escape>",
            lambda event: janela.destroy()
        )

        fechar.focus_set()


    # ========================================================
    # FLUXO
    # ========================================================

    def _build_flow(self):

        frame = tk.Frame(
            self,
            bg=BG
        )

        frame.pack(
            fill="x",
            padx=42,
            pady=(0, 16)
        )

        etapas = [
            ("01", "EXCEL"),
            ("02", "ETIQUETA"),
            ("03", "PDF"),
        ]

        for i, (numero, nome) in enumerate(etapas):

            bloco = tk.Frame(
                frame,
                bg=BG
            )

            bloco.pack(
                side="left"
            )

            tk.Label(
                bloco,
                text=numero,
                bg=BG_PANEL_2,
                fg=ACCENT,
                width=3,
                height=1,
                font=(
                    "Segoe UI",
                    8,
                    "bold"
                )
            ).pack(
                side="left"
            )

            tk.Label(
                bloco,
                text=nome,
                bg=BG,
                fg=TEXT_SECONDARY,
                font=(
                    "Segoe UI",
                    8,
                    "bold"
                )
            ).pack(
                side="left",
                padx=(7, 0)
            )

            if i < len(etapas) - 1:

                tk.Label(
                    frame,
                    text="›",
                    bg=BG,
                    fg=TEXT_MUTED,
                    font=(
                        "Segoe UI",
                        13
                    )
                ).pack(
                    side="left",
                    padx=14
                )


    # ========================================================
    # EXCEL
    # ========================================================

    def _build_excel_section(self, parent):

        section = tk.Frame(
            parent,
            bg=BG_PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        section.pack(
            fill="x",
            pady=(0, 10)
        )

        top = tk.Frame(
            section,
            bg=BG_PANEL
        )

        top.pack(
            fill="x",
            padx=20,
            pady=(13, 8)
        )

        tk.Label(
            top,
            text="Arquivo de origem",
            bg=BG_PANEL,
            fg=TEXT,
            font=FONT_SECTION
        ).pack(
            side="left"
        )

        tk.Button(
            top,
            text="Selecionar Excel",
            command=self.selecionar_excel,
            bg=BG_PANEL_2,
            fg=TEXT,
            activebackground=BORDER,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            font=FONT_NORMAL
        ).pack(
            side="right"
        )

        arquivo_frame = tk.Frame(
            section,
            bg=BG_PANEL_2
        )

        arquivo_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 13)
        )

        self.arquivo_label = tk.Label(
            arquivo_frame,
            textvariable=self.arquivo_var,
            bg=BG_PANEL_2,
            fg=TEXT_SECONDARY,
            anchor="w",
            font=FONT_NORMAL
        )

        self.arquivo_label.pack(
            fill="x",
            padx=12,
            pady=8
        )


    # ========================================================
    # FORMATO
    # ========================================================

    def _build_format_section(self, parent):

        section = tk.Frame(
            parent,
            bg=BG_PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        section.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            section,
            text="Formato da etiqueta",
            bg=BG_PANEL,
            fg=TEXT,
            font=FONT_SECTION
        ).pack(
            anchor="w",
            padx=20,
            pady=(13, 9)
        )

        formatos = tk.Frame(
            section,
            bg=BG_PANEL
        )

        formatos.pack(
            fill="x",
            padx=20,
            pady=(0, 13)
        )

        self.formato_buttons = {}

        nomes = list(PRESETS.keys())

        for index, nome in enumerate(nomes):

            dados = PRESETS[nome]

            button = tk.Frame(
                formatos,
                bg=BG_PANEL_2,
                highlightbackground=BORDER,
                highlightthickness=1,
                cursor="hand2"
            )

            button.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(
                    0 if index == 0 else 5,
                    5 if index == 0 else 0
                )
            )

            tamanho = tk.Label(
                button,
                text=nome,
                bg=BG_PANEL_2,
                fg=TEXT,
                font=FONT_FORMAT,
                cursor="hand2"
            )

            tamanho.pack(
                anchor="w",
                padx=15,
                pady=(10, 2)
            )

            descricao = tk.Label(
                button,
                text=dados["descricao"],
                bg=BG_PANEL_2,
                fg=TEXT_MUTED,
                font=FONT_SMALL,
                cursor="hand2"
            )

            descricao.pack(
                anchor="w",
                padx=15,
                pady=(0, 10)
            )

            self.formato_buttons[nome] = button

            for widget in (
                button,
                tamanho,
                descricao
            ):

                widget.bind(
                    "<Button-1>",
                    lambda event, n=nome:
                    self.selecionar_formato(n)
                )

        self._atualizar_formato_visual()


    # ========================================================
    # DESTINO
    # ========================================================

    def _build_destination_section(self, parent):

        section = tk.Frame(
            parent,
            bg=BG_PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        section.pack(
            fill="x",
            pady=(0, 10)
        )

        top = tk.Frame(
            section,
            bg=BG_PANEL
        )

        top.pack(
            fill="x",
            padx=20,
            pady=(13, 8)
        )

        tk.Label(
            top,
            text="Destino do PDF",
            bg=BG_PANEL,
            fg=TEXT,
            font=FONT_SECTION
        ).pack(
            side="left"
        )

        tk.Button(
            top,
            text="Selecionar pasta",
            command=self.alterar_pasta_destino,
            bg=BG_PANEL_2,
            fg=TEXT,
            activebackground=BORDER,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            font=FONT_NORMAL
        ).pack(
            side="right"
        )

        destino_frame = tk.Frame(
            section,
            bg=BG_PANEL_2
        )

        destino_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 13)
        )

        self.destino_label = tk.Label(
            destino_frame,
            textvariable=self.destino_var,
            bg=BG_PANEL_2,
            fg=TEXT_SECONDARY,
            anchor="w",
            font=FONT_NORMAL
        )

        self.destino_label.pack(
            fill="x",
            padx=12,
            pady=8
        )


    # ========================================================
    # AÇÃO
    # ========================================================

    def _build_action_section(self, parent):

        frame = tk.Frame(
            parent,
            bg=BG
        )

        frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.gerar_btn = tk.Button(
            frame,
            text="GERAR PDF",
            command=self.gerar_pdf,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            padx=28,
            pady=11,
            cursor="hand2",
            font=FONT_BUTTON
        )

        self.gerar_btn.pack(
            fill="x"
        )


    # ========================================================
    # STATUS
    # ========================================================

    def _build_status_section(self, parent):

        section = tk.Frame(
            parent,
            bg=BG_PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        section.pack(
            fill="x"
        )

        status_box = tk.Frame(
            section,
            bg=BG_PANEL_2
        )

        status_box.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.status_indicator = tk.Label(
            status_box,
            text="●",
            bg=BG_PANEL_2,
            fg=ACCENT,
            font=(
                "Segoe UI",
                10
            )
        )

        self.status_indicator.pack(
            side="left",
            padx=(12, 5),
            pady=2
        )

        self.status_label = tk.Label(
            status_box,
            textvariable=self.status_var,
            bg=BG_PANEL_2,
            fg=TEXT_SECONDARY,
            anchor="w",
            font=FONT_NORMAL
        )

        self.status_label.pack(
            side="left",
            fill="x",
            expand=True,
            pady=2
        )


    # ========================================================
    # FOOTER
    # ========================================================

    def _build_footer(self):

        footer = tk.Frame(
            self,
            bg=BG,
            height=25
        )

        footer.pack(
            fill="x",
            padx=42,
            pady=(3, 9)
        )

        footer.pack_propagate(False)

        tk.Frame(
            footer,
            bg="#17212B",
            height=1
        ).pack(
            fill="x",
            side="top"
        )

        conteudo = tk.Frame(
            footer,
            bg=BG
        )

        conteudo.pack(
            fill="x",
            expand=True,
            pady=(3, 0)
        )

        tk.Label(
            conteudo,
            text=(
                f"CPA Label Engine  •  "
                f"{APP_VERSION}"
            ),
            bg=BG,
            fg="#53616E",
            font=FONT_FOOTER
        ).pack(
            side="left"
        )

        tk.Label(
            conteudo,
            text=APP_COMPANY,
            bg=BG,
            fg="#4A5865",
            font=FONT_FOOTER
        ).pack(
            side="right"
        )


    # ========================================================
    # SELECIONAR EXCEL
    # ========================================================

    def selecionar_excel(self):

        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[
                (
                    "Arquivos Excel",
                    "*.xlsx"
                ),
                (
                    "Todos os arquivos",
                    "*.*"
                )
            ]
        )

        if not arquivo:

            return

        self.excel_path = Path(
            arquivo
        )

        self.arquivo_var.set(
            self.excel_path.name
        )

        self._salvar_configuracao()

        self._set_status(
            "Arquivo Excel selecionado.",
            "normal"
        )


    # ========================================================
    # ALTERAR DESTINO
    # ========================================================

    def alterar_pasta_destino(self):

        if (
            self.output_dir is not None
            and self.output_dir.exists()
        ):

            initial_dir = str(
                self.output_dir
            )

        else:

            initial_dir = str(
                Path.home()
            )

        pasta = filedialog.askdirectory(
            title="Selecionar pasta para os PDFs",
            initialdir=initial_dir
        )

        if not pasta:

            return

        self.output_dir = Path(
            pasta
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.destino_var.set(
            str(self.output_dir)
        )

        self._salvar_configuracao()

        self._set_status(
            "Pasta de destino atualizada.",
            "normal"
        )


    # ========================================================
    # FORMATO
    # ========================================================

    def selecionar_formato(self, nome):

        self.formato_atual = nome

        self.formato_var.set(
            nome
        )

        self._atualizar_formato_visual()

        dados = PRESETS[nome]

        self._set_status(
            f"Formato selecionado: "
            f"{dados['largura']} × "
            f"{dados['altura']} mm.",
            "normal"
        )


    def _atualizar_formato_visual(self):

        for nome, button in (
            self.formato_buttons.items()
        ):

            widgets = button.winfo_children()

            if nome == self.formato_atual:

                button.configure(
                    bg=BG_SELECTED,
                    highlightbackground=BORDER_SELECTED,
                    highlightthickness=1
                )

                for widget in widgets:

                    widget.configure(
                        bg=BG_SELECTED
                    )

                if len(widgets) >= 1:

                    widgets[0].configure(
                        fg=ACCENT
                    )

                if len(widgets) >= 2:

                    widgets[1].configure(
                        fg=TEXT_SECONDARY
                    )

            else:

                button.configure(
                    bg=BG_PANEL_2,
                    highlightbackground=BORDER,
                    highlightthickness=1
                )

                for widget in widgets:

                    widget.configure(
                        bg=BG_PANEL_2
                    )

                if len(widgets) >= 1:

                    widgets[0].configure(
                        fg=TEXT
                    )

                if len(widgets) >= 2:

                    widgets[1].configure(
                        fg=TEXT_MUTED
                    )


    # ========================================================
    # STATUS
    # ========================================================

    def _set_status(
        self,
        texto,
        tipo="normal"
    ):

        self.status_var.set(
            texto
        )

        if tipo == "success":

            self.status_indicator.configure(
                fg=SUCCESS
            )

            self.status_label.configure(
                fg=TEXT
            )

        elif tipo == "error":

            self.status_indicator.configure(
                fg=ERROR
            )

            self.status_label.configure(
                fg=TEXT
            )

        elif tipo == "warning":

            self.status_indicator.configure(
                fg=WARNING
            )

            self.status_label.configure(
                fg=TEXT
            )

        else:

            self.status_indicator.configure(
                fg=ACCENT
            )

            self.status_label.configure(
                fg=TEXT_SECONDARY
            )


    # ========================================================
    # NOME DE SAÍDA
    # ========================================================

    def _gerar_nome_saida(
        self,
        largura,
        altura
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        nome_base = self.excel_path.stem

        nome = (
            f"{nome_base}_"
            f"{largura}x{altura}mm_"
            f"{timestamp}.pdf"
        )

        caminho = (
            self.output_dir
            / nome
        )

        contador = 1

        while caminho.exists():

            nome = (
                f"{nome_base}_"
                f"{largura}x{altura}mm_"
                f"{timestamp}_"
                f"{contador}.pdf"
            )

            caminho = (
                self.output_dir
                / nome
            )

            contador += 1

        return caminho


    # ========================================================
    # ABRIR PASTA
    # ========================================================

    def _abrir_pasta_com_arquivo(
        self,
        pdf
    ):

        try:

            subprocess.Popen(
                [
                    "explorer",
                    "/select,",
                    str(pdf)
                ]
            )

        except Exception:

            try:

                os.startfile(
                    str(pdf.parent)
                )

            except Exception:

                pass


    # ========================================================
    # GERAR PDF
    # ========================================================

    def gerar_pdf(self):

        if self.excel_path is None:

            messagebox.showwarning(
                "Arquivo não selecionado",
                "Selecione o arquivo Excel antes de gerar o PDF."
            )

            return

        if not self.excel_path.exists():

            messagebox.showerror(
                "Arquivo não encontrado",
                "O arquivo Excel selecionado não existe mais."
            )

            self.excel_path = None

            self.arquivo_var.set(
                "Nenhum arquivo selecionado"
            )

            self._salvar_configuracao()

            return

        if self.output_dir is None:

            messagebox.showwarning(
                "Pasta de destino não selecionada",
                "Selecione a pasta onde os arquivos PDF deverão ser salvos."
            )

            return

        if not self.output_dir.exists():

            try:

                self.output_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

            except Exception as erro:

                messagebox.showerror(
                    "Destino inválido",
                    "Não foi possível acessar a pasta de destino.\n\n"
                    f"{erro}"
                )

                return

        # ----------------------------------------------------
        # MOTOR
        # ----------------------------------------------------

        motor = localizar_motor()

        if motor is None:

            if MODO_EMPACOTADO:

                mensagem_motor = (

                    "Não foi possível localizar o executável "
                    "gerar_etiquetas_pdf.exe.\n\n"

                    "Locais verificados:\n\n"

                    f"{BASE_DIR / 'gerar_etiquetas_pdf.exe'}\n"

                    f"{INTERNAL_DIR / 'motor' / 'gerar_etiquetas_pdf.exe'}\n"

                    f"{BASE_DIR / 'motor' / 'gerar_etiquetas_pdf.exe'}"

                )

            else:

                mensagem_motor = (

                    "Não foi possível localizar o motor "
                    "gerar_etiquetas_pdf.py.\n\n"

                    "Locais verificados:\n\n"

                    f"{BASE_DIR / 'gerar_etiquetas_pdf.py'}\n"

                    f"{BASE_DIR / 'motor' / 'gerar_etiquetas_pdf.py'}\n"

                    f"{BASE_DIR / 'distribuicao' / 'motor' / 'gerar_etiquetas_pdf.py'}"

                )

            messagebox.showerror(
                "Motor não encontrado",
                mensagem_motor
            )

            return

        # ----------------------------------------------------
        # PYTHON
        # ----------------------------------------------------

        python_exe = None

        if motor.suffix.lower() == ".py":

            python_exe = localizar_python()

            if python_exe is None:

                messagebox.showerror(
                    "Python não encontrado",
                    "O motor encontrado é um arquivo Python, "
                    "mas não foi encontrado um interpretador Python "
                    "para executá-lo.\n\n"
                    f"Motor:\n{motor}\n\n"
                    "Instale Python 3.11 ou superior."
                )

                return

        # ----------------------------------------------------
        # LIBREOFFICE
        # ----------------------------------------------------

        libreoffice = localizar_libreoffice()

        if libreoffice is None:

            messagebox.showerror(
                "LibreOffice não encontrado",
                "O LibreOffice necessário para gerar as "
                "etiquetas não foi localizado.\n\n"
                "Verifique se o arquivo existe em:\n\n"
                f"{INTERNAL_DIR / 'motor' / 'libreoffice' / 'program' / 'soffice.exe'}"
            )

            return

        # ----------------------------------------------------
        # FORMATO
        # ----------------------------------------------------

        dados = PRESETS[
            self.formato_atual
        ]

        largura = dados["largura"]
        altura = dados["altura"]

        output_pdf = self._gerar_nome_saida(
            largura,
            altura
        )

        self.gerar_btn.configure(
            state="disabled",
            text="PROCESSANDO..."
        )

        self._set_status(
            "Gerando etiquetas...",
            "normal"
        )

        thread = threading.Thread(
            target=self._executar_motor,
            args=(
                motor,
                python_exe,
                libreoffice,
                largura,
                altura,
                output_pdf
            ),
            daemon=True
        )

        thread.start()


    # ========================================================
    # EXECUTA MOTOR
    # ========================================================

    def _executar_motor(
        self,
        motor,
        python_exe,
        libreoffice,
        largura,
        altura,
        output_pdf
    ):

        try:

            if motor.suffix.lower() == ".exe":

                comando = [

                    str(motor),

                    str(self.excel_path),

                    "--largura",
                    str(largura),

                    "--altura",
                    str(altura),

                    "--saida",
                    str(output_pdf)

                ]

            else:

                comando = [

                    str(python_exe),

                    str(motor),

                    str(self.excel_path),

                    "--largura",
                    str(largura),

                    "--altura",
                    str(altura),

                    "--saida",
                    str(output_pdf)

                ]

            ambiente = os.environ.copy()

            libreoffice_program = (
                libreoffice.parent
            )

            path_atual = ambiente.get(
                "PATH",
                ""
            )

            ambiente["PATH"] = (
                str(libreoffice_program)
                + os.pathsep
                + path_atual
            )

            ambiente[
                "CPA_LIBREOFFICE"
            ] = str(
                libreoffice
            )

            perfil = (
                self.output_dir
                / ".cpa_lo_profile"
            )

            perfil.mkdir(
                parents=True,
                exist_ok=True
            )

            ambiente[
                "CPA_LIBREOFFICE_PROFILE"
            ] = str(
                perfil
            )

            ambiente[
                "CPA_ENGINE_DIR"
            ] = str(
                motor.parent
            )

            creationflags = 0
            startupinfo = None

            if os.name == "nt":

                creationflags = (
                    subprocess.CREATE_NO_WINDOW
                )

                startupinfo = (
                    subprocess.STARTUPINFO()
                )

                startupinfo.dwFlags |= (
                    subprocess.STARTF_USESHOWWINDOW
                )

                startupinfo.wShowWindow = 0

            processo = subprocess.run(

                comando,

                capture_output=True,

                text=True,

                cwd=str(motor.parent),

                env=ambiente,

                encoding="utf-8",

                errors="replace",

                creationflags=creationflags,

                startupinfo=startupinfo

            )

            if processo.returncode != 0:

                erro = (

                    processo.stderr.strip()

                    or processo.stdout.strip()

                    or "Erro desconhecido."

                )

                diagnostico = (

                    "O motor retornou erro.\n\n"

                    f"Motor:\n{motor}\n\n"

                    f"LibreOffice:\n{libreoffice}\n\n"

                    f"Retorno: {processo.returncode}\n\n"

                    f"Mensagem:\n{erro}"

                )

                self.after(
                    0,
                    lambda:
                    self._finalizar_erro(
                        diagnostico
                    )
                )

                return

            if not output_pdf.exists():

                saida = (
                    processo.stdout.strip()
                )

                erro_saida = (
                    processo.stderr.strip()
                )

                diagnostico = (

                    "O motor terminou sem erro, "
                    "mas o PDF não foi encontrado.\n\n"

                    f"Esperado:\n{output_pdf}\n\n"

                    f"Saída do motor:\n{saida}\n\n"

                    f"Erro do motor:\n{erro_saida}"

                )

                self.after(
                    0,
                    lambda:
                    self._finalizar_erro(
                        diagnostico
                    )
                )

                return

            self.after(
                0,
                lambda:
                self._finalizar_sucesso(
                    output_pdf
                )
            )

        except Exception as erro:

            self.after(
                0,
                lambda:
                self._finalizar_erro(
                    str(erro)
                )
            )


    # ========================================================
    # SUCESSO
    # ========================================================

    def _finalizar_sucesso(
        self,
        pdf
    ):

        self.gerar_btn.configure(
            state="normal",
            text="GERAR PDF"
        )

        self._set_status(
            "PDF gerado com sucesso.",
            "success"
        )

        resposta = messagebox.askyesno(
            "Etiqueta gerada",
            "O PDF foi gerado com sucesso.\n\n"
            f"{pdf.name}\n\n"
            "Deseja abrir a pasta do arquivo?"
        )

        if resposta:

            self._abrir_pasta_com_arquivo(
                pdf
            )


    # ========================================================
    # ERRO
    # ========================================================

    def _finalizar_erro(
        self,
        erro
    ):

        self.gerar_btn.configure(
            state="normal",
            text="GERAR PDF"
        )

        self._set_status(
            "Não foi possível gerar o PDF.",
            "error"
        )

        messagebox.showerror(
            "Erro ao gerar PDF",
            erro
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    app = CPALabelEngine()

    app.mainloop()
