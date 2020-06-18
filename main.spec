# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['D:/PYTHON/Games/Lines2020/main.py'],
             pathex=['D:/PYTHON/Games/Lines2020/classes', 'D:/PYTHON/Games/Lines2020/utils', 'D:\\PYTHON\\Games\\Lines2020'],
             binaries=[],
             datas=[('D:/PYTHON/Games/Lines2020/config.yaml', '.'), ('D:/PYTHON/Games/Lines2020/audio', 'audio/'), ('D:/PYTHON/Games/Lines2020/fonts', 'fonts/'), ('D:/PYTHON/Games/Lines2020/logs', 'logs/'), ('D:/PYTHON/Games/Lines2020/sprites', 'sprites/'), ('D:/PYTHON/Games/Lines2020/tests', 'tests/')],
             hiddenimports=["'pkg_resources.py2_warn'"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
