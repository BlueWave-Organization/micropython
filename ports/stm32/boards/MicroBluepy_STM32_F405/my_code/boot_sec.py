import pyb
import uos
import machine
import micropython
import builtins

try:
    import hashlib
except ImportError:
    import uhashlib as hashlib

LICENSE_OTP_ADDR = 0x1FFF7820
UID_ADDR         = 0x1FFF7A10
OTP_BLOCK_5_ADDR = 0x1FFF78A0

RSA_N = bytes([
    0xD2, 0x28, 0x84, 0x34, 0x95, 0xDC, 0x31, 0x91, 0x3A, 0xB5, 0xC5, 0x42, 0xA2, 0x53, 0x5A, 0x46,
    0x00, 0x0F, 0x01, 0x5F, 0x20, 0xA6, 0x3A, 0xFD, 0xE4, 0x59, 0xD1, 0x2E, 0x17, 0x5E, 0x10, 0x0B,
    0xF1, 0xFA, 0xA6, 0xBD, 0x7B, 0xC4, 0xA2, 0xBD, 0x94, 0xFD, 0x66, 0x2A, 0x8B, 0x9C, 0x29, 0x09,
    0xBA, 0xE4, 0x0D, 0x53, 0xEB, 0x80, 0x04, 0x5F, 0xAA, 0x63, 0x5B, 0x8D, 0xD0, 0x58, 0x42, 0x21,
    0xCD, 0x8C, 0x77, 0x1C, 0x02, 0xFE, 0x79, 0x08, 0xBF, 0xD0, 0x87, 0xFC, 0xDE, 0xFF, 0x4A, 0xD2,
    0xA0, 0xE8, 0xB5, 0x2A, 0x30, 0x40, 0xCF, 0x63, 0xF8, 0xCD, 0x60, 0x35, 0x28, 0xE3, 0x44, 0x5E,
    0xFE, 0x65, 0xD6, 0x7A, 0x57, 0x54, 0x3A, 0xB8, 0x04, 0x5D, 0x17, 0xAA, 0x89, 0x4F, 0x51, 0x1F,
    0x1A, 0x8F, 0x16, 0x5C, 0x2A, 0x22, 0xA6, 0xE5, 0x90, 0xB3, 0xCA, 0xAA, 0xF1, 0x8F, 0x4D, 0xAF
])
RSA_E = 65537

def read_mem_bytes(addr, length):
    return bytes([machine.mem8[addr + i] for i in range(length)])

def verify_hardware_signature():
    try:
        signature = read_mem_bytes(LICENSE_OTP_ADDR, 128)
        phys_uid = read_mem_bytes(UID_ADDR, 12)
        uid_hash = hashlib.sha256(phys_uid).digest()
        
        sig_int = int.from_bytes(signature, 'big')
        n_int = int.from_bytes(RSA_N, 'big')
        
        recovered_int = pow(sig_int, RSA_E, n_int)
        recovered_bytes = recovered_int.to_bytes(128, 'big')
        
        for i in range(96):
            if recovered_bytes[i] != 0:
                return False
                
        if recovered_bytes[96:] != uid_hash:
            return False
            
        return True
    except Exception:
        return False

if not verify_hardware_signature():
    try:
        flash = pyb.Flash()
        uos.VfsFat.mkfs(flash)
    except Exception:
        pass

    try:
        sd = pyb.SDCard()
        if sd.present():
            uos.VfsFat.mkfs(sd)
    except Exception:
        pass
    
    try:
        pyb.usb_mode(None)
    except Exception:
        pass
        
    machine.disable_irq()
    micropython.kbd_intr(-1)

    try:
        led = machine.Pin('A13', machine.Pin.OUT)
        while True:
            led.value(1)
            for _ in range(800000): pass 
            led.value(0)
            for _ in range(800000): pass
    except Exception:
        while True:
            pass

micropython.kbd_intr(3)

class BlueCoreSystem:
    def __init__(self):
        uid_bytes = read_mem_bytes(UID_ADDR, 12)
        otp_custom_data = read_mem_bytes(OTP_BLOCK_5_ADDR, 128)
        super().__setattr__('_hw_uid', uid_bytes)
        super().__setattr__('_otp_payload', otp_custom_data)

    @property
    def HARDWARE_UID(self):
        return self._hw_uid

    @property
    def OTP_PAYLOAD(self):
        return self._otp_payload

    def __setattr__(self, name, value):
        raise AttributeError("Access Denied: Read-Only System")

try:
    builtins.BlueCore
except AttributeError:
    builtins.BlueCore = BlueCoreSystem()