; ============================================================
; STRIKE Aerospace - Mission Control Installer
; Inno Setup Script
; ============================================================
; Para compilar este script necesitas Inno Setup:
;   https://jrsoftware.org/isdl.php
;
; PASOS:
;   1. Primero genera el build con PyInstaller (ver build.bat)
;   2. Abre este archivo en Inno Setup Compiler
;   3. Click en "Compile" (Ctrl+F9)
;   4. El instalador se genera en la carpeta "installer_output/"
; ============================================================

#define MyAppName "STRIKE Mission Control"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "S.T.R.I.K.E Aerospace"
#define MyAppExeName "STRIKE_Mission_Control.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=STRIKE_Mission_Control_Setup_v{#MyAppVersion}
SetupIconFile=assets\LogoSTRIKE300.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
AllowNoIcons=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el &Escritorio"; GroupDescription: "Accesos directos:"
Name: "startmenuicon"; Description: "Crear acceso directo en el &Menú Inicio"; GroupDescription: "Accesos directos:"

[Files]
Source: "dist\STRIKE_Mission_Control\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

[Registry]
; Guardar la ruta de datos del usuario para poder limpiar al desinstalar
Root: HKCU; Subkey: "Software\STRIKE_Aerospace"; ValueType: string; ValueName: "DataDir"; ValueData: "{userdocs}\STRIKE_Aerospace"; Flags: uninsdeletekey

[UninstallDelete]
; Limpiar carpeta de instalación
Type: filesandordirs; Name: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent shellexec

[Code]
// Eliminar la carpeta de datos en Documentos al desinstalar
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
  UserProfile: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Intento 1: Leer ruta guardada en el registro
    if RegQueryStringValue(HKEY_CURRENT_USER, 'Software\STRIKE_Aerospace', 'DataDir', DataDir) then
    begin
      if DirExists(DataDir) then
        DelTree(DataDir, True, True, True);
    end;

    // Intento 2: Usar {userdocs}
    DataDir := ExpandConstant('{userdocs}\STRIKE_Aerospace');
    if DirExists(DataDir) then
      DelTree(DataDir, True, True, True);

    // Intento 3: Usar %USERPROFILE%\Documents como respaldo
    UserProfile := GetEnv('USERPROFILE');
    if UserProfile <> '' then
    begin
      DataDir := UserProfile + '\Documents\STRIKE_Aerospace';
      if DirExists(DataDir) then
        DelTree(DataDir, True, True, True);
    end;

    // Limpiar clave del registro
    RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, 'Software\STRIKE_Aerospace');
  end;
end;

