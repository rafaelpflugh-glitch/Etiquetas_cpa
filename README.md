# Etiquetas CPA (CPA Label Engine)

Sistema desktop em Python para geração e preparação de etiquetas para impressão a partir de planilhas Excel (`.xlsx`), desenvolvido para o **Grupo CPA - Soluções Inteligentes**.

## Arquitetura

O processamento segue o pipeline:

`XLSX -> LibreOffice -> PDF intermediário -> PyMuPDF -> PDF final de etiquetas`

- **`interface_etiquetas.py`**: interface gráfica (Tkinter + Pillow) do **CPA Label Engine** para seleção de planilhas, pasta de saída e geração das etiquetas.
- **`gerar_etiquetas_pdf.py`**: motor de conversão, ajuste de escala, margens, recorte e geração do PDF final de etiquetas (ex.: 100×100 mm e 100×60 mm).
- **`diagnostico_100x100.py`**: utilitário para gerar uma folha PDF de diagnóstico de impressão 100×100 mm (ex.: impressoras térmicas TSC).
- **`CPALabelEngine.spec`**: especificação do PyInstaller para empacotar a interface, o motor e o LibreOffice embarcado.
- **`instalador/CPALabelEngine.iss`**: script do Inno Setup para gerar o instalador Windows (`CPALabelEngine_Setup_v1.0.0.exe`).
- **`copiar_libreoffice.py` / `copiar_lo_para_dist.py`**: scripts auxiliares para copiar a instalação local do LibreOffice para empacotamento.

## Requisitos

- **Python 3.10+**
- **LibreOffice** instalado no sistema (para execução em desenvolvimento) ou embarcado para distribuição
- Dependências Python:

```bash
pip install -r requirements.txt
```

## Como executar em desenvolvimento

```bash
python interface_etiquetas.py
```

## Empacotamento e Instalador (Windows)

1. Copie o LibreOffice embarcado (se necessário) e ajuste os caminhos em `CPALabelEngine.spec`.
2. Gere o bundle com PyInstaller:
   ```bash
   pyinstaller CPALabelEngine.spec
   ```
3. Compile o instalador com o Inno Setup usando `instalador/CPALabelEngine.iss`.

> **Nota:** Artefatos de build (`build/`, `dist/`, `motor/`, instaladores `.exe`), planilhas e PDFs gerados são ignorados via `.gitignore` para manter o repositório leve e sem dados locais.

## Licença / Direitos Autorais

Copyright (c) 2026 Rafael Pflug. Todos os direitos reservados.
