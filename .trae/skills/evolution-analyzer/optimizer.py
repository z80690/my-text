# -*- coding: utf-8 -*-
"""
自动优化器 - 根据调研和缺陷分析结果自动净化
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class AutoOptimizer:
    """
    自动优化器
    功能：
    1. 根据调研结果生成优化提案
    2. 根据缺陷报告执行自动修复
    3. 生成优化报告
    """
    
    def __init__(self):
        self.optimizations = []
        self.reports_dir = Path(__file__).parent.parent / "memories" / "project" / "evolution_proposals"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_proposal(
        self,
        research_summary: Dict[str, Any],
        comparison_report: Dict[str, Any],
        defect_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成优化提案
        """
        proposal = {
            "proposal_id": f"PROPOSAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "status": "pending",
            "research_summary": research_summary,
            "comparison_report": comparison_report,
            "defect_report": defect_report,
            "recommendations": [],
            "action_items": []
        }
        
        # 基于调研结果生成建议
        if "best_practices" in research_summary:
            for practice in research_summary["best_practices"]:
                proposal["recommendations"].append({
                    "type": "best_practice",
                    "priority": "high",
                    "description": f"采纳最佳实践：{practice}",
                    "source": research_summary.get("sources", [])
                })
        
        # 基于对比结果生成建议
        if comparison_report.get("systems"):
            best = comparison_report["best_system"]
            worst = comparison_report.get("worst_system")
            
            if best and worst:
                score_diff = best["total_score"] - worst["total_score"]
                if score_diff > 10:
                    proposal["recommendations"].append({
                        "type": "architecture_upgrade",
                        "priority": "critical",
                        "description": f"架构升级建议：{best['system_name']} 比 {worst['system_name']} 高 {score_diff:.1f} 分",
                        "details": best
                    })
        
        # 基于缺陷报告生成行动项
        critical_defects = defect_report.get("critical_defects", [])
        if critical_defects:
            for defect in critical_defects:
                proposal["action_items"].append({
                    "type": "fix_critical",
                    "priority": "critical",
                    "description": f"修复严重缺陷：{defect.description}",
                    "suggestion": defect.suggestion,
                    "module": defect.module
                })
        
        high_defects = defect_report.get("high_defects", [])
        if high_defects:
            for defect in high_defects:
                proposal["action_items"].append({
                    "type": "fix_high",
                    "priority": "high",
                    "description": f"修复高级缺陷：{defect.description}",
                    "suggestion": defect.suggestion,
                    "module": defect.module
                })
        
        return proposal
    
    def save_proposal(self, proposal: Dict[str, Any], status: str = "pending"):
        """
        保存提案到文件
        """
        proposal["status"] = status
        filename = f"{proposal['proposal_id']}.json"
        filepath = self.reports_dir / status / filename
        
        # 确保目录存在
        (self.reports_dir / status).mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(proposal, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def execute_auto_fix(self, defect: Any) -> bool:
        """
        执行自动修复
        Args:
            defect: 缺陷对象
        Returns:
            是否修复成功
        """
        # 这里实现具体的自动修复逻辑
        # 例如：添加缺失的文档字符串、创建缺失的文件等
        
        if defect.defect_type == "missing_init":
            init_path = Path(defect.module) / "__init__.py"
            if not init_path.exists():
                init_path.write_text("# -*- coding: utf-8 -*-\n", encoding='utf-8')
                return True
        
        # 其他类型的缺陷需要手动修复
        return False
    
    def generate_optimization_report(self, proposal: Dict[str, Any]) -> str:
        """
        生成优化报告（Markdown 格式）
        """
        report = f"""# 自主进化优化报告

**提案 ID**: {proposal['proposal_id']}
**生成时间**: {proposal['generated_at']}
**状态**: {proposal['status']}

## 📊 调研总结

- 信源数量：{proposal['research_summary'].get('total_sources', 0)}
- 高可信度信源：{proposal['research_summary'].get('high_credibility_count', 0)}

## 📈 对比分析

"""
        if proposal["comparison_report"].get("systems"):
            best = proposal["comparison_report"]["best_system"]
            worst = proposal["comparison_report"].get("worst_system")
            
            if best:
                report += f"**最佳系统**: {best['system_name']} ({best['total_score']:.1f}分)\n"
            if worst:
                report += f"**需改进系统**: {worst['system_name']} ({worst['total_score']:.1f}分)\n"
        
        report += f"""
## 🐛 缺陷检测

- 总缺陷数：{proposal['defect_report']['total_defects']}
- 严重缺陷：{len(proposal['defect_report']['critical_defects'])}
- 高级缺陷：{len(proposal['defect_report']['high_defects'])}

## 💡 优化建议

"""
        for i, rec in enumerate(proposal["recommendations"], 1):
            report += f"{i}. **[{rec['priority']}]** {rec['description']}\n"
        
        report += f"""
## 🔧 行动项

"""
        for i, item in enumerate(proposal["action_items"], 1):
            report += f"{i}. **[{item['priority']}]** {item['description']}\n"
            report += f"   - 建议：{item['suggestion']}\n"
            report += f"   - 模块：{item['module']}\n\n"
        
        return report
    
    def export_report(self, proposal: Dict[str, Any], output_path: str):
        """
        导出优化报告
        """
        report_md = self.generate_optimization_report(proposal)
        Path(output_path).write_text(report_md, encoding='utf-8')
