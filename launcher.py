#!/usr/bin/env python
import sys, subprocess, shutil, os

# 1) Ensure pip packages
REQUIRED_PKGS = ["flet", "pyomo"]
for pkg in REQUIRED_PKGS:
    try:
        __import__(pkg)
    except ImportError:
        print(f"[launcher] Installing missing package: {pkg}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

# 2) Ensure glpsol is available
GLPSOL = shutil.which("glpsol") or os.path.join(os.path.dirname(__file__), "glpsol.exe")
if not os.path.isfile(GLPSOL) and not shutil.which("glpsol"):
    print("[launcher] ERROR: glpsol.exe not found. Place it next to launcher.py or on PATH.")
    sys.exit(1)

# 3) Launch your actual Flet app
#    If your entrypoint is main.py and defines a `GUI` target, adjust accordingly:
from PlannerGUI import GUI  
import flet

if __name__ == "__main__":
    # Pass glpsol path via environment so your planner can pick it up:
    os.environ["GLPSOL_PATH"] = GLPSOL
    flet.app(target=GUI)
