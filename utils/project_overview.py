#!/usr/bin/env python3
"""
Project Overview Utility
Shows the current project structure and file organization.
"""

import os
import sys

# Add the parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)


def show_project_structure():
    """Display the project structure and file organization."""
    print("=" * 60)
    print("ROBOT ACTION PLANNER - PROJECT OVERVIEW")
    print("=" * 60)
    
    project_root = parent_dir
    print(f"Project Root: {project_root}")
    
    # Core files in root
    print("\n📁 Core Application Files:")
    core_files = [
        "main.py",
        "constant.py", 
        "action_compiler.py",
        "spreadsheet_loader.py",
        "cache_manager.py"
    ]
    
    for file in core_files:
        file_path = os.path.join(project_root, file)
        if os.path.exists(file_path):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
    
    # Documentation
    print("\n📖 Documentation:")
    docs_dir = os.path.join(project_root, "docs")
    if os.path.exists(docs_dir):
        for file in os.listdir(docs_dir):
            if file.endswith('.md'):
                print(f"  ✓ docs/{file}")
    else:
        print("  ✗ docs/ directory not found")
    
    # Utilities
    print("\n🛠️ Utilities:")
    utils_dir = os.path.join(project_root, "utils")
    if os.path.exists(utils_dir):
        for file in os.listdir(utils_dir):
            if file.endswith('.py'):
                print(f"  ✓ utils/{file}")
    else:
        print("  ✗ utils/ directory not found")
    
    # Module directories
    print("\n📦 Module Directories:")
    module_dirs = [
        "actions",
        "config", 
        "driver",
        "execution",
        "media",
        "robots"
    ]
    
    for module in module_dirs:
        module_path = os.path.join(project_root, module)
        if os.path.exists(module_path):
            print(f"  ✓ {module}/")
        else:
            print(f"  ✗ {module}/ (missing)")
    
    # Cache directory
    cache_dir = os.path.join(project_root, "cache")
    if os.path.exists(cache_dir):
        cache_files = len([f for f in os.listdir(cache_dir) if f.endswith('.json')])
        print(f"\n💾 Cache Directory: cache/ ({cache_files} cache files)")
    else:
        print(f"\n💾 Cache Directory: cache/ (not created yet)")
    
    # Logs directory
    logs_dir = os.path.join(project_root, "logs")
    if os.path.exists(logs_dir):
        log_files = len([f for f in os.listdir(logs_dir) if f.endswith('.log')])
        print(f"📝 Logs Directory: logs/ ({log_files} log files)")
    else:
        print(f"📝 Logs Directory: logs/ (not created yet)")


def show_file_organization_benefits():
    """Show the benefits of the current file organization."""
    print("\n" + "=" * 60)
    print("FILE ORGANIZATION BENEFITS")
    print("=" * 60)
    
    print("\n✅ Benefits of Current Organization:")
    print("  • Cleaner root directory with only core application files")
    print("  • Documentation centralized in docs/ directory")
    print("  • Utilities and tools organized in utils/ directory")
    print("  • Clear separation between application code and support files")
    print("  • Easier navigation and maintenance")
    print("  • Better version control organization")
    
    print("\n📁 Directory Purpose:")
    print("  • root/          - Core application files and main entry point")
    print("  • docs/          - All documentation and guides")
    print("  • utils/         - Development and maintenance tools")
    print("  • actions/       - Robot action implementations") 
    print("  • config/        - Configuration management")
    print("  • driver/        - Robot communication drivers")
    print("  • execution/     - Action execution engine")
    print("  • media/         - Media playback management")
    print("  • robots/        - Robot factory and management")
    print("  • cache/         - File-based cache storage")
    print("  • logs/          - Application log files")


def show_quick_commands():
    """Show quick commands for common tasks."""
    print("\n" + "=" * 60)
    print("QUICK REFERENCE COMMANDS")
    print("=" * 60)
    
    print("\n🚀 Application:")
    print("  python main.py                    # Run the main application")
    
    print("\n🛠️ Cache Management:")
    print("  python utils/cache_utils.py info  # Show cache information")
    print("  python utils/cache_utils.py clear # Clear all cache")
    print("  python utils/cache_utils.py test  # Test cache performance")
    
    print("\n📊 Testing:")
    print("  python utils/test_caching.py      # Test caching performance")
    print("  python utils/project_overview.py  # Show this overview")
    
    print("\n📖 Documentation:")
    print("  docs/CACHING_OPTIMIZATION.md      # Complete caching guide")
    print("  docs/CACHE_QUICK_START.md         # Quick start for caching")
    print("  README.md                         # Main project documentation")


def main():
    """Main entry point."""
    show_project_structure()
    show_file_organization_benefits()
    show_quick_commands()
    
    print("\n" + "=" * 60)
    print("PROJECT OVERVIEW COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
