import random
import csv
import json
import threading
import time
from datetime import datetime

# 全局变量用于存储中间结果
workflow_results = {}
lock = threading.Lock()

def log(message):
    """日志函数，带时间戳"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def step1_generate_csv():
    """Step 1: 生成包含随机数的CSV文件"""
    log("Step 1 [顺序流] 开始：生成随机数CSV文件")
    
    # 生成100个随机数（1-10范围）
    data = [random.randint(1, 10) for _ in range(100)]
    
    # 写入CSV文件
    with open('data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['value'])
        for num in data:
            writer.writerow([num])
    
    log(f"Step 1 [顺序流] 完成：生成了100个随机数，范围1-10")
    return data

def step2a_calculate_average(data):
    """Step 2A: 计算平均值"""
    log("Step 2A [并行] 开始：计算平均值")
    time.sleep(1)  # 模拟计算耗时
    
    avg = sum(data) / len(data)
    
    with lock:
        workflow_results['average'] = avg
    
    log(f"Step 2A [并行] 完成：平均值 = {avg:.2f}")
    return avg

def step2b_find_extremes(data):
    """Step 2B: 找出极值"""
    log("Step 2B [并行] 开始：查找极值")
    time.sleep(1.5)  # 模拟计算耗时（比A稍长）
    
    min_val = min(data)
    max_val = max(data)
    
    with lock:
        workflow_results['extremes'] = {'min': min_val, 'max': max_val}
    
    log(f"Step 2B [并行] 完成：最小值 = {min_val}, 最大值 = {max_val}")
    return {'min': min_val, 'max': max_val}

def step3_merge_results():
    """Step 3: 合并结果成JSON报告"""
    log("Step 3 [合并流] 开始：等待Step 2A和2B完成...")
    
    # 等待两个并行任务完成
    while 'average' not in workflow_results or 'extremes' not in workflow_results:
        time.sleep(0.1)
    
    report = {
        'summary': {
            'data_points': 100,
            'data_range': '1-10'
        },
        'statistics': {
            'average': workflow_results['average'],
            'min': workflow_results['extremes']['min'],
            'max': workflow_results['extremes']['max'],
            'range': workflow_results['extremes']['max'] - workflow_results['extremes']['min']
        },
        'generated_at': datetime.now().isoformat()
    }
    
    # 写入JSON文件
    with open('report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    log("Step 3 [合并流] 完成：生成JSON报告")
    return report

def step4_condition_check(report):
    """Step 4: 条件分支判断"""
    log("Step 4 [条件分支] 开始：检查平均值")
    
    avg = report['statistics']['average']
    if avg > 5:
        conclusion = "数据偏高"
    else:
        conclusion = "数据正常"
    
    report['conclusion'] = conclusion
    log(f"Step 4 [条件分支] 完成：平均值={avg:.2f}，结论：{conclusion}")
    
    return conclusion

def run_workflow():
    """执行完整工作流"""
    log("=" * 60)
    log("开始执行多步骤工作流：数据分析流程")
    log("=" * 60)
    
    # Step 1: 顺序流 - 生成CSV
    data = step1_generate_csv()
    
    # Step 2: 并行网关 - 同时执行A和B
    log("\nStep 2 [并行网关] 开始：启动两个并行任务")
    thread_a = threading.Thread(target=step2a_calculate_average, args=(data,))
    thread_b = threading.Thread(target=step2b_find_extremes, args=(data,))
    
    thread_a.start()
    thread_b.start()
    
    # 等待两个线程完成
    thread_a.join()
    thread_b.join()
    log("Step 2 [并行网关] 完成：两个任务均已结束")
    
    # Step 3: 合并流 - 生成报告
    log("\n" + "=" * 60)
    report = step3_merge_results()
    
    # Step 4: 条件分支 - 判断结果
    log("\n" + "=" * 60)
    conclusion = step4_condition_check(report)
    
    # 输出最终报告
    log("\n" + "=" * 60)
    log("工作流执行完成！")
    log("=" * 60)
    log("\n📊 最终JSON报告：")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    log(f"\n🎯 最终结论：{conclusion}")
    
    return report, conclusion

if __name__ == "__main__":
    run_workflow()