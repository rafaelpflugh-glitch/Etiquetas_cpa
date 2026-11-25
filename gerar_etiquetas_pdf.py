#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font


# ============================================================
# GERADOR DE ETIQUETAS INBETTA
# ============================================================
#
# Motor:
#   XLSX -> LibreOffice -> PDF -> PyMuPDF -> PDF final
#
# PRODUÃ‡ÃƒO:
#   O LibreOffice poderÃ¡ ser embarcado junto do programa.
#
# DESENVOLVIMENTO:
#   Se o LibreOffice embarcado nÃ£o existir, o motor aceita
#   uma instalaÃ§Ã£o local do LibreOffice no Windows.
#
# ============================================================


# ============================================================
# CONFIGURAÃ‡ÃƒO GERAL
# ============================================================

MM_TO_PT = 72.0 / 25.4


# ============================================================
# CONTROLES DA ETIQUETA 100 x 100
# ============================================================

MARGEM_SEGURANCA_HORIZONTAL_MM = 3.5
MARGEM_SEGURANCA_VERTICAL_MM = 3.5


# ============================================================
# TAMANHO DAS FONTES
# ============================================================

ESCALA_FONTE_100X100 = 1.08


# ============================================================
# APROVEITAMENTO VERTICAL
# ============================================================

ESCALA_VERTICAL_100X100 = 1.35


# ============================================================
# ESPAÃ‡AMENTO ENTRE LINHAS
# ============================================================

ESPACAMENTO_EXTRA_LINHAS_100X100 = 1.08


# ============================================================
# RECUO INTERNO DO CONTEÃšDO
# ============================================================

RECUO_INTERNO_CONTEUDO_MM = 1.2


# ============================================================
# POSIÃ‡ÃƒO HORIZONTAL DO CONTEÃšDO
# ============================================================

DESLOCAMENTO_CONTEUDO_DIREITA_MM = 1.0


# ============================================================
# RECORTE DO PDF ORIGINAL
# ============================================================

RECORTE_ESQUERDO_PT = 0.0
RECORTE_DIREITO_PT = 2.5
RECORTE_SUPERIOR_PT = 2.5
RECORTE_INFERIOR_PT = 2.5


# ============================================================
# MÃSCARA DO FRAGMENTO VERTICAL
# ============================================================

MASCARA_LINHA_VERTICAL_MM = 0.55


# ============================================================
# POSIÃ‡ÃƒO BASE DA MÃSCARA
# ============================================================

MASCARA_OFFSET_ESQUERDA_MM = 0.45


# ============================================================
# MÃNIMO DE FONTE
# ============================================================

MIN_FONT_PT = 5.0


# ============================================================
# REDUÃ‡ÃƒO DE SEGURANÃ‡A PARA TEXTO WRAP
# ============================================================

WRAPPED_FONT_FACTOR = 0.96


# ============================================================
# LIMPEZA DO PDF
# ============================================================

LIMPEZA_VERTICAL_MM = 2.0
LIMPEZA_HORIZONTAL_MM = 0.8


# ============================================================
# ESPESSURA DO QUADRO FINAL
# ============================================================

ESPESSURA_QUADRO_PT = 1.2


# ============================================================
# UTILITÃRIOS DE CAMINHO
# ============================================================

def obter_diretorio_programa() -> Path:
    """
    Retorna o diretÃ³rio base da aplicaÃ§Ã£o.

    Em Python:
        diretÃ³rio onde este .py estÃ¡.

    Em PyInstaller:
        diretÃ³rio onde o executÃ¡vel estÃ¡ instalado.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def obter_diretorio_recursos_embarcados() -> Path:
    """
    Retorna o diretÃ³rio de recursos utilizado pelo PyInstaller.

    No modo normal, retorna o diretÃ³rio do programa.
    No modo PyInstaller, _MEIPASS pode existir quando recursos
    estiverem extraÃ­dos para a pasta temporÃ¡ria do executÃ¡vel.
    """

    meipass = getattr(sys, "_MEIPASS", None)

    if meipass:
        return Path(meipass).resolve()

    return obter_diretorio_programa()


# ============================================================
# FUNÃ‡Ã•ES BÃSICAS
# ============================================================

def mm_to_pt(valor):
    return float(valor) * MM_TO_PT


def eh_100x100(largura, altura):
    return (
        abs(largura - 100.0) < 0.01
        and abs(altura - 100.0) < 0.01
    )


# ============================================================
# LIBREOFFICE
# ============================================================

def find_embedded_libreoffice(
    caminho_explicitado: str | None = None
) -> Path:
    """
    Localiza o LibreOffice utilizado pelo InBetta Label Engine.

    Ordem de procura:

    1. --libreoffice informado manualmente
    2. variÃ¡vel INBETTA_LIBREOFFICE
    3. LibreOffice embarcado em:
           motor/libreoffice/program/soffice.exe
    4. LibreOffice embarcado em:
           libreoffice/program/soffice.exe
    5. LibreOffice instalado localmente no Windows

    A instalaÃ§Ã£o local Ã© um FALLBACK DE DESENVOLVIMENTO.

    Na versÃ£o final distribuÃ­da, o LibreOffice embarcado terÃ¡
    prioridade e nÃ£o serÃ¡ necessÃ¡rio ter LibreOffice instalado
    no computador do cliente.
    """

    candidatos: list[Path] = []

    # --------------------------------------------------------
    # 1. CAMINHO INFORMADO EXPLICITAMENTE
    # --------------------------------------------------------

    if caminho_explicitado:

        informado = Path(
            caminho_explicitado
        ).expanduser()

        if informado.is_file():

            if informado.name.lower() == "soffice.exe":
                candidatos.append(informado)

        else:

            candidatos.append(
                informado
                / "program"
                / "soffice.exe"
            )

    # --------------------------------------------------------
    # 2. VARIÃVEL DE AMBIENTE
    # --------------------------------------------------------

    variavel = os.environ.get(
        "INBETTA_LIBREOFFICE",
        ""
    ).strip()

    if variavel:

        caminho_env = Path(
            variavel
        ).expanduser()

        if caminho_env.is_file():

            if caminho_env.name.lower() == "soffice.exe":
                candidatos.append(
                    caminho_env
                )

        else:

            candidatos.append(
                caminho_env
                / "program"
                / "soffice.exe"
            )

    # --------------------------------------------------------
    # 3. DIRETÃ“RIOS DO PROGRAMA
    # --------------------------------------------------------

    base_programa = (
        obter_diretorio_programa()
    )

    base_recursos = (
        obter_diretorio_recursos_embarcados()
    )

    bases = [
        base_programa,
        base_recursos,
    ]

    # Remove duplicados
    bases_unicas = []

    for base in bases:

        try:
            base = base.resolve()

        except Exception:
            continue

        if base not in bases_unicas:
            bases_unicas.append(base)

    # --------------------------------------------------------
    # 4. LIBREOFFICE EMBARCADO
    # --------------------------------------------------------

    for base in bases_unicas:

        candidatos.append(
            base
            / "motor"
            / "libreoffice"
            / "program"
            / "soffice.exe"
        )

        candidatos.append(
            base
            / "libreoffice"
            / "program"
            / "soffice.exe"
        )

    # --------------------------------------------------------
    # 5. LIBREOFFICE INSTALADO NO WINDOWS
    #
    # FALLBACK DE DESENVOLVIMENTO
    # --------------------------------------------------------

    candidatos.extend(
        [
            Path(
                r"C:\Program Files\LibreOffice\program\soffice.exe"
            ),

            Path(
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
            ),
        ]
    )

    # --------------------------------------------------------
    # 6. VERIFICAÃ‡ÃƒO
    # --------------------------------------------------------

    vistos = set()

    for candidato in candidatos:

        try:
            candidato = candidato.resolve()

        except Exception:
            continue

        if candidato in vistos:
            continue

        vistos.add(candidato)

        if candidato.is_file():

            return candidato

    # --------------------------------------------------------
    # ERRO
    # --------------------------------------------------------

    raise RuntimeError(
        "Nenhum motor LibreOffice foi encontrado.\n\n"

        "O InBetta Label Engine procura primeiro "
        "o LibreOffice embarcado e, durante o desenvolvimento, "
        "tambem aceita uma instalacao local do LibreOffice.\n\n"

        "Estrutura esperada para a versao embarcada:\n\n"

        "motor\\libreoffice\\program\\soffice.exe\n\n"

        "ou:\n\n"

        "libreoffice\\program\\soffice.exe\n\n"

        "Tambem foi verificada a instalacao local do Windows."
    )


# ============================================================
# EXECUTA LIBREOFFICE
# ============================================================

def export_with_libreoffice(
    xlsx_path,
    out_dir,
    caminho_libreoffice: str | None = None
):
    """
    Converte XLSX para PDF utilizando o LibreOffice encontrado
    pelo mecanismo de localizaÃ§Ã£o acima.

    Cada conversÃ£o recebe um perfil temporÃ¡rio prÃ³prio.
    """

    xlsx_path = Path(
        xlsx_path
    ).resolve()

    out_dir = Path(
        out_dir
    ).resolve()

    soffice = find_embedded_libreoffice(
        caminho_libreoffice
    )

    # --------------------------------------------------------
    # DiretÃ³rio de perfil temporÃ¡rio
    # --------------------------------------------------------

    profile_dir = (
        out_dir
        / "libreoffice_profile"
    )

    profile_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # URI DO PERFIL
    # --------------------------------------------------------

    profile_uri = profile_dir.as_uri()

    # --------------------------------------------------------
    # AMBIENTE ISOLADO
    # --------------------------------------------------------

    ambiente = os.environ.copy()

    ambiente[
        "SAL_USE_VCLPLUGIN"
    ] = "svp"

    # --------------------------------------------------------
    # COMANDO
    # --------------------------------------------------------

    comando = [
        str(soffice),

        "--headless",

        "--nologo",

        "--nodefault",

        "--nofirststartwizard",

        "--norestore",

        "--nolockcheck",

        f"-env:UserInstallation={profile_uri}",

        "--convert-to",
        "pdf",

        "--outdir",
        str(out_dir),

        str(xlsx_path),
    ]

    # --------------------------------------------------------
    # EXECUÃ‡ÃƒO
    # --------------------------------------------------------

    try:

        processo = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=ambiente,
            cwd=str(soffice.parent),
            timeout=180,
        )

    except subprocess.TimeoutExpired as erro:

        raise RuntimeError(
            "O LibreOffice excedeu o tempo limite "
            "durante a conversao do Excel para PDF."
        ) from erro

    except OSError as erro:

        raise RuntimeError(
            "Nao foi possivel iniciar o motor "
            "do LibreOffice.\n\n"

            f"Executavel:\n{soffice}\n\n"

            f"Detalhes:\n{erro}"
        ) from erro

    # --------------------------------------------------------
    # VERIFICAÃ‡ÃƒO DO PROCESSO
    # --------------------------------------------------------

    if processo.returncode != 0:

        raise RuntimeError(
            "Falha ao converter o Excel para PDF.\n\n"

            f"LibreOffice:\n{soffice}\n\n"

            f"Saida:\n{processo.stdout}\n\n"

            f"Erro:\n{processo.stderr}"
        )

    # --------------------------------------------------------
    # PDF GERADO
    # --------------------------------------------------------

    pdf = (
        out_dir
        /
        f"{xlsx_path.stem}.pdf"
    )

    if not pdf.exists():

        raise RuntimeError(
            "O LibreOffice terminou sem erro, "
            "mas o PDF intermediario nao foi encontrado.\n\n"

            f"Arquivo esperado:\n{pdf}\n\n"

            f"Saida do LibreOffice:\n"
            f"{processo.stdout}\n\n"

            f"Erros:\n"
            f"{processo.stderr}"
        )

    return pdf


# ============================================================
# IDENTIFICAÃ‡ÃƒO DAS ETIQUETAS
# ============================================================

def is_label_marker(valor):

    if valor is None:
        return False

    texto = str(valor).strip()

    return bool(
        re.fullmatch(
            r"\d{1,3}",
            texto
        )
    )


def detect_label_blocks(ws):

    starts = []

    for r in range(
        1,
        ws.max_row + 1
    ):

        if (
            is_label_marker(
                ws.cell(r, 1).value
            )
            and
            ws.cell(r, 2).value not in (
                None,
                ""
            )
        ):

            starts.append(r)

    if not starts:

        raise RuntimeError(
            "Nao encontrei os blocos das etiquetas."
        )

    blocks = []

    for i, start in enumerate(starts):

        if i + 1 < len(starts):
            next_start = starts[i + 1]

        else:
            next_start = ws.max_row + 1

        end = None

        # ----------------------------------------------------
        # PROCURA CONTEÃšDO
        # ----------------------------------------------------

        for r in range(
            start,
            next_start
        ):

            valor = ws.cell(
                r,
                2
            ).value

            if (
                isinstance(valor, str)
                and
                valor.strip()
                .upper()
                .startswith("CONTENIDO")
            ):

                end = r
                break

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if end is None:

            for r in range(
                next_start - 1,
                start - 1,
                -1
            ):

                if any(
                    ws.cell(r, c).value not in (
                        None,
                        ""
                    )
                    for c in range(2, 6)
                ):

                    end = r
                    break

        if end is None:
            end = start

        blocks.append(
            (
                start,
                end
            )
        )

    return blocks


# ============================================================
# FONTE
# ============================================================

def criar_fonte(
    fonte_original,
    fator
):

    if fonte_original is None:
        return None

    tamanho = fonte_original.sz

    if tamanho is None:

        return copy.copy(
            fonte_original
        )

    novo_tamanho = max(
        MIN_FONT_PT,
        float(tamanho) * fator
    )

    return Font(
        name=fonte_original.name,
        sz=novo_tamanho,
        b=fonte_original.b,
        i=fonte_original.i,
        vertAlign=fonte_original.vertAlign,
        underline=fonte_original.underline,
        strike=fonte_original.strike,
        color=copy.copy(
            fonte_original.color
        ),
        charset=fonte_original.charset,
        family=fonte_original.family,
        scheme=fonte_original.scheme,
        condense=fonte_original.condense,
        extend=fonte_original.extend,
        outline=fonte_original.outline,
        shadow=fonte_original.shadow
    )


# ============================================================
# CÃ“PIA DE CÃ‰LULA
# ============================================================

def copy_cell(
    src,
    dst,
    value,
    escala_fonte
):

    dst.value = value

    if src.has_style:

        dst.fill = copy.copy(
            src.fill
        )

        dst.border = copy.copy(
            src.border
        )

        dst.alignment = copy.copy(
            src.alignment
        )

        dst.protection = copy.copy(
            src.protection
        )

    if src.number_format:

        dst.number_format = (
            src.number_format
        )

    # --------------------------------------------------------
    # FONTE
    # --------------------------------------------------------

    if src.font:

        fonte = criar_fonte(
            src.font,
            escala_fonte
        )

        dst.font = fonte


# ============================================================
# VALOR CALCULADO
# ============================================================

def cached_value(
    formula_ws,
    cached_ws,
    row,
    col
):

    original = formula_ws.cell(
        row,
        col
    ).value

    if (
        isinstance(original, str)
        and
        original.startswith("=")
    ):

        cached = cached_ws.cell(
            row,
            col
        ).value

        if cached is not None:
            return cached

    return original


# ============================================================
# CONSTRÃ“I EXCEL TEMPORÃRIO
# ============================================================

def build_export_workbook(
    input_xlsx,
    temp_xlsx,
    largura_mm,
    altura_mm
):

    wb_formula = load_workbook(
        input_xlsx,
        data_only=False
    )

    wb_cached = load_workbook(
        input_xlsx,
        data_only=True
    )

    if "Etiqueta Produto" in wb_formula.sheetnames:
        sheet_name = "Etiqueta Produto"

    else:
        sheet_name = (
            wb_formula.active.title
        )

    src = wb_formula[
        sheet_name
    ]

    cached = wb_cached[
        sheet_name
    ]

    blocks = detect_label_blocks(
        src
    )

    out = Workbook()

    out.remove(
        out.active
    )

    # --------------------------------------------------------
    # ESCALAS
    # --------------------------------------------------------

    if eh_100x100(
        largura_mm,
        altura_mm
    ):

        escala_fonte = (
            ESCALA_FONTE_100X100
        )

        escala_vertical = (
            ESCALA_VERTICAL_100X100
            *
            ESPACAMENTO_EXTRA_LINHAS_100X100
        )

    else:

        escala_fonte = 1.0
        escala_vertical = 1.0

    # --------------------------------------------------------
    # COLUNAS ORIGINAIS
    # --------------------------------------------------------

    src_min_col = 2
    src_max_col = 5

    for idx, (
        start,
        end
    ) in enumerate(
        blocks,
        start=1
    ):

        dst = out.create_sheet(
            f"Etiqueta_{idx:02d}"
        )

        row_count = (
            end - start + 1
        )

        # ----------------------------------------------------
        # LARGURA DAS COLUNAS
        # ----------------------------------------------------

        for (
            src_col,
            dst_col
        ) in zip(
            range(
                src_min_col,
                src_max_col + 1
            ),
            range(
                1,
                5
            )
        ):

            src_letter = src.cell(
                1,
                src_col
            ).column_letter

            dst_letter = dst.cell(
                1,
                dst_col
            ).column_letter

            largura_coluna = (
                src.column_dimensions[
                    src_letter
                ].width
            )

            if largura_coluna is not None:

                dst.column_dimensions[
                    dst_letter
                ].width = (
                    largura_coluna
                )

            # =================================================
            # AJUSTE DO ":"
            #
            # SOMENTE A COLUNA B ORIGINAL
            # recebe +1.0 de largura no 100x100.
            # =================================================

            if (
                src_col == 2
                and
                eh_100x100(
                    largura_mm,
                    altura_mm
                )
            ):

                largura_atual = (
                    dst.column_dimensions[
                        dst_letter
                    ].width
                )

                if largura_atual is None:
                    largura_atual = 8.43

                dst.column_dimensions[
                    dst_letter
                ].width = (
                    largura_atual + 1.0
                )

        # ----------------------------------------------------
        # LINHAS / CÃ‰LULAS
        # ----------------------------------------------------

        for src_row in range(
            start,
            end + 1
        ):

            dst_row = (
                src_row
                -
                start
                +
                1
            )

            altura_original = (
                src.row_dimensions[
                    src_row
                ].height
            )

            if altura_original is not None:

                altura_nova = (
                    float(
                        altura_original
                    )
                    *
                    escala_vertical
                )

            else:

                altura_nova = (
                    15.0
                    *
                    escala_vertical
                )

            dst.row_dimensions[
                dst_row
            ].height = altura_nova

            for src_col in range(
                src_min_col,
                src_max_col + 1
            ):

                dst_col = (
                    src_col
                    -
                    src_min_col
                    +
                    1
                )

                s = src.cell(
                    src_row,
                    src_col
                )

                d = dst.cell(
                    dst_row,
                    dst_col
                )

                value = cached_value(
                    src,
                    cached,
                    src_row,
                    src_col
                )

                copy_cell(
                    s,
                    d,
                    value,
                    escala_fonte
                )

                # ------------------------------------------------
                # CORREÃ‡ÃƒO DE ALINHAMENTO
                # ------------------------------------------------

                valor_coluna_b = (
                    src.cell(
                        src_row,
                        2
                    ).value
                )

                if (
                    src_col in (2, 3)
                    and
                    isinstance(
                        valor_coluna_b,
                        str
                    )
                    and
                    valor_coluna_b.strip()
                    .upper()
                    .startswith(
                        "CONTENIDO"
                    )
                ):

                    alinhamento = copy.copy(
                        d.alignment
                    )

                    alinhamento.vertical = (
                        "center"
                    )

                    if src_col == 3:
                        alinhamento.indent = 1

                    d.alignment = alinhamento

        # ----------------------------------------------------
        # MESCLAGENS
        # ----------------------------------------------------

        for merged in (
            src.merged_cells.ranges
        ):

            if (
                merged.min_row >= start
                and
                merged.max_row <= end
                and
                merged.min_col >= src_min_col
                and
                merged.max_col <= src_max_col
            ):

                dst.merge_cells(
                    start_row=(
                        merged.min_row
                        -
                        start
                        +
                        1
                    ),

                    start_column=(
                        merged.min_col
                        -
                        src_min_col
                        +
                        1
                    ),

                    end_row=(
                        merged.max_row
                        -
                        start
                        +
                        1
                    ),

                    end_column=(
                        merged.max_col
                        -
                        src_min_col
                        +
                        1
                    )
                )

        # ----------------------------------------------------
        # PÃGINA
        # ----------------------------------------------------

        dst.print_area = (
            f"A1:D{row_count}"
        )

        dst.sheet_view.showGridLines = False

        if largura_mm > altura_mm:

            dst.page_setup.orientation = (
                "landscape"
            )

        else:

            dst.page_setup.orientation = (
                "portrait"
            )

        dst.page_setup.fitToWidth = 1
        dst.page_setup.fitToHeight = 1

        dst.sheet_properties.pageSetUpPr.fitToPage = True

        # ----------------------------------------------------
        # SEM MARGENS DO LIBREOFFICE
        # ----------------------------------------------------

        dst.page_margins.left = 0
        dst.page_margins.right = 0
        dst.page_margins.top = 0
        dst.page_margins.bottom = 0
        dst.page_margins.header = 0
        dst.page_margins.footer = 0

    # --------------------------------------------------------
    # CÃLCULO
    # --------------------------------------------------------

    try:

        out.calculation.fullCalcOnLoad = True
        out.calculation.forceFullCalc = True

    except Exception:

        pass

    # --------------------------------------------------------
    # SALVA
    # --------------------------------------------------------

    out.save(
        temp_xlsx
    )

    return len(blocks)


# ============================================================
# ENCONTRA QUADRO ORIGINAL
# ============================================================

def find_source_frame(page):

    horizontals = []
    verticals = []

    for drawing in (
        page.get_drawings()
    ):

        rect_data = drawing.get(
            "rect"
        )

        if not rect_data:
            continue

        rect = pymupdf.Rect(
            rect_data
        )

        if (
            rect.width > 80
            and
            rect.height < 3
        ):

            horizontals.append(
                rect
            )

        elif (
            rect.height > 60
            and
            rect.width < 3
        ):

            verticals.append(
                rect
            )

    if (
        len(horizontals) >= 2
        and
        len(verticals) >= 2
    ):

        x0 = min(
            v.x0
            for v in verticals
        )

        x1 = max(
            v.x1
            for v in verticals
        )

        y0 = min(
            h.y0
            for h in horizontals
        )

        y1 = max(
            h.y1
            for h in horizontals
        )

        frame = pymupdf.Rect(
            x0,
            y0,
            x1,
            y1
        )

        if (
            frame.width > 20
            and
            frame.height > 20
        ):

            return frame

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    words = page.get_text(
        "words"
    )

    if not words:

        return pymupdf.Rect(
            page.rect
        )

    x0 = min(
        w[0]
        for w in words
    )

    y0 = min(
        w[1]
        for w in words
    )

    x1 = max(
        w[2]
        for w in words
    )

    y1 = max(
        w[3]
        for w in words
    )

    return pymupdf.Rect(
        x0 - 3,
        y0 - 3,
        x1 + 3,
        y1 + 3
    )


# ============================================================
# NORMALIZA PDF
# ============================================================

def normalize_pdf(
    source_pdf,
    output_pdf,
    largura_mm,
    altura_mm,
    expected_pages
):

    src_doc = pymupdf.open(
        source_pdf
    )

    try:

        if (
            expected_pages is not None
            and
            len(src_doc) != expected_pages
        ):

            raise RuntimeError(
                f"Foram detectadas "
                f"{expected_pages} etiquetas, "
                f"mas o LibreOffice gerou "
                f"{len(src_doc)} paginas."
            )

        out = pymupdf.open()

        try:

            page_w = mm_to_pt(
                largura_mm
            )

            page_h = mm_to_pt(
                altura_mm
            )

            # ------------------------------------------------
            # MARGENS
            # ------------------------------------------------

            margem_x = mm_to_pt(
                MARGEM_SEGURANCA_HORIZONTAL_MM
            )

            margem_y = mm_to_pt(
                MARGEM_SEGURANCA_VERTICAL_MM
            )

            frame_rect = pymupdf.Rect(
                margem_x,
                margem_y,
                page_w - margem_x,
                page_h - margem_y
            )

            # ------------------------------------------------
            # ÃREA INTERNA DO QUADRO
            # ------------------------------------------------

            conteudo_recuo = mm_to_pt(
                RECUO_INTERNO_CONTEUDO_MM
            )

            # ------------------------------------------------
            # DESLOCAMENTO HORIZONTAL
            # ------------------------------------------------

            deslocamento_direita = mm_to_pt(
                DESLOCAMENTO_CONTEUDO_DIREITA_MM
            )

            inner_x0 = (
                frame_rect.x0
                +
                conteudo_recuo
                +
                deslocamento_direita
            )

            inner_x1 = (
                frame_rect.x1
                -
                conteudo_recuo
            )

            inner_y0 = (
                frame_rect.y0
                +
                conteudo_recuo
            )

            inner_y1 = (
                frame_rect.y1
                -
                conteudo_recuo
            )

            inner_rect = pymupdf.Rect(
                inner_x0,
                inner_y0,
                inner_x1,
                inner_y1
            )

            # =================================================
            # PROCESSAMENTO DAS PÃGINAS
            # =================================================

            for page_no, src_page in enumerate(
                src_doc
            ):

                src_frame = (
                    find_source_frame(
                        src_page
                    )
                )

                # ------------------------------------------------
                # RECORTE ORIGINAL
                # ------------------------------------------------

                src_inner = pymupdf.Rect(
                    src_frame.x0
                    +
                    RECORTE_ESQUERDO_PT,

                    src_frame.y0
                    +
                    RECORTE_SUPERIOR_PT,

                    src_frame.x1
                    -
                    RECORTE_DIREITO_PT,

                    src_frame.y1
                    -
                    RECORTE_INFERIOR_PT
                )

                # ------------------------------------------------
                # GARANTIA DE RETÃ‚NGULO VÃLIDO
                # ------------------------------------------------

                if (
                    src_inner.width <= 10
                    or
                    src_inner.height <= 10
                ):

                    raise RuntimeError(
                        "Area interna do quadro original invalida."
                    )

                dst = out.new_page(
                    width=page_w,
                    height=page_h
                )

                # ------------------------------------------------
                # CONTEÃšDO
                # ------------------------------------------------

                dst.show_pdf_page(
                    inner_rect,
                    src_doc,
                    page_no,
                    clip=src_inner,
                    keep_proportion=True,
                    overlay=True
                )

                # =================================================
                # LIMPEZA DAS EXTREMIDADES
                # =================================================

                limpeza_vertical = mm_to_pt(
                    LIMPEZA_VERTICAL_MM
                )

                limpeza_horizontal = mm_to_pt(
                    LIMPEZA_HORIZONTAL_MM
                )

                # ------------------------------------------------
                # SUPERIOR
                #
                # NÃƒO FAZER LIMPEZA SUPERIOR.
                # ------------------------------------------------

                # ------------------------------------------------
                # INFERIOR
                # ------------------------------------------------

                dst.draw_rect(
                    pymupdf.Rect(
                        0,
                        page_h - limpeza_vertical,
                        page_w,
                        page_h
                    ),
                    color=(1, 1, 1),
                    fill=(1, 1, 1),
                    overlay=True
                )

                # ------------------------------------------------
                # ESQUERDA
                # ------------------------------------------------

                dst.draw_rect(
                    pymupdf.Rect(
                        0,
                        0,
                        limpeza_horizontal,
                        page_h
                    ),
                    color=(1, 1, 1),
                    fill=(1, 1, 1),
                    overlay=True
                )

                # ------------------------------------------------
                # DIREITA
                # ------------------------------------------------

                dst.draw_rect(
                    pymupdf.Rect(
                        page_w - limpeza_horizontal,
                        0,
                        page_w,
                        page_h
                    ),
                    color=(1, 1, 1),
                    fill=(1, 1, 1),
                    overlay=True
                )

                # =================================================
                # MÃSCARA DA LINHA VERTICAL
                # =================================================

                mascara_largura = mm_to_pt(
                    MASCARA_LINHA_VERTICAL_MM
                )

                mascara_offset = mm_to_pt(
                    MASCARA_OFFSET_ESQUERDA_MM
                )

                mascara_x0 = (
                    inner_rect.x0
                    -
                    mascara_offset
                )

                mascara_x1 = (
                    mascara_x0
                    +
                    mascara_largura
                )

                mascara_rect = pymupdf.Rect(
                    mascara_x0,
                    inner_rect.y0,
                    mascara_x1,
                    inner_rect.y1
                )

                dst.draw_rect(
                    mascara_rect,
                    color=(1, 1, 1),
                    fill=(1, 1, 1),
                    overlay=True
                )

                # =================================================
                # QUADRO FINAL
                #
                # A borda Ã© desenhada POR ÃšLTIMO.
                # =================================================

                dst.draw_rect(
                    frame_rect,
                    color=(0, 0, 0),
                    width=ESPESSURA_QUADRO_PT,
                    overlay=True
                )

            # =====================================================
            # METADADOS
            # =====================================================

            metadata = (
                src_doc.metadata
                or {}
            )

            metadata["title"] = (
                output_pdf.stem
            )

            metadata["producer"] = (
                "Gerador de Etiquetas Inbetta"
            )

            out.set_metadata(
                metadata
            )

            # -----------------------------------------------------
            # SALVA PDF FINAL
            # -----------------------------------------------------

            out.save(
                output_pdf,
                garbage=4,
                deflate=True
            )

        finally:

            out.close()

    finally:

        src_doc.close()


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Gerador de Etiquetas Inbetta - "
            "XLSX para PDF"
        )
    )

    parser.add_argument(
        "arquivo",
        help="Arquivo XLSX de origem"
    )

    parser.add_argument(
        "--largura",
        type=float,
        required=True,
        help="Largura da etiqueta em mm"
    )

    parser.add_argument(
        "--altura",
        type=float,
        required=True,
        help="Altura da etiqueta em mm"
    )

    parser.add_argument(
        "-o",
        "--saida",
        help="Arquivo PDF de saÃ­da"
    )

    parser.add_argument(
        "--libreoffice",
        help=(
            "Caminho do LibreOffice. "
            "Usado para desenvolvimento/testes."
        )
    )

    args = parser.parse_args()

    # ========================================================
    # ARQUIVO DE ENTRADA
    # ========================================================

    input_xlsx = (
        Path(
            args.arquivo
        )
        .expanduser()
        .resolve()
    )

    if not input_xlsx.exists():

        print(
            "ERRO: arquivo nao encontrado:\n"
            f"{input_xlsx}",
            file=sys.stderr
        )

        return 2

    # ========================================================
    # TAMANHO
    # ========================================================

    largura = float(
        args.largura
    )

    altura = float(
        args.altura
    )

    if (
        largura <= 0
        or
        altura <= 0
    ):

        print(
            "ERRO: tamanho invalido.",
            file=sys.stderr
        )

        return 2

    # ========================================================
    # SAÃDA
    # ========================================================

    if args.saida:

        output_pdf = (
            Path(
                args.saida
            )
            .expanduser()
            .resolve()
        )

    else:

        output_pdf = (
            input_xlsx.with_name(
                f"{input_xlsx.stem}_"
                f"{largura}x{altura}mm.pdf"
            )
        )

    output_pdf.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # ORIENTAÃ‡ÃƒO
    # ========================================================

    if altura >= largura:
        orientacao = "RETRATO"

    else:
        orientacao = "PAISAGEM"

    # ========================================================
    # INFORMAÃ‡Ã•ES
    # ========================================================

    print()

    print(
        "=========================================="
    )

    print(
        "      GERADOR DE ETIQUETAS INBETTA"
    )

    print(
        "=========================================="
    )

    print(
        f"Tamanho: "
        f"{largura} x {altura} mm"
    )

    print(
        f"Orientacao: {orientacao}"
    )

    print(
        f"Margem horizontal: "
        f"{MARGEM_SEGURANCA_HORIZONTAL_MM} mm"
    )

    print(
        f"Margem vertical: "
        f"{MARGEM_SEGURANCA_VERTICAL_MM} mm"
    )

    print(
        f"Recuo interno: "
        f"{RECUO_INTERNO_CONTEUDO_MM} mm"
    )

    print(
        f"Deslocamento direita: "
        f"{DESLOCAMENTO_CONTEUDO_DIREITA_MM} mm"
    )

    print(
        f"Recorte esquerdo: "
        f"{RECORTE_ESQUERDO_PT} pt"
    )

    print(
        f"Recorte direito: "
        f"{RECORTE_DIREITO_PT} pt"
    )

    print(
        f"Mascaramento linha vertical: "
        f"{MASCARA_LINHA_VERTICAL_MM} mm"
    )

    print(
        f"Offset mascara esquerda: "
        f"{MASCARA_OFFSET_ESQUERDA_MM} mm"
    )

    print(
        f"Espessura quadro: "
        f"{ESPESSURA_QUADRO_PT} pt"
    )

    print(
        f"Limpeza horizontal: "
        f"{LIMPEZA_HORIZONTAL_MM} mm"
    )

    print(
        f"Limpeza vertical: "
        f"{LIMPEZA_VERTICAL_MM} mm"
    )

    if eh_100x100(
        largura,
        altura
    ):

        print(
            f"Escala fonte: "
            f"{ESCALA_FONTE_100X100}"
        )

        print(
            f"Escala vertical: "
            f"{ESCALA_VERTICAL_100X100}"
        )

        print(
            f"Espacamento linhas: "
            f"{ESPACAMENTO_EXTRA_LINHAS_100X100}"
        )

        print(
            "Ajuste coluna B para ':': +1.0"
        )

    print(
        "Quadro adicional: NAO"
    )

    # ========================================================
    # LIBREOFFICE
    # ========================================================

    try:

        soffice = find_embedded_libreoffice(
            args.libreoffice
        )

        print(
            f"Motor LibreOffice: {soffice}"
        )

    except Exception as erro:

        print(
            f"ERRO: {erro}",
            file=sys.stderr
        )

        return 1

    print()

    # ========================================================
    # PROCESSAMENTO
    # ========================================================

    try:

        with tempfile.TemporaryDirectory(
            prefix="inbetta_etiquetas_"
        ) as temp_dir:

            temp_dir = Path(
                temp_dir
            )

            temp_xlsx = (
                temp_dir
                /
                "etiquetas_preparadas.xlsx"
            )

            # ------------------------------------------------
            # XLSX TEMPORÃRIO
            # ------------------------------------------------

            quantidade = (
                build_export_workbook(
                    input_xlsx,
                    temp_xlsx,
                    largura,
                    altura
                )
            )

            print(
                f"Etiquetas detectadas: {quantidade}"
            )

            # ------------------------------------------------
            # XLSX -> PDF
            # ------------------------------------------------

            intermediate_pdf = (
                export_with_libreoffice(
                    temp_xlsx,
                    temp_dir,
                    args.libreoffice
                )
            )

            print(
                "Conversao XLSX -> PDF concluida."
            )

            # ------------------------------------------------
            # PDF -> PDF FINAL
            # ------------------------------------------------

            normalize_pdf(
                intermediate_pdf,
                output_pdf,
                largura,
                altura,
                quantidade
            )

        # ====================================================
        # SUCESSO
        # ====================================================

        print()

        print(
            f"OK: {quantidade} etiquetas geradas."
        )

        print(
            f"Tamanho: "
            f"{largura} x {altura} mm"
        )

        print(
            f"Orientacao: {orientacao}"
        )

        print(
            f"PDF: {output_pdf}"
        )

        print()

        return 0

    except Exception as erro:

        print(
            f"ERRO: {erro}",
            file=sys.stderr
        )

        return 1


# ============================================================
# ENTRADA DO PROGRAMA
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )





