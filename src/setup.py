from distutils.core import setup
import py2exe

setup(
    name = "ngqlauncher",
    version = "0.1",
    windows = [{"script":"ngq_manager.py"}, {"script":"ngq_client.py"}],
    #console = [{"script":"test.py"}],
    #options={"py2exe": {'bundle_files': 1, 'compressed': True, "includes":["SIP"]}},
    options={"py2exe": {"includes":["sip"]}},
    data_files = [
        (
            'imageformats', [
                r'c:\\Python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qico4.dll'
            ]
        ),
        r'ngq.ico',
        r'project_types.json',
        r'mnemonic_diagrams.json',
     ]
)