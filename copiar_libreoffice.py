from pathlib import Path
import shutil
import sys

ORIGEM = Path(r"C:\Program Files\LibreOffice")
DESTINO = Path(r"C:\Users\pflug\Etiquetas_Inbetta\motor\libreoffice")


def main():
    print("=" * 60)
    print("COPIANDO LIBREOFFICE PARA O INBETTA LABEL ENGINE")
    print("=" * 60)
    print()
    
    print(f"Origem : {ORIGEM}")
    print(f"Destino: {DESTINO}")
    print()

    if not ORIGEM.exists():
        print("ERRO: instalação original do LibreOffice não encontrada.")
        return 1

    soffice = ORIGEM / "program" / "soffice.exe"

    if not soffice.exists():
        print("ERRO: soffice.exe não encontrado.")
        print(soffice)
        return 1

    DESTINO.mkdir(parents=True, exist_ok=True)

    arquivos = 0
    diretorios = 0

    for item in ORIGEM.rglob("*"):

        relativo = item.relative_to(ORIGEM)
        destino = DESTINO / relativo

        if item.is_dir():
            destino.mkdir(parents=True, exist_ok=True)
            diretorios += 1

        elif item.is_file():
            destino.parent.mkdir(parents=True, exist_ok=True)

            print(f"Copiando: {relativo}")

            shutil.copy2(
                item,
                destino
            )

            arquivos += 1

    print()
    print("=" * 60)
    print("CÓPIA CONCLUÍDA")
    print("=" * 60)
    print()
    print(f"Arquivos copiados   : {arquivos}")
    print(f"Diretórios criados  : {diretorios}")
    print()
    
    soffice_destino = (
        DESTINO
        / "program"
        / "soffice.exe"
    )

    if soffice_destino.exists():
        print("OK: LibreOffice embarcado encontrado.")
        print()
        print(f"Executável:")
        print(soffice_destino)
        print()
        return 0

    print("ERRO: cópia terminou, mas soffice.exe não foi encontrado.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())