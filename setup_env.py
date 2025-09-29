#!/usr/bin/env python3
"""
Environment setup script for AI Travel Agent
"""
import os
import sys

def setup_serpapi_key():
    """Setup SerpAPI key"""
    print("=== SerpAPI Setup ===")
    print("To use live flight search, you need a SerpAPI key.")
    print("1. Visit https://serpapi.com/")
    print("2. Sign up for a free account")
    print("3. Get your API key from the dashboard")
    print()
    
    current_key = os.environ.get('SERPAPI_API_KEY')
    if current_key:
        print(f"✓ Current API key found: {current_key[:10]}...")
        choice = input("Do you want to update it? (y/N): ").lower()
        if choice != 'y':
            return
    
    api_key = input("Enter your SerpAPI key: ").strip()
    if not api_key:
        print("No API key provided. Skipping setup.")
        return
    
    # Set environment variable for current session
    os.environ['SERPAPI_API_KEY'] = api_key
    print("✓ API key set for current session")
    
    # Create .env file for persistence
    env_file = '.env'
    env_content = f"SERPAPI_API_KEY={api_key}\n"
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'SERPAPI_API_KEY' in content:
            # Update existing key
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('SERPAPI_API_KEY='):
                    new_lines.append(f"SERPAPI_API_KEY={api_key}")
                else:
                    new_lines.append(line)
            env_content = '\n'.join(new_lines)
        else:
            # Append to existing file
            env_content = content.rstrip() + '\n' + env_content
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✓ API key saved to {env_file}")
    print()
    print("To use the API key in future sessions:")
    print("1. Windows: set SERPAPI_API_KEY=your_key_here")
    print("2. Linux/Mac: export SERPAPI_API_KEY=your_key_here")
    print("3. Or the .env file will be loaded automatically")

def test_setup():
    """Test the current setup"""
    print("\n=== Testing Setup ===")
    
    # Test API key
    api_key = os.environ.get('SERPAPI_API_KEY')
    if api_key:
        print(f"✓ SERPAPI_API_KEY: {api_key[:10]}...")
    else:
        print("✗ SERPAPI_API_KEY not found")
    
    # Test SerpAPI import
    try:
        import serpapi
        print("✓ SerpAPI library available")
    except ImportError:
        print("✗ SerpAPI library not found. Install with: pip install google-search-results")
    
    print("\nSetup complete! You can now run the travel agent.")

def main():
    """Main setup function"""
    print("AI Travel Agent - Environment Setup")
    print("=" * 40)
    
    setup_serpapi_key()
    test_setup()

if __name__ == "__main__":
    main()