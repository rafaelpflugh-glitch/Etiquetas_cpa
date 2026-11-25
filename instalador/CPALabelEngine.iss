#define MyAppName "CPA Label Engine"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Grupo CPA"
#define MyAppExeName "CPALabelEngine.exe"

[Setup]
AppId={{8F8B4A1E-7A7B-4E7C-9A72-CPA2026LABEL}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\CPA Label Engine
DefaultGroupName=CPA Label Engine

OutputDir=installer
OutputBaseFilename=CPALabelEngine_Setup_v1.0.0

Compression=lzma
SolidCompression=yes

WizardStyle=modern
DisableProgramGroupPage=yes

SetupIconFile=..\CPA_LOGO_SIMBOLO.ico

UninstallDisplayIcon={app}\CPALabelEngine.exe

ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; \
    Description: "Criar atalho na Área de Trabalho"; \
    GroupDescription: "Atalhos:"; \
    Flags: unchecked

[Files]
Source: "..\dist\CPALabelEngine\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CPA Label Engine"; \
    Filename: "{app}\CPALabelEngine.exe"; \
    WorkingDir: "{app}"

Name: "{autodesktop}\CPA Label Engine"; \
    Filename: "{app}\CPALabelEngine.exe"; \
    WorkingDir: "{app}"; \
    Tasks: desktopicon

[Run]
Filename: "{app}\CPALabelEngine.exe"; \
    Description: "Executar CPA Label Engine"; \
    Flags: nowait postinstall skipifsilent
