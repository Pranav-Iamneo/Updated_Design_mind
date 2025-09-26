#!/usr/bin/env python3
"""
Quick validation script to test PDF detection and basic functionality
"""

import sys
from pathlib import Path

def test_pdf_detection():
    """Test if PDFs are properly detected"""
    print("🔍 Testing PDF Detection...")
    
    # Import the function from main.py
    sys.path.append('.')
    try:
        from main import list_requirement_pdfs, get_pdf_info
        
        # Test PDF detection
        pdf_files = list_requirement_pdfs()
        print(f"✅ Found {len(pdf_files)} PDF files")
        
        if pdf_files:
            print("\n📄 Detected PDF files:")
            for pdf_path in pdf_files:
                info = get_pdf_info(pdf_path)
                if info:
                    print(f"   • {info['name']} ({info.get('size_mb', 'N/A')} MB)")
                else:
                    print(f"   • {Path(pdf_path).name} (info unavailable)")
            
            # Test file selection simulation
            print(f"\n🎯 File selection test:")
            file_names = [Path(p).name for p in pdf_files]
            options = ["— Select a requirements file —"] + file_names
            print(f"   Dropdown options: {len(options)} items")
            print(f"   First few options: {options[:4]}...")
            
            return True
        else:
            print("❌ No PDF files detected")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_data_directory():
    """Test data directory structure"""
    print("\n🗂️ Testing Data Directory...")
    
    data_dir = Path('data')
    if not data_dir.exists():
        print("❌ data/ directory not found")
        return False
    
    print("✅ data/ directory exists")
    
    # List all files
    all_files = list(data_dir.iterdir())
    pdf_files = [f for f in all_files if f.suffix.lower() == '.pdf' and f.is_file()]
    other_files = [f for f in all_files if f.suffix.lower() != '.pdf']
    
    print(f"📊 Directory contents:")
    print(f"   • PDF files: {len(pdf_files)}")
    print(f"   • Other files: {len(other_files)}")
    
    if pdf_files:
        print(f"\n📄 PDF files found:")
        for pdf_file in sorted(pdf_files):
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"   • {pdf_file.name} ({size_mb:.2f} MB)")
    
    return len(pdf_files) > 0

def test_imports():
    """Test if all required modules can be imported"""
    print("\n📦 Testing Imports...")
    
    required_modules = [
        ('streamlit', 'st'),
        ('pandas', 'pd'),
        ('pathlib', 'Path'),
        ('datetime', 'datetime'),
    ]
    
    optional_modules = [
        ('langgraph', None),
        ('langchain_core', None),
        ('google.generativeai', 'genai'),
        ('pydantic', None),
    ]
    
    success = True
    
    # Test required modules
    for module, alias in required_modules:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} (required)")
            success = False
    
    # Test optional modules (for full functionality)
    for module, alias in optional_modules:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            print(f"✅ {module}")
        except ImportError:
            print(f"⚠️ {module} (optional, needed for full functionality)")
    
    return success

def main():
    """Run all validation tests"""
    print("🧠 DesignMind GenAI LangGraph - Setup Validation")
    print("=" * 55)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Data Directory", test_data_directory),
        ("PDF Detection", test_pdf_detection),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
            all_passed = False
    
    # Summary
    print(f"\n{'='*55}")
    print("📋 Test Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n{'='*55}")
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
        print("🚀 Run: streamlit run main.py")
        print("📄 You have access to 9 sample PDF requirements")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("💡 Try running: python setup_guide.py check")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)