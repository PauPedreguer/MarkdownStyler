; Instal·lador de Windows (Inno Setup 6).
;
; Es compila des de l'arrel del projecte, després de generar el bundle amb
; build.sh (o el workflow de GitHub Actions):
;
;   iscc packaging\windows\markdown-styler.iss
;
; Les rutes són relatives a este fitxer: ..\build\ dist és on deixa el bundle
; PyInstaller i ..\dist\ és on ix l'instal·lador.

#define Versio "1.0.0"
#define Arrel "..\.."
#define Bundle "..\build\dist\markdown-styler\*"

[Setup]
AppId={{8E4C1B2A-6D3F-4A97-9C2E-5B1F7D0A3C64}
AppName=Markdown Styler
AppVersion={#Versio}
AppVerName=Markdown Styler {#Versio}
AppPublisher=Pau Palacios Server
AppPublisherURL=https://github.com/PauPedreguer/MarkdownStyler
AppSupportURL=https://github.com/PauPedreguer/MarkdownStyler/issues
AppUpdatesURL=https://github.com/PauPedreguer/MarkdownStyler/releases
DefaultDirName={autopf}\MarkdownStyler
DefaultGroupName=Markdown Styler
DisableProgramGroupPage=yes
LicenseFile={#Arrel}\LICENSE
OutputDir=..\dist
OutputBaseFilename=MarkdownStyler-{#Versio}-setup
SetupIconFile=..\build\icones\icona.ico
UninstallDisplayIcon={app}\markdown-styler.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"

[Tasks]
Name: "desktopicon"; Description: "Crea una icona a l'escriptori"; \
    GroupDescription: "Icones addicionals:"; Flags: unchecked

[Files]
Source: "{#Bundle}"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Arrel}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Arrel}\THIRD-PARTY.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Markdown Styler"; Filename: "{app}\markdown-styler.exe"
Name: "{group}\Desinstal·la Markdown Styler"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Markdown Styler"; Filename: "{app}\markdown-styler.exe"; \
    Tasks: desktopicon

[Run]
Filename: "{app}\markdown-styler.exe"; Description: "Executa Markdown Styler"; \
    Flags: nowait postinstall skipifsilent
