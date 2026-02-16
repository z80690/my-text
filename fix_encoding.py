#!/usr/bin/env python3
"""Fix Python file encoding issues"""

import os
import glob

def detect_and_fix_encoding(filepath):
    """Detect file encoding and fix"""
    # Read raw bytes first
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    # Detect line ending
    if b'\r\n' in raw:
        eol = b'\r\n'
    else:
        eol = b'\n'
    
    # Remove BOM if present
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    
    # Try multiple encodings
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1', 'cp1252']
    content = None
    used_encoding = None
    
    for enc in encodings:
        try:
            content = raw.decode(enc)
            used_encoding = enc
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        content = raw.decode('utf-8', errors='replace')
        used_encoding = 'utf-8 with replacements'
    
    # Clean special characters (Chinese punctuation incorrectly converted)
    replacements = {
        '\uff0c': ',',
        '\uff01': '!',
        '\uff1a': ':',
        '\uff1b': ';',
        '\uff1f': '?',
        '\uff08': '(',
        '\uff09': ')',
        '\uff5b': '[',
        '\uff5d': ']',
        '\u3000': ' ',
        '\u3001': ',',
        '\u3002': '.',
        '\u3010': '[',
        '\u3011': ']',
    }
    
    original = content
    for bad, good in replacements.items():
        content = content.replace(bad, good)
    
    # Remove duplicate blank lines
    lines = content.split('\n')
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        is_empty = line.strip() == ''
        if is_empty and prev_empty:
            continue
        cleaned_lines.append(line)
        prev_empty = is_empty
    content = '\n'.join(cleaned_lines)
    
    # Fix lines with extra newlines
    fixed_lines = []
    for line in cleaned_lines:
        stripped = line.rstrip()
        if '\n' in line:
            for subline in line.split('\n'):
                if subline.strip():
                    fixed_lines.append(subline.rstrip())
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Add encoding declaration (if not exists)
    first_lines = content.split('\n')[:3]
    has_encoding = any('coding:' in line or 'coding=' in line for line in first_lines)
    
    if not has_encoding:
        if content.startswith('#!'):
            first_newline = content.find('\n')
            if first_newline != -1:
                header = content[:first_newline + 1]
                rest = content[first_newline + 1:]
                content = header + '# -*- coding: utf-8 -*-\n' + rest
            else:
                content = '# -*- coding: utf-8 -*-\n' + content
        else:
            content = '# -*- coding: utf-8 -*-\n' + content
    
    # Write back file (using LF)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    changed = content != original
    return used_encoding, changed

def process_directory(directory):
    """Process all Python files in directory"""
    files = [f for f in os.listdir(directory) if f.endswith('.py')]
    print(f'Processing {len(files)} Python files...\n')
    
    fixed_count = 0
    for filename in files:
        filepath = os.path.join(directory, filename)
        try:
            encoding, changed = detect_and_fix_encoding(filepath)
            if changed:
                print(f'[FIXED] {filename} (encoding: {encoding})')
                fixed_count += 1
            else:
                print(f'[SKIP]  {filename} (no changes)')
        except Exception as e:
            print(f'[ERROR] {filename} - {e}')
    
    print(f'\nDone! Fixed {fixed_count} files.')

if __name__ == '__main__':
    process_directory('src')
