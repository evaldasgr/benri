import aqt

cfg = aqt.mw.addonManager.getConfig(__name__)

if cfg["benridict"]["enabled"] == True:
    from . import benridict
if cfg["benritalk"]["enabled"] == True:
    from . import benritalk
if cfg["benripaste"]["enabled"] == True:
    from . import benripaste
if cfg["benriocr"]["enabled"] == True:
    from . import benriocr
if cfg["benriclear"]["enabled"] == True:
    from . import benriclear
