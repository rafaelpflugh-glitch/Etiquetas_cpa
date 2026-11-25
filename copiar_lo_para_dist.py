from pathlib import Path
import shutil

BASE = Path(r"C:\Users\pflug\Etiquetas_Inbetta")

origem = BASE / "motor" / "libreoffice"

destino = (
    BASE
    / "dist"
    / "InBettaLabelEngine"
    / "motor"
    / "libreoffice"
)

print("Origem:")
print(origem)

print()
print("Destino:")
print(destino)

if not origem.exists():
    raise SystemExit(
        "ERRO: LibreOffice de origem nao encontrado."
    )

if destino.exists():
    print()
    print("Removendo copia antiga...")
    shutil.rmtree(destino)

print()
print("Copiando LibreOffice...")
print("Isso pode demorar alguns minutos.")

shutil.copytree(
    origem,
    destino
)

soffice = (
    destino
    / "program"
    / "soffice.exe"
)

print()
print("=" * 60)

if soffice.exists():
    print("COPIA CONCLUIDA")
    print()
    print("LibreOffice encontrado em:")
    print(soffice)
else:
    print("ERRO: soffice.exe nao foi encontrado.")