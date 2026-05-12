# -*- coding: utf-8 -*-
"""
知识图谱 MCP 服务 - stdio 协议
基于知识图谱的持久记忆系统
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.load_from_file()
    
    def load_from_file(self):
        """从文件加载知识图谱"""
        try:
            db_path = os.environ.get('MEMORY_FILE_PATH', 'knowledge_graph.db')
            if os.path.exists(db_path):
                with open(db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.nodes = data.get('nodes', {})
                    self.edges = data.get('edges', [])
        except:
            self.nodes = {}
            self.edges = []
    
    def save_to_file(self):
        """保存知识图谱到文件"""
        db_path = os.environ.get('MEMORY_FILE_PATH', 'knowledge_graph.db')
        data = {
            "nodes": self.nodes,
            "edges": self.edges,
            "updated_at": datetime.now().isoformat()
        }
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_node(self, node_id, node_type, properties=None):
        """添加节点"""
        self.nodes[node_id] = {
            "type": node_type,
            "properties": properties or {},
            "created_at": datetime.now().isoformat()
        }
        self.save_to_file()
        return {"status": "success", "node_id": node_id}
    
    def add_edge(self, source, target, relation):
        """添加边"""
        edge = {
            "source": source,
            "target": target,
            "relation": relation,
            "created_at": datetime.now().isoformat()
        }
        self.edges.append(edge)
        self.save_to_file()
        return {"status": "success"}
    
    def query(self, query_type, params=None):
        """查询知识图谱"""
        params = params or {}
        
        if query_type == 'get_node':
            node_id = params.get('node_id')
            if node_id in self.nodes:
                return {"status": "success", "data": self.nodes[node_id]}
            return {"status": "error", "message": "Node not found"}
        
        elif query_type == 'search':
            keyword = params.get('keyword', '').lower()
            results = []
            for node_id, node in self.nodes.items():
                props = node.get('properties', {})
                text = str(node_id) + ' ' + str(props.get('name', '')) + ' ' + str(props.get('description', ''))
                if keyword in text.lower():
                    results.append({"node_id": node_id, **node})
            return {"status": "success", "data": results}
        
        elif query_type == 'get_related':
            node_id = params.get('node_id')
            related = []
            for edge in self.edges:
                if edge['source'] == node_id:
                    related.append({"relation": edge['relation'], "target": edge['target']})
                elif edge['target'] == node_id:
                    related.append({"relation": edge['relation'], "source": edge['source']})
            return {"status": "success", "data": related}
        
        return {"status": "error", "message": "Unknown query type"}

def main():
    """MCP stdio 协议主循环"""
    kg = KnowledgeGraph()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                response = json.dumps({"error": "Invalid JSON"})
                print(response)
                sys.stdout.flush()
                continue
            
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'add_node':
                result = kg.add_node(
                    params.get('node_id'),
                    params.get('node_type'),
                    params.get('properties')
                )
            elif method == 'add_edge':
                result = kg.add_edge(
                    params.get('source'),
                    params.get('target'),
                    params.get('relation')
                )
            elif method == 'query':
                result = kg.query(
                    params.get('query_type'),
                    params.get('query_params')
                )
            elif method == 'get_status':
                result = {
                    "status": "running",
                    "version": "1.0",
                    "nodes_count": len(kg.nodes),
                    "edges_count": len(kg.edges)
                }
            else:
                result = {"error": f"Unknown method: {method}"}
            
            response = json.dumps({"result": result})
            print(response)
            sys.stdout.flush()
            
        except Exception as e:
            response = json.dumps({"error": str(e)})
            print(response)
            sys.stdout.flush()

if __name__ == '__main__':
    main()
