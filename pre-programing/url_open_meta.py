import re
import sys
from urllib.request import urlopen

curl = sys.argv[1]
f = urlopen(curl)
#f = urlopen("http://sample.scraping-book.com/dp")

bytes_content = f.read()
scanned_text = bytes_content[:1024].decode('ascii', errors="replace")

#match = re.search(r"charset=[\"']?([w-]+)", scanned_text)
match = re.search(r"charset=(.+)?\"", scanned_text)
if match:
    encoding = match.group(1)
else:
    encoding = "utf-8"

print("encoding:", encoding, file=sys.stderr)

text = bytes_content.decode(encoding)
print(text)