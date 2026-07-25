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