#!/usr/bin/env python3
"""
Module 4 Setup Script - AI-Powered Solutions & Executive Strategy
Configures OpenAI integration and generates business intelligence
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_module_4():
    """Setup Module 4 AI-powered components"""
    
    print("🚀 Setting up Module 4: AI-Powered Solutions & Executive Strategy")
    print("=" * 60)
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API Key not found")
        print("📝 Set your OpenAI API key: export OPENAI_API_KEY='your-key'")
        print("🔗 Get API key: https://platform.openai.com/api-keys")
    else:
        print("✅ OpenAI API key found")
    
    # Install required packages
    print("\n📦 Installing required packages...")
    packages = ['openai>=1.0.0', 'pandas>=1.5.0', 'numpy>=1.21.0']
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except subprocess.CalledProcessError:
            print(f"⚠️  Could not install {package}")
    
    print("✅ Setup complete!")
    print("\n🚀 Launch: python3 -m http.server 8080")
    print("📱 Access: http://localhost:8080/ai_powered_dashboard.html")
    return True

if __name__ == "__main__":
    setup_module_4()