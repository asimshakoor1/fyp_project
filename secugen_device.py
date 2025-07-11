import ctypes
import time

# 1) Load SecuGen library (bitness must match your Python interpreter)
dll_path = r"D:\secugen_drivers\FDx SDK Pro for Windows v4.21_J1.12\FDx SDK Pro for Windows v4.21\bin\x64\sgfplib.dll"
sgfplib = ctypes.WinDLL(dll_path)

print("DLL loaded successfully.")

# 2) Constants
DEVICE_AUTO_DETECT = 0x01
ERROR_NONE        = 0

# 3) Bind functions by their exact exported names:

# 3.1 CreateSGFPMObject
sgfplib.CreateSGFPMObject.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
sgfplib.CreateSGFPMObject.restype  = ctypes.c_int
time.sleep(2)
# 3.2 SGFPM_Init
sgfplib.SGFPM_Init.argtypes = [ctypes.c_void_p]
sgfplib.SGFPM_Init.restype  = ctypes.c_int

# 3.3 SGFPM_OpenDevice
sgfplib.SGFPM_OpenDevice.argtypes = [ctypes.c_void_p, ctypes.c_int]
sgfplib.SGFPM_OpenDevice.restype  = ctypes.c_int

# 3.4 SGFPM_GetDeviceInfo
class SGDeviceInfo(ctypes.Structure):
    _fields_ = [
        ("deviceID", ctypes.c_int),
        ("deviceType", ctypes.c_int),
        ("imageWidth", ctypes.c_int),
        ("imageHeight", ctypes.c_int),
        ("serialNumber", ctypes.c_char * 16),
    ]

sgfplib.SGFPM_GetDeviceInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(SGDeviceInfo)]
sgfplib.SGFPM_GetDeviceInfo.restype  = ctypes.c_int

# 3.5 SGFPM_GetImage
sgfplib.SGFPM_GetImage.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
sgfplib.SGFPM_GetImage.restype  = ctypes.c_int

# 3.6 SGFPM_CloseDevice
sgfplib.SGFPM_CloseDevice.argtypes = [ctypes.c_void_p]
sgfplib.SGFPM_CloseDevice.restype  = ctypes.c_int

# 3.7 DestroySGFPMObject (correct cleanup function)
sgfplib.DestroySGFPMObject.argtypes = [ctypes.c_void_p]
sgfplib.DestroySGFPMObject.restype  = ctypes.c_int


def capture_fingerprint():
    """
    Creates a SecuGen context, initializes the device, captures one fingerprint image,
    and returns the raw image buffer as a hexadecimal string.
    """
    hSgfplib = ctypes.c_void_p()

    # A) Create the SGFPM object
    res = sgfplib.CreateSGFPMObject(ctypes.byref(hSgfplib))
    if res != ERROR_NONE:
        raise Exception(f"CreateSGFPMObject failed (0x{res:02X})")

    # B) Initialize the library
    res = sgfplib.SGFPM_Init(hSgfplib)
    if res != ERROR_NONE:
        raise Exception(f"SGFPM_Init failed (0x{res:02X})")

    # C) Open the fingerprint device (auto-detect)
    res = sgfplib.SGFPM_OpenDevice(hSgfplib, DEVICE_AUTO_DETECT)
    if res != ERROR_NONE:
        raise Exception(f"SGFPM_OpenDevice failed (0x{res:02X})")

    # D) Get device info for image dimensions
    device_info = SGDeviceInfo()
    res = sgfplib.SGFPM_GetDeviceInfo(hSgfplib, ctypes.byref(device_info))
    if res != ERROR_NONE:
        raise Exception(f"SGFPM_GetDeviceInfo failed (0x{res:02X})")

    width = device_info.imageWidth
    height = device_info.imageHeight
    image_size = width * height
    buffer = ctypes.create_string_buffer(image_size)

    # E) Prompt and capture one fingerprint image
    print("Please place your finger on the scanner…")
    for attempt in range(30):
        res = sgfplib.SGFPM_GetImage(hSgfplib, buffer)
        if res == ERROR_NONE:
            print("Fingerprint captured!")
            break
        time.sleep(1)
    else:
        raise Exception("Timeout: No fingerprint detected after 30 seconds.")

    # F) Clean up
    sgfplib.SGFPM_CloseDevice(hSgfplib)
    sgfplib.DestroySGFPMObject(hSgfplib)

    # Return raw buffer as hex string
    return buffer.raw.hex()


if __name__ == "__main__":
    try:
        tpl = capture_fingerprint()
        print("Template (first 100 hex chars):", tpl[:100])
    except Exception as e:
        print("Error:", e)
