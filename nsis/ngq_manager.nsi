SetCompressor /SOLID lzma
RequestExecutionLevel admin

!define PROGRAM_NAME "NGQ Manager"
!define PROGRAM_NAME_FOR_DIR "NGQManager"
!define INSTALLER_NAME "ngq_manager"
!define COMPILE_CODE_DIR "..\src\dist"

!define NEXTGIS_QGIS "NextGIS QGIS"
!define REGISTER_ROOT_KEY "ngq"

!define INSTALL_DIR_NAME "ngqmanager"

;--------------------------------
;Configuration

Name "${PROGRAM_NAME}"
OutFile "${INSTALLER_NAME}.exe"
InstallDir ""

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "if_key_exists.nsh"

ShowInstDetails show
;ShowUnInstDetails show
 
;--------------------------------
;Pages

;!insertmacro MUI_PAGE_WELCOME
;!insertmacro MUI_PAGE_LICENSE "..\Installer-Files\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
;!insertmacro MUI_PAGE_FINISH

Section "MAIN" MAIN
	SectionIn RO
    SetOutPath "$INSTDIR\${INSTALL_DIR_NAME}"
    File /r "${COMPILE_CODE_DIR}\*.*"
	
    WriteRegStr HKCR "${REGISTER_ROOT_KEY}" "" 'URL:ngq Protocol'
	WriteRegStr HKCR "${REGISTER_ROOT_KEY}" "URL Protocol" ''
	WriteRegStr HKCR "${REGISTER_ROOT_KEY}\Shell\open\command" "" '"$INSTDIR\${INSTALL_DIR_NAME}\ngq_manager.exe" "--uri" "%1"'
	
SectionEnd


Section "NSI Emulator" TEST_APP
    WriteRegStr HKCR "visidata" "" 'URL:visidata Protocol'
    WriteRegStr HKCR "visidata" "URL Protocol" ''
    WriteRegStr HKCR "visidata\Shell\open\command" "" '"$INSTDIR\${INSTALL_DIR_NAME}\ngq_client.exe" "%1"'

    CreateShortCut "$DESKTOP\Emulator.lnk" "$INSTDIR\${INSTALL_DIR_NAME}\ngq_client.exe" \
        "" "$INSTDIR\${INSTALL_DIR_NAME}\ngq.ico" 0 SW_SHOWNORMAL "" "Run emulator!"
SectionEnd

Function .onInit
    !insertmacro IfKeyExists HKLM "Software" "${NEXTGIS_QGIS}"
    Pop $R0
    ${If} $R0 = 1
    	ReadRegStr $0 HKLM "Software\${NEXTGIS_QGIS}" "InstallPath"
    	StrCpy $InstDir $0
    ${EndIf}
FunctionEnd
