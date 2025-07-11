import random
import string
import time

def capture_fingerprint():
    # Simulate a delay like real sensor
    time.sleep(2)
    
    # Generate random fingerprint string
    return ''.join(random.choices(string.ascii_uppercase + string.digits,k=64))