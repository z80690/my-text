# -*- coding: utf-8 -*-
"""分布式锁 - 自动启用"""

import time
import uuid
from typing import Optional

class DistributedLock:
    """分布式锁实现"""
    
    def __init__(self):
        self.locks = {}  # key -> (owner_id, expire_time)
    
    def acquire(self, key: str, timeout: int = 30, owner_id: Optional[str] = None) -> bool:
        """获取锁"""
        owner = owner_id or str(uuid.uuid4())
        expire_time = time.time() + timeout
        
        current = self.locks.get(key)
        
        if current is None:
            # 锁不存在，直接获取
            self.locks[key] = (owner, expire_time)
            return True
        
        # 检查锁是否过期
        if time.time() > current[1]:
            # 锁已过期，获取锁
            self.locks[key] = (owner, expire_time)
            return True
        
        # 锁被其他持有者持有
        return False
    
    def release(self, key: str, owner_id: Optional[str] = None):
        """释放锁"""
        current = self.locks.get(key)
        
        if current is None:
            return
        
        # 如果没有指定owner_id或者owner_id匹配，则释放锁
        if owner_id is None or current[0] == owner_id:
            del self.locks[key]
    
    def is_locked(self, key: str) -> bool:
        """检查锁是否被持有"""
        current = self.locks.get(key)
        
        if current is None:
            return False
        
        # 检查锁是否过期
        if time.time() > current[1]:
            return False
        
        return True