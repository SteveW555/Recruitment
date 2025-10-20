import re
from pathlib import Path
text = Path("firecrawl_mcp_doc.html").read_text(encoding="utf-8")
match = re.search(r"\"compiledSource\":\"(.*?)\"\}\}\],\"\$undefined\"", text)
if not match:
    print("not found")
else:
    src = bytes(match.group(1), "utf-8").decode("unicode_escape")
    print(src)
