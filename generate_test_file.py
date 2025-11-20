{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: 生成测试文件",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "args": [
                "--filename", "my_output.txt",
                "--size", "5"
            ],
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}