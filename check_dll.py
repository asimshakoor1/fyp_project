import ctypes

dll_path = r"D:\secugen\FDx SDK Pro for Windows v4.3.1_J1.12\FDx SDK Pro for Windows v4.3.1\bin\x64\sgfplib.dll"
sgfplib = ctypes.WinDLL(dll_path)

try:
    func = sgfplib.SGFPM_CreateSGFPMObject
    print("Function SGFPM_CreateSGFPMObject found!")
except AttributeError:
    print("Function SGFPM_CreateSGFPMObject NOT found.")
