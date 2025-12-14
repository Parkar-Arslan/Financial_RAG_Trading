"""Setup script to prepare the environment"""

import os
import subprocess
import sys

def main():
    print("="*50)
    print("Financial RAG Assistant - Setup Script")
    print("="*50)
    
    # Step 1: Create directories
    print("\n📁 Creating directories...")
    directories = [
        "data/raw",
        "data/processed", 
        "data/sample",
        "chroma_db",
        "logs"
    ]
    
    for dir in directories:
        os.makedirs(dir, exist_ok=True)
        print(f"  ✓ Created {dir}")
    
    # Step 2: Install requirements
    print("\n📦 Installing requirements...")
    print("  This may take a few minutes...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Step 3: Create .env file
    print("\n🔧 Setting up environment...")
    if not os.path.exists(".env"):
        with open(".env.example", "r") as example:
            with open(".env", "w") as env:
                env.write(example.read())
        print("  ✓ Created .env file")
        print("  ⚠️  Please edit .env and add your Groq API key")
        print("     Get one free at: https://console.groq.com/keys")
    else:
        print("  ✓ .env file already exists")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Groq API key")
    print("2. Run: python load_data.py")
    print("3. Run: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()