"""Machine paths for the model generators, read from source/models/settings.local.json."""
import json
import os

_FILE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                      "settings.local.json"))

if not os.path.exists(_FILE):
    raise SystemExit("model generators: copy settings.example.json to settings.local.json next "
                     "to it and fill in the paths (%s)" % _FILE)
with open(_FILE, encoding="utf-8") as _fh:
    _S = json.load(_fh)

DAYZ_TOOLS = _S["dayz_tools"]
PDRIVE = _S["pdrive"]
FONTS = _S.get("fonts", "C:/Windows/Fonts/")
IMAGE_TO_PAA = os.path.join(DAYZ_TOOLS, "Bin", "ImageToPAA", "ImageToPAA.exe")
VANILLA_DZ = os.path.join(PDRIVE, "dz")
