#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为所有 Python 文件添加 UTF-8 编码声明"""

import os
import glob

def add_encoding_declaration(directory, file_pattern='*.py'):
    """为指定目录中的 Python 文件添加编码声明"""
    count = 0
    for filepath in glob.glob(os.path.join(directory, file_pattern)):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有编码声明
        first_lines = content.split('\n')[:3]
        has_encoding = any(
            'coding:' in line or 'coding=' in line 
            for line in first_lines
        )
        
        if not has_encoding:
            # 读取原始字节以保留格式
            with open(filepath, 'rb') as f:
                raw_content = f.read()
            
            # 检测原始换行符
            if b'\r\n' in raw_content:
                eol = b'\r\n'
            else:
                eol = b'\n'
            
            # 添加编码声明
            if raw_content.startswith(b'#!'):
                # 有 shebang，在第二行添加
                first_newline = raw_content.find(eol)
                if first_newline != -1:
                    header = raw_content[:first_newline + len(eol)]
                    rest = raw_content[first_newline + len(eol):]
                    new_content = header + b'# -*- coding: utf-8 -*-' + eol + rest
                else:
                    new_content = b'# -*- coding: utf-8 -*-' + eol + raw_content
            else:
                # 直接添加
                new_content = b'# -*- coding: utf-8 -*-' + eol + raw_content
            
            with open(filepath, 'wb') as f:
                f.write(new_content)
            
            print(f'已修复: {os.path.basename(filepath)}')
            count += 1
        else:
            print(f'已存在编码声明: {os.path.basename(filepath)}')
    
    print(f'\n共修复 {count} 个文件')
    return count

if __name__ == '__main__':
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else 'src'
    add_encoding_declaration(directory)
