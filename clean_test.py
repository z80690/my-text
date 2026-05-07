import sys
sys.path.insert(0, '.trae/skills/file-cleaner')

from file_cleaner import auto_clean

print("Starting auto-clean...")
result = auto_clean(".")
print("\nCleanup Result:")
print(result)