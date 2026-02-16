import os
import sys
import subprocess

def check_files():
    essential_files = [
        'fprintdcs.py', 'extract_template.py', 'restore_config.py', 
        'helpers_dcs.py', 'helpers_generic.py', 'requirements.txt', 'version.txt'
    ]
    print("--- 📦 Checking Files ---")
    for f in essential_files:
        if os.path.exists(f):
            print(f"✅ {f} found.")
        else:
            print(f"❌ {f} MISSING!")

def check_version():
    if os.path.exists('version.txt'):
        print("\n--- 📝 Build Info ---")
        with open('version.txt', 'r') as f:
            print(f.read().strip())

def check_dependencies():
    print("\n--- 📦 Checking Dependencies ---")
    try:
        # This checks if the packages in requirements.txt are actually met
        subprocess.check_call([sys.executable, '-m', 'pip', 'check'])
        print("✅ All python dependencies satisfied.")
    except subprocess.CalledProcessError:
        print("⚠️  Dependency conflict or missing packages detected.")
        print("Run: pip install -r requirements.txt")

if __name__ == "__main__":
    check_files()
    check_version()
    check_dependencies()
    print("\nVerification Complete.")