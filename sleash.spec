# PyInstaller spec for Sleash Browser
# Build: pyinstaller sleash.spec --clean

import os
import PySide6

_p6_dir = os.path.dirname(PySide6.__file__)

def _p6(rel):
    return os.path.join(_p6_dir, rel.replace('/', os.sep))

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],   # QtWebEngineProcess.exe placed by hooks in _internal/PySide6/
    datas=[
        ('data', 'data'),
        ('adblock.py', '.'),
        ('browser.py', '.'),
        # WebEngine resources — placed inside PySide6/ to match Qt6WebEngineCore.dll location
        # Qt looks for resources at <dll_dir>/resources/ by default
        (_p6('resources/icudtl.dat'),                            'PySide6/resources'),
        (_p6('resources/qtwebengine_resources.pak'),             'PySide6/resources'),
        (_p6('resources/qtwebengine_devtools_resources.pak'),    'PySide6/resources'),
        (_p6('resources/qtwebengine_resources_100p.pak'),        'PySide6/resources'),
        (_p6('resources/qtwebengine_resources_200p.pak'),        'PySide6/resources'),
        # Locale translations — at <dll_dir>/translations/qtwebengine_locales/
        (_p6('translations/qtwebengine_locales'), 'PySide6/translations/qtwebengine_locales'),
    ],
    hiddenimports=[
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebChannel',
        'PySide6.QtNetwork',
        'PySide6.QtPrintSupport',
        'PySide6.QtPositioning',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DExtras',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DRender',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtMultimedia',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtSerialPort',
        'PySide6.QtSensors',
        'PySide6.QtLocation',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Sleash',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['QtWebEngineProcess.exe'],
    name='Sleash',
)
