import pyb

pyb.usb_mode('VCP+MSC')

try:
    import boot_sec
except Exception:
    pass

try:
    import mylogo
except Exception:
    pass
    
import os
cwd = os.getcwd()         
try:
    os.stat(cwd + '/boot.py')
    exec(open(cwd + '/boot.py').read())
except OSError:
    pass
