#!/usr/bin/env python3
"""
Project setup and activation script
"""

import os
import sys
import subprocess
from pathlib import Path

def activate_environment():
    """Activate the virtual environment"""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"
    
    if not venv_path.exists():
        print("❌ Virtual environment not found. Run 'uv venv' first.")
        return False
    
    # For scripts running in activated environment
    if sys.prefix != sys.base_prefix:
        print("✅ Virtual environment already activated")
        return True
    
    # Instructions for manual activation
    activate_script = venv_path / "bin" / "activate"
    print(f"🔧 To activate the virtual environment, run:")
    print(f"source {activate_script}")
    
    return True

def check_packages():
    """Check if required packages are installed"""
    required_packages = [
        'pandas', 'plotly', 'jupyter', 'openpyxl', 
        'xlrd', 'notebook', 'ipykernel'
    ]
    
    print("📦 Checking installed packages...")
    
    try:
        import pkg_resources
        
        for package in required_packages:
            try:
                version = pkg_resources.get_distribution(package).version
                print(f"✅ {package}: {version}")
            except pkg_resources.DistributionNotFound:
                print(f"❌ {package}: Not installed")
                return False
        
        return True
        
    except ImportError:
        print("❌ setuptools not available")
        return False

def start_jupyter():
    """Start Jupyter notebook server"""
    notebooks_dir = Path(__file__).parent / "notebooks"
    
    if not notebooks_dir.exists():
        notebooks_dir.mkdir(exist_ok=True)
    
    print(f"🚀 Starting Jupyter notebook server...")
    print(f"📁 Notebook directory: {notebooks_dir}")
    
    try:
        os.chdir(notebooks_dir)
        subprocess.run(["jupyter", "notebook"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Jupyter: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Jupyter server stopped")
        return True

def main():
    """Main setup function"""
    print("🔧 Goedgekeurde Vergunningen Project Setup")
    print("=" * 50)
    
    # Check environment
    if not activate_environment():
        sys.exit(1)
    
    # Check packages
    if not check_packages():
        print("\n💡 To install missing packages, run:")
        print("uv pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n✅ Environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Place your Excel files in the 'data/' folder")
    print("2. Start Jupyter notebook server")
    print("3. Open 'notebooks/data_analysis_setup.ipynb' to begin analysis")
    
    # Ask if user wants to start Jupyter
    response = input("\n🚀 Start Jupyter notebook server now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        start_jupyter()

if __name__ == "__main__":
    main()
