from distutils.core import setup
import py2exe

setup(options = {"py2exe": {"compressed": 1, "optimize": 2, "bundle_files": 1, "dll_excludes": ["w9xpopen.exe", "MSVCP90.dll"]}},
      zipfile = None,
	  windows=[{
	            "script": "snarl_notifications.py",
				"icon_resources": [(1, "icon.ico")]
				}])