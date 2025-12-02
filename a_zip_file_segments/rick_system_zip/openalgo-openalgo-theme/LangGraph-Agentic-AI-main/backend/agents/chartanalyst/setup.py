#!/usr/bin/env python3
"""
ChartAnalyst Setup and Installation Script
Handles dependencies, configuration, and initial setup
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class ChartAnalystSetup:
    """Setup class for ChartAnalyst installation"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.os_type = platform.system().lower()
        self.python_version = sys.version_info
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        if self.python_version < (3, 8):
            print("❌ Python 3.8 or higher is required")
            print(f"Current version: {sys.version}")
            sys.exit(1)
        else:
            print(f"✅ Python {sys.version.split()[0]} is compatible")
    
    def install_system_dependencies(self):
        """Install system dependencies based on OS"""
        print("\n?? Installing system dependencies...")
        
        if self.os_type == "linux":
            self._install_linux_deps()
        elif self.os_type == "darwin":  # macOS
            self._install_macos_deps()
        elif self.os_type == "windows":
            self._install_windows_deps()
        else:
            print(f"⚠️  Unsupported OS: {self.os_type}")
            print("You may need to install TA-Lib manually")
    
    def _install_linux_deps(self):
        """Install Linux dependencies"""
        try:
            # Check if we can use apt-get
            if shutil.which("apt-get"):
                print("Installing TA-Lib dependencies with apt-get...")
                subprocess.run([
                    "sudo", "apt-get", "update"
                ], check=True)
                subprocess.run([
                    "sudo", "apt-get", "install", "-y",
                    "build-essential", "wget", "python3-dev"
                ], check=True)
                self._install_talib_from_source()
                
            elif shutil.which("yum"):
                print("Installing TA-Lib dependencies with yum...")
                subprocess.run([
                    "sudo", "yum", "groupinstall", "-y", "Development Tools"
                ], check=True)
                subprocess.run([
                    "sudo", "yum", "install", "-y", "wget", "python3-devel"
                ], check=True)
                self._install_talib_from_source()
            else:
                print("⚠️  No package manager found. Please install TA-Lib manually")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install system dependencies: {e}")
            print("Please install TA-Lib manually")
    
    def _install_macos_deps(self):
        """Install macOS dependencies"""
        try:
            if shutil.which("brew"):
                print("Installing TA-Lib with Homebrew...")
                subprocess.run(["brew", "install", "ta-lib"], check=True)
            else:
                print("Homebrew not found. Installing from source...")
                self._install_talib_from_source()
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install TA-Lib: {e}")
            self._install_talib_from_source()
    
    def _install_windows_deps(self):
        """Install Windows dependencies"""
        print("For Windows, please install TA-Lib manually:")
        print("1. Download TA-Lib from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib")
        print("2. Install with: pip install TA_Lib‑0.4.XX‑cp39‑cp39‑win_amd64.whl")
        print("3. Or use conda: conda install -c conda-forge ta-lib")
        
        input("Press Enter after installing TA-Lib...")
    
    def _install_talib_from_source(self):
        """Install TA-Lib from source"""
        try:
            print("Installing TA-Lib from source...")
            
            # Download and extract
            subprocess.run([
                "wget", "http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
            ], check=True)
            subprocess.run(["tar", "-xzf", "ta-lib-0.4.0-src.tar.gz"], check=True)
            
            # Compile and install
            os.chdir("ta-lib")
            subprocess.run(["./configure", "--prefix=/usr/local"], check=True)
            subprocess.run(["make"], check=True)
            subprocess.run(["sudo", "make", "install"], check=True)
            
            # Cleanup
            os.chdir("..")
            shutil.rmtree("ta-lib")
            os.remove("ta-lib-0.4.0-src.tar.gz")
            
            print("✅ TA-Lib installed successfully")
            
        except Exception as e:
            print(f"❌ Failed to install TA-Lib from source: {e}")
            print("Please install TA-Lib manually")
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("\n?? Installing Python dependencies...")
        
        try:
            # Upgrade pip first
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True)
            
            # Install from requirements.txt
            requirements_file = self.root_dir / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
                print("✅ Python dependencies installed successfully")
            else:
                print("❌ requirements.txt not found")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            sys.exit(1)
    
    def setup_environment(self):
        """Set up environment configuration"""
        print("\n⚙️  Setting up environment...")
        
        env_file = self.root_dir / ".env"
        env_example = self.root_dir / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("?? Please edit .env file with your API keys")
        elif env_file.exists():
            print("✅ .env file already exists")
        else:
            print("⚠️  No .env.example found")
    
    def create_directories(self):
        """Create necessary directories"""
        print("\n?? Creating directories...")
        
        dirs_to_create = [
            "logs",
            "data",
            "backups"
        ]
        
        for dir_name in dirs_to_create:
            dir_path = self.root_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created {dir_name}/ directory")
    
    def test_installation(self):
        """Test the installation"""
        print("\n?? Testing installation...")
        
        try:
            # Test TA-Lib import
            import talib
            print("✅ TA-Lib import successful")
            
            # Test other critical imports
            import pandas as pd
            import numpy as np
            import redis
            print("✅ Core dependencies import successful")
            
            # Test ChartAnalyst import
            sys.path.append(str(self.root_dir))
            from chartanalyst_main import ChartAnalyst
            analyst = ChartAnalyst()
            print("✅ ChartAnalyst initialization successful")
            
            print("\n?? Installation completed successfully!")
            return True
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def print_post_install_instructions(self):
        """Print instructions for after installation"""
        print("\n?? POST-INSTALLATION INSTRUCTIONS")
        print("=" * 40)
        print("1. Edit .env file with your API keys:")
        print("   - BINANCE_API_KEY (for crypto data)")
        print("   - REDIS_URL (if using Redis event bus)")
        print("")
        print("2. Test your installation:")
        print("   python test_chartanalyst.py")
        print("")
        print("3. Run single analysis:")
        print("   python test_chartanalyst.py single BTCUSDT 1h")
        print("")
        print("4. Run comprehensive tests:")
        print("   python test_chartanalyst.py comprehensive")
        print("")
        print("5. Start the main analyzer:")
        print("   python chartanalyst_main.py")
        print("")
        print("?? For more help, run: python test_chartanalyst.py help")
    
    def run_setup(self):
        """Run complete setup process"""
        print("?? ChartAnalyst Setup")
        print("=" * 30)
        
        # Check Python version
        self.check_python_version()
        
        # Install system dependencies
        self.install_system_dependencies()
        
        # Install Python dependencies
        self.install_python_dependencies()
        
        # Setup environment
        self.setup_environment()
        
        # Create directories
        self.create_directories()
        
        # Test installation
        success = self.test_installation()
        
        # Print instructions
        self.print_post_install_instructions()
        
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n⚠️  Setup completed with warnings. Please check the errors above.")
        
        return success

def main():
    """Main setup function"""
    setup = ChartAnalystSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-only":
        # Only run tests, skip installation
        success = setup.test_installation()
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        return success
    
    # Run full setup
    return setup.run_setup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
