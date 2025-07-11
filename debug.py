import ctypes
import time

# 1) Load SecuGen library (bitness must match your Python)
dll_path = r"C:\Users\COMPUTER CORNER\Downloads\FDx SDK Pro for Windows v4.3.1_J1.12\FDx SDK Pro for Windows v4.3.1\bin\x64\sgfplib.dll"
sgfplib = ctypes.WinDLL(dll_path)

print("DLL loaded successfully.")

# 2) Constants
DEVICE_AUTO_DETECT = 0x01
ERROR_NONE = 0

# 3) Define function signatures

sgfplib.CreateSGFPMObject.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
sgfplib.CreateSGFPMObject.restype = ctypes.c_int

sgfplib.SGFPM_Init.argtypes = [ctypes.c_void_p]
sgfplib.SGFPM_Init.restype = ctypes.c_int

sgfplib.SGFPM_OpenDevice.argtypes = [ctypes.c_void_p, ctypes.c_int]
sgfplib.SGFPM_OpenDevice.restype = ctypes.c_int

sgfplib.SGFPM_CloseDevice.argtypes = [ctypes.c_void_p]
sgfplib.SGFPM_CloseDevice.restype = ctypes.c_int

sgfplib.DestroySGFPMObject.argtypes = [ctypes.c_void_p]
sgfplib.DestroySGFPMObject.restype = ctypes.c_int

class SGDeviceInfo(ctypes.Structure):
    _fields_ = [
        ("deviceID", ctypes.c_int),
        ("deviceType", ctypes.c_int),
        ("imageWidth", ctypes.c_int),
        ("imageHeight", ctypes.c_int),
        ("serialNumber", ctypes.c_char * 16),
    ]

sgfplib.SGFPM_GetDeviceInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(SGDeviceInfo)]
sgfplib.SGFPM_GetDeviceInfo.restype = ctypes.c_int

sgfplib.SGFPM_GetImage.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
sgfplib.SGFPM_GetImage.restype = ctypes.c_int


def capture_fingerprint():
    hSgfplib = ctypes.c_void_p()

    print("Step 1: Creating SGFPM object...")
    res = sgfplib.CreateSGFPMObject(ctypes.byref(hSgfplib))
    if res != ERROR_NONE:
        raise Exception(f"CreateSGFPMObject failed (0x{res:02X})")
    print("✓ SGFPM object created.")

    print("Step 2: Initializing device...")
    res = sgfplib.SGFPM_Init(hSgfplib)
    print(f"SGFPM_Init result: 0x{res:02X}")
    if res != ERROR_NONE:
        raise Exception(f"SGFPM_Init failed (0x{res:02X})")
    print("✓ Initialization successful.")

    print("Step 3: Opening fingerprint device (auto-detect)...")
    res = sgfplib.SGFPM_OpenDevice(hSgfplib, DEVICE_AUTO_DETECT)
    print(f"SGFPM_OpenDevice result: 0x{res:02X}")
    if res != ERROR_NONE:
        raise Exception(f"SGFPM_OpenDevice failed (0x{res:02X})")
    print("✓ Device opened successfully.")

    print("Step 4: Getting device info...")
    device_info = SGDeviceInfo()
    res = sgfplib.SGFPM_GetDeviceInfo(hSgfplib, ctypes.byref(device_info))
    if res != ERROR_NONE:
        raise Exception(f"SGFPM_GetDeviceInfo failed (0x{res:02X})")
    print(f"✓ Device Info → Width: {device_info.imageWidth}, Height: {device_info.imageHeight}, Serial: {device_info.serialNumber.decode(errors='ignore')}")

    width = device_info.imageWidth
    height = device_info.imageHeight
    image_size = width * height
    buffer = ctypes.create_string_buffer(image_size)

    print("Step 5: Please place your finger on the scanner…")
    for attempt in range(30):
        res = sgfplib.SGFPM_GetImage(hSgfplib, buffer)
        if res == ERROR_NONE:
            print("✓ Fingerprint image captured successfully.")
            break
        else:
            print(f"Attempt {attempt + 1}/30 failed. Waiting...")
        time.sleep(1)
    else:
        raise Exception("Timeout: No fingerprint detected after 30 seconds.")

    print("Step 6: Cleaning up...")
    sgfplib.SGFPM_CloseDevice(hSgfplib)
    sgfplib.DestroySGFPMObject(hSgfplib)
    print("✓ Device closed and object destroyed.")

    return buffer.raw.hex()


if __name__ == "__main__":
    try:
        hex_image = capture_fingerprint()
        print("Captured Fingerprint (First 100 hex chars):")
        print(hex_image[:100])
    except Exception as e:
        print("❌ Error:", e)
