#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""转换 Python 文件的换行符从 CRLF 到 LF"""

import os
import glob

def convert_crlf_to_lf(directory, file_pattern='*.py'):
    """将指定目录中的文件从 CRLF 转换为 LF"""
    count = 0
    for filepath in glob.glob(os.path.join(directory, file_pattern)):
        with open(filepath, 'rb') as f:
            content = f.read()

        # 检测是否为 CRLF
        if b'\r\n' in content:
            # 转换为 LF
            content = content.replace(b'\r\n', b'\n')
            with open(filepath, 'wb') as f:
                f.write(content)
            print(f'转换: {os.path.basename(filepath)}')
            count += 1
        else:
            print(f'跳过 (已是 LF): {os.path.basename(filepath)}')

    print(f'\n共转换 {count} 个文件')
    return count

if __name__ == '__main__':
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else 'src'
    convert_crlf_to_lf(directory)
