
import glob
import os

fl = []

for file in glob.glob("*.png"):
	fl.append(f"<file>{file}</file>")

fl.append("<file>FiraCode-Regular.ttf</file>")

fl.append("<file>style.qss</file>")

rfiles = "\n".join(fl)

out = f"""
<RCC>
<qresource>
{rfiles}
</qresource>
</RCC>
"""

print(out)
