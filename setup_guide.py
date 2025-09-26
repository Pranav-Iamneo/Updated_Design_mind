#!/usr/bin/env python3
"""
Setup Guide and PDF Validation Script for DesignMind GenAI LangGraph
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'langgraph', 
        'langchain-core',
        'langchain-google-genai',
        'google-generativeai',
        'pydantic',
        'pandas',
        'matplotlib',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        'GEMINI_API_KEY',
        'GEMINI_API_KEY_1',
        'GEMINI_API_KEY_2', 
        'GEMINI_API_KEY_3',
        'GEMINI_API_KEY_4'
    ]
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Create .env file with your Gemini API keys")
        return False
    
    missing_vars = []
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    for var in required_vars:
        if var not in env_content or f"{var}=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_pdf_files():
    """Check PDF files in data directory"""
    data_dir = Path('data')
    if not data_dir.exists():
        print("❌ data/ directory not found")
        data_dir.mkdir(parents=True, exist_ok=True)
        print("📁 Created data/ directory")
        return False
    
    pdf_files = list(data_dir.glob('*.pdf'))
    pdf_files = [f for f in pdf_files if f.is_file()]  # Exclude directories
    
    if not pdf_files:
        print("❌ No PDF files found in data/ directory")
        print("📄 Add PDF requirement documents to data/ folder")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files:")
    total_size = 0
    for pdf_file in pdf_files:
        size_mb = pdf_file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"   📄 {pdf_file.name} ({size_mb:.2f} MB)")
    
    print(f"📊 Total size: {total_size:.2f} MB")
    return True

def validate_pdf_content(pdf_path: Path):
    """Basic PDF validation"""
    try:
        # Try to read first few bytes to check if it's a valid PDF
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF-'):
                return False, "Not a valid PDF file"
        
        # Check file size
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            return False, f"File too large ({size_mb:.2f} MB). Consider files under 50MB"
        
        return True, "Valid PDF"
    
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def run_system_check():
    """Run comprehensive system check"""
    print("🔍 DesignMind GenAI LangGraph - System Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("PDF Files", check_pdf_files)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Ready to run DesignMind GenAI")
        print("🚀 Run: streamlit run main.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    
    return all_passed

def create_sample_env():
    """Create sample .env file"""
    env_content = """# Gemini API Keys (required)
GEMINI_API_KEY=your_primary_gemini_key_here
GEMINI_API_KEY_1=your_auth_integrations_key
GEMINI_API_KEY_2=your_behavior_quality_key
GEMINI_API_KEY_3=your_domain_api_key
GEMINI_API_KEY_4=your_pdf_extractor_key

# Model Configuration
GEMINI_MODEL=gemini-2.0-flash-exp

# Diagram Rendering
KROKI_URL=https://kroki.io

# LangGraph Configuration (optional)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langsmith_key_optional
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        env_file.write_text(env_content)
        print("✅ Created .env template file")
        print("📝 Please edit .env and add your actual API keys")
    else:
        print("ℹ️ .env file already exists")

def show_pdf_requirements():
    """Show PDF requirements and tips"""
    print("\n📄 PDF Requirements:")
    print("• File format: PDF (.pdf)")
    print("• Size limit: Under 50MB recommended")
    print("• Content: Technical requirements, PRDs, specifications")
    print("• Language: English (for best results)")
    print("• Structure: Well-formatted with headings and sections")
    
    print("\n💡 Tips for better results:")
    print("• Use clear, structured documents")
    print("• Include functional and non-functional requirements")
    print("• Mention system integrations and APIs")
    print("• Specify security and authentication needs")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'check':
            run_system_check()
        elif command == 'env':
            create_sample_env()
        elif command == 'pdf':
            show_pdf_requirements()
        elif command == 'validate':
            data_dir = Path('data')
            if data_dir.exists():
                pdf_files = list(data_dir.glob('*.pdf'))
                for pdf_file in pdf_files:
                    valid, message = validate_pdf_content(pdf_file)
                    status = "✅" if valid else "❌"
                    print(f"{status} {pdf_file.name}: {message}")
            else:
                print("❌ data/ directory not found")
        else:
            print("❌ Unknown command")
            show_help()
    else:
        show_help()

def show_help():
    """Show help information"""
    print("🧠 DesignMind GenAI LangGraph - Setup Guide")
    print("\nUsage: python setup_guide.py <command>")
    print("\nCommands:")
    print("  check     - Run comprehensive system check")
    print("  env       - Create sample .env file")
    print("  pdf       - Show PDF requirements and tips")
    print("  validate  - Validate PDF files in data/ directory")
    print("\nExamples:")
    print("  python setup_guide.py check")
    print("  python setup_guide.py env")
    print("  python setup_guide.py validate")

if __name__ == "__main__":
    main()