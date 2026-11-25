import fitz


# ============================================================
# DIAGNÓSTICO DE IMPRESSÃO TSC
# Etiqueta física: 100 x 100 mm
# Orientação: RETRATO
# ============================================================

MM = 72 / 25.4

LARGURA = 100 * MM
ALTURA = 100 * MM


# ============================================================
# CORES
# ============================================================

PRETO = (0, 0, 0)
CINZA = (0.45, 0.45, 0.45)
VERMELHO = (0.8, 0, 0)


# ============================================================
# CRIA PDF
# ============================================================

pdf = fitz.open()

pagina = pdf.new_page(
    width=LARGURA,
    height=ALTURA
)


# ============================================================
# BORDA EXTERNA
# ============================================================

pagina.draw_rect(
    fitz.Rect(
        0,
        0,
        LARGURA,
        ALTURA
    ),
    color=PRETO,
    width=1.2
)


# ============================================================
# MARGEM INTERNA DE REFERÊNCIA
# ============================================================

margem = 5 * MM

pagina.draw_rect(
    fitz.Rect(
        margem,
        margem,
        LARGURA - margem,
        ALTURA - margem
    ),
    color=CINZA,
    width=0.5
)


# ============================================================
# TÍTULO
# ============================================================

pagina.insert_text(
    fitz.Point(
        8 * MM,
        12 * MM
    ),
    "DIAGNOSTICO TSC - 100 x 100 mm",
    fontsize=9,
    color=PRETO
)


pagina.insert_text(
    fitz.Point(
        8 * MM,
        17 * MM
    ),
    "RETRATO",
    fontsize=7,
    color=CINZA
)


# ============================================================
# LINHA CENTRAL VERTICAL
# ============================================================

centro_x = LARGURA / 2

pagina.draw_line(
    fitz.Point(
        centro_x,
        20 * MM
    ),
    fitz.Point(
        centro_x,
        95 * MM
    ),
    color=CINZA,
    width=0.5
)


# ============================================================
# LINHA CENTRAL HORIZONTAL
# ============================================================

centro_y = ALTURA / 2

pagina.draw_line(
    fitz.Point(
        5 * MM,
        centro_y
    ),
    fitz.Point(
        95 * MM,
        centro_y
    ),
    color=CINZA,
    width=0.5
)


# ============================================================
# RÉGUA VERTICAL
#
# 0 até 100 mm
# ============================================================

x_regua = 12 * MM

for mm in range(0, 101, 10):

    y = mm * MM

    # Marca principal
    pagina.draw_line(
        fitz.Point(
            x_regua,
            y
        ),
        fitz.Point(
            x_regua + 6 * MM,
            y
        ),
        color=PRETO,
        width=1
    )

    # Número
    texto_y = y - 1.5 * MM

    if texto_y < 6 * MM:
        texto_y = y + 4 * MM

    if texto_y > ALTURA - 3 * MM:
        texto_y = ALTURA - 3 * MM

    pagina.insert_text(
        fitz.Point(
            x_regua + 8 * MM,
            texto_y
        ),
        f"{mm} mm",
        fontsize=6,
        color=PRETO
    )

    # Marcas intermediárias de 5 mm
    if mm < 100:

        y5 = (mm + 5) * MM

        pagina.draw_line(
            fitz.Point(
                x_regua,
                y5
            ),
            fitz.Point(
                x_regua + 3 * MM,
                y5
            ),
            color=CINZA,
            width=0.5
        )


# ============================================================
# RÉGUA HORIZONTAL
#
# 0 até 100 mm
# ============================================================

y_regua = 88 * MM

for mm in range(0, 101, 10):

    x = mm * MM

    pagina.draw_line(
        fitz.Point(
            x,
            y_regua
        ),
        fitz.Point(
            x,
            y_regua - 6 * MM
        ),
        color=PRETO,
        width=1
    )

    # Número
    texto_x = x + 1 * MM

    if texto_x > LARGURA - 12 * MM:
        texto_x = LARGURA - 12 * MM

    pagina.insert_text(
        fitz.Point(
            texto_x,
            y_regua + 5 * MM
        ),
        f"{mm}",
        fontsize=6,
        color=PRETO
    )

    # Marca de 5 mm
    if mm < 100:

        x5 = (mm + 5) * MM

        pagina.draw_line(
            fitz.Point(
                x5,
                y_regua
            ),
            fitz.Point(
                x5,
                y_regua - 3 * MM
            ),
            color=CINZA,
            width=0.5
        )


# ============================================================
# MARCA DE ORIGEM - 0 MM
# ============================================================

pagina.draw_line(
    fitz.Point(
        0,
        0
    ),
    fitz.Point(
        8 * MM,
        8 * MM
    ),
    color=VERMELHO,
    width=1.5
)

pagina.draw_line(
    fitz.Point(
        0,
        8 * MM
    ),
    fitz.Point(
        8 * MM,
        0
    ),
    color=VERMELHO,
    width=1.5
)


# ============================================================
# MARCA DE 50 x 50 MM
# ============================================================

centro = fitz.Rect(
    48 * MM,
    48 * MM,
    52 * MM,
    52 * MM
)

pagina.draw_rect(
    centro,
    color=VERMELHO,
    width=1
)

pagina.insert_text(
    fitz.Point(
        54 * MM,
        51 * MM
    ),
    "50 x 50 mm",
    fontsize=7,
    color=VERMELHO
)


# ============================================================
# MARCA DE FUNDO
# ============================================================

pagina.insert_text(
    fitz.Point(
        39 * MM,
        98 * MM
    ),
    "FUNDO / 100 mm",
    fontsize=6,
    color=PRETO
)


# ============================================================
# INFORMAÇÕES
# ============================================================

pagina.insert_text(
    fitz.Point(
        62 * MM,
        25 * MM
    ),
    "MEDIR:",
    fontsize=7,
    color=PRETO
)

pagina.insert_text(
    fitz.Point(
        62 * MM,
        30 * MM
    ),
    "1. Inicio da etiqueta",
    fontsize=6,
    color=CINZA
)

pagina.insert_text(
    fitz.Point(
        62 * MM,
        34 * MM
    ),
    "2. Marca 0 mm",
    fontsize=6,
    color=CINZA
)

pagina.insert_text(
    fitz.Point(
        62 * MM,
        38 * MM
    ),
    "3. Marca 50 mm",
    fontsize=6,
    color=CINZA
)

pagina.insert_text(
    fitz.Point(
        62 * MM,
        42 * MM
    ),
    "4. Marca 100 mm",
    fontsize=6,
    color=CINZA
)


# ============================================================
# SALVA
# ============================================================

saida = "diagnostico_100x100.pdf"

pdf.save(
    saida,
    garbage=4,
    deflate=True
)

pdf.close()

print("OK: PDF de diagnóstico criado.")
print(f"Arquivo: {saida}")
print("Tamanho: 100 x 100 mm")
print("Orientação: RETRATO")