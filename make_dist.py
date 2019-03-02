
import os
import sys
#import zipfile
#import zlib
import shutil

from quirc.common import *

#compression = zipfile.ZIP_DEFLATED

os.mkdir("./dist")
os.mkdir("./dist/data")

os.system("compile_resources.bat")

shutil.copytree("./quirc", "./dist/quirc",ignore=shutil.ignore_patterns('*.pyc', 'tmp*',"__pycache__"))

shutil.copy("./quirc.py", "./dist/quirc.py")

shutil.copy("./CHANGELOG", "./dist/CHANGELOG")
shutil.copy("./LICENSE", "./dist/LICENSE")
shutil.copy("./README.md", "./dist/README.md")

shutil.copy("./data/user.json", "./dist/data/user.json")

os.system("powershell.exe -nologo -noprofile -command \"& { Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::CreateFromDirectory('dist', 'quirc_dist.zip'); }\" ")

shutil.rmtree('./dist')

os.rename('quirc_dist.zip', f"{APPLICATION_NAME.lower()}-{APPLICATION_VERSION}.zip")

