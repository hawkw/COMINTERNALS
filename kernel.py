import cominternals, re, os

modifier = r"""const|volatile|extern|static|register|signed|unsigned|__inline__|inline"""

header_name = re.compile(r"""^(?:(?""" + modifier +
                         r""")\s+)*[a-zA-Z_0-9]+[\s\*]+([a-zA-Z_0-9]+).+$|""" +
                         r"""#define\s+([a-zA-Z_0-9]+).+$""")

def header_names(path):
    """Generates a list of names defined in the header file at `path`."""
    with open(path) as f:
        for line in f:
            match = header_name.match(line)
            if match:
                name = match.group(2) if match.group(2) else match.group(1)
                print("found name {} in header {}".format(name, path))
                yield name

def headers_in(dir):
    """Generates a list of header files in directory `dir`."""
    for _, _, filenames in os.walk(dir):
        for f in filenames:
            if f.endswith(".h"): yield f
