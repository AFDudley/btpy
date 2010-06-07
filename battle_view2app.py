from distutils.core import setup
import py2app
import os, shutil
import commands

APP = ['views/battle_view.py']
DATA_FILES = ['views/DroidSansMono.ttf','yaml']
OPTIONS = {'argv_emulation': True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

#yes, sweet sweet hack
yeah = 'dist/battle_view.app/Contents/Resources/'
os.makedirs(yeah + 'views')
shutil.move(yeah + 'DroidSansMono.ttf', yeah +'views/DroidSansMono.ttf')
print "Converting app to dmg, please wait."
print commands.getstatusoutput('hdiutil create -imagekey zlib-level=9 -srcfolder dist/battle_view.app dist/battle_view.dmg')[1]