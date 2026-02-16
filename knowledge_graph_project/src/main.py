# -*- coding: utf-8 -*-
"""
知识图谱数据库项目主入口
Knowledge Graph Database Project Entry Point

提供FastAPI应用和命令行接口
"""

import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from platforms.bilibili import BilibiliClient, BilibiliLogin, BilibiliDataExtractor
from platforms.toutiao import ToutiaoClient, ToutiaoLogin, ToutiaoDataExtractor
from auth.cookie_manager import CookieManager, SessionManager
from database.models import (
    ContentType, RelationType, APIResponse, PaginatedResponse,
    User, Content, Comment, Relation, GraphQuery
)


# ==================== FastAPI应用 ====================

app = FastAPI(
    title="知识图谱数据库API",
    description="基于哔哩哔哩和今日头条的知识图谱数据库系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 初始化管理 ====================

cookie_manager = CookieManager()
session_manager = SessionManager()

# 平台客户端缓存
_bilibili_client: Optional[BilibiliClient] = None
_toutiao_client: Optional[ToutiaoClient] = None


def get_bilibili_client() -> BilibiliClient:
    """获取或创建B站客户端"""
    global _bilibili_client
    
    if _bilibili_client is None:
        cookies = cookie_manager.load_cookies('bilibili')
        _bilibili_client = BilibiliClient(cookies=cookies)
    
    return _bilibili_client


def get_toutiao_client() -> ToutiaoClient:
    """获取或创建头条客户端"""
    global _toutiao_client
    
    if _toutiao_client is None:
        cookies = cookie_manager.load_cookies('toutiao')
        _toutiao_client = ToutiaoClient(cookies=cookies)
    
    return _toutiao_client


# ==================== 请求模型 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    platform: str = Field(..., description="平台: bilibili/toutiao")
    method: str = Field(default="auto", description="登录方式: auto/qrcode/password")
    username: Optional[str] = Field(None, description="用户名(密码登录时需要)")
    password: Optional[str] = Field(None, description="密码(密码登录时需要)")


class ContentFilterRequest(BaseModel):
    """内容筛选请求"""
    platform: Optional[str] = None
    content_type: Optional[ContentType] = None
    author_id: Optional[str] = None
    tags: Optional[list[str]] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class GraphSearchRequest(BaseModel):
    """图谱搜索请求"""
    start_user_id: str
    max_depth: int = Field(default=2, ge=1, le=5)
    max_users: int = Field(default=100, ge=1, le=1000)


# ==================== API端点 - 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "知识图谱数据库API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# ==================== API端点 - 登录管理 ====================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """登录平台"""
    try:
        if request.platform == 'bilibili':
            login_manager = BilibiliLogin(headless=False)
            success, cookies = login_manager.auto_login(
                username=request.username,
                password=request.password,
                method=request.method
            )
            login_manager.close()
            
            if success:
                cookie_manager.save_cookies('bilibili', cookies)
                return {
                    "success": True,
                    "message": "B站登录成功",
                    "data": {"cookie_count": len(cookies)}
                }
            else:
                return {
                    "success": False,
                    "message": "B站登录失败"
                }
        
        elif request.platform == 'toutiao':
            login_manager = ToutiaoLogin(headless=False)
            success, cookies = login_manager.auto_login(
                username=request.username,
                password=request.password,
                method=request.method
            )
            login_manager.close()
            
            if success:
                cookie_manager.save_cookies('toutiao', cookies)
                return {
                    "success": True,
                    "message": "头条登录成功",
                    "data": {"cookie_count": len(cookies)}
                }
            else:
                return {
                    "success": False,
                    "message": "头条登录失败"
                }
        
        else:
            raise HTTPException(status_code=400, detail="不支持的平台")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/logout")
async def logout(platform: str = Query(..., description="平台: bilibili/toutiao")):
    """退出登录"""
    try:
        cookie_manager.delete_cookies(platform)
        
        # 重置客户端缓存
        global _bilibili_client, _toutiao_client
        if platform == 'bilibili':
            _bilibili_client = None
        elif platform == 'toutiao':
            _toutiao_client = None
        
        return {
            "success": True,
            "message": f"{platform}已退出登录"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/status")
async def auth_status():
    """查看认证状态"""
    try:
        bilibili_info = cookie_manager.get_cookie_info('bilibili')
        toutiao_info = cookie_manager.get_cookie_info('toutiao')
        
        return {
            "success": True,
            "data": {
                "bilibili": bilibili_info,
                "toutiao": toutiao_info
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== API端点 - B站数据 ====================

@app.get("/api/bilibili/user/{user_id}")
async def get_bilibili_user(user_id: str):
    """获取B站用户信息"""
    try:
        client = get_bilibili_client()
        extractor = BilibiliDataExtractor(client)
        user = extractor.extract_user(user_id)
        
        if user:
            return {"success": True, "data": user}
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bilibili/user/{user_id}/videos")
async def get_bilibili_user_videos(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """获取B站用户视频"""
    try:
        client = get_bilibili_client()
        extractor = BilibiliDataExtractor(client)
        
        videos = []
        page = 1
        while len(videos) < limit:
            data = client.get_user_videos(user_id, page=page, page_size=30)
            if data.get('code') != 0:
                break
            
            video_list = data.get('data', {}).get('list', {}).get('vlist', [])
            if not video_list:
                break
            
            for video in video_list:
                videos.append(extractor._parse_video_info(video))
            
            if len(video_list) < 30:
                break
            page += 1
        
        return {"success": True, "data": videos[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bilibili/video/{bvid}")
async def get_bilibili_video(bvid: str):
    """获取B站视频详情"""
    try:
        client = get_bilibili_client()
        extractor = BilibiliDataExtractor(client)
        video = extractor.extract_video(bvid)
        
        if video:
            return {"success": True, "data": video}
        else:
            raise HTTPException(status_code=404, detail="视频不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bilibili/video/{bvid}/comments")
async def get_bilibili_video_comments(
    bvid: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """获取B站视频评论"""
    try:
        client = get_bilibili_client()
        extractor = BilibiliDataExtractor(client)
        comments = extractor.extract_video_comments(bvid, limit=limit)
        
        return {"success": True, "data": comments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bilibili/popular")
async def get_bilibili_popular(
    limit: int = Query(default=50, ge=1, le=100)
):
    """获取B站热门视频"""
    try:
        client = get_bilibili_client()
        extractor = BilibiliDataExtractor(client)
        videos = extractor.extract_popular_videos(limit=limit)
        
        return {"success": True, "data": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bilibili/search")
async def search_bilibili(
    keyword: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """搜索B站视频"""
    try:
        client = get_bilibili_client()
        extractor = BilibiliDataExtractor(client)
        videos = extractor.search_videos(keyword, limit=limit)
        
        return {"success": True, "data": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== API端点 - 头条数据 ====================

@app.get("/api/toutiao/user/{user_id}")
async def get_toutiao_user(user_id: str):
    """获取头条用户信息"""
    try:
        client = get_toutiao_client()
        extractor = ToutiaoDataExtractor(client)
        user = extractor.extract_user(user_id)
        
        if user:
            return {"success": True, "data": user}
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/toutiao/user/{user_id}/articles")
async def get_toutiao_user_articles(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """获取头条用户文章"""
    try:
        client = get_toutiao_client()
        extractor = ToutiaoDataExtractor(client)
        articles = extractor.extract_user_articles(user_id, limit=limit)
        
        return {"success": True, "data": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/toutiao/article/{group_id}")
async def get_toutiao_article(group_id: str):
    """获取头条文章详情"""
    try:
        client = get_toutiao_client()
        extractor = ToutiaoDataExtractor(client)
        article = extractor.extract_article(group_id)
        
        if article:
            return {"success": True, "data": article}
        else:
            raise HTTPException(status_code=404, detail="文章不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/toutiao/feed")
async def get_toutiao_feed(
    limit: int = Query(default=50, ge=1, le=100),
    category: str = Query(default="all")
):
    """获取头条推荐内容"""
    try:
        client = get_toutiao_client()
        extractor = ToutiaoDataExtractor(client)
        contents = extractor.extract_feed(category=category, limit=limit)
        
        return {"success": True, "data": contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/toutiao/hot")
async def get_toutiao_hot(
    limit: int = Query(default=50, ge=1, le=100)
):
    """获取头条热搜榜"""
    try:
        client = get_toutiao_client()
        extractor = ToutiaoDataExtractor(client)
        hot_list = extractor.extract_hot_search(limit=limit)
        
        return {"success": True, "data": hot_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== API端点 - 图谱查询 ====================

@app.post("/api/graph/crawl/user")
async def crawl_user_network(request: GraphSearchRequest):
    """爬取用户关系网络"""
    try:
        # B站
        bilibili_client = get_bilibili_client()
        bilibili_extractor = BilibiliDataExtractor(bilibili_client)
        bilibili_network = bilibili_extractor.crawl_user_network(
            seed_user_id=request.start_user_id,
            max_users=request.max_users,
            depth=request.max_depth
        )
        
        # 头条
        toutiao_client = get_toutiao_client()
        toutiao_extractor = ToutiaoDataExtractor(toutiao_client)
        toutiao_network = toutiao_extractor.crawl_user_network(
            seed_user_id=request.start_user_id,
            max_users=request.max_users,
            depth=request.max_depth
        )
        
        return {
            "success": True,
            "data": {
                "bilibili": bilibili_network,
                "toutiao": toutiao_network
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 错误处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": str(exc),
            "error_type": type(exc).__name__
        }
    )


# ==================== 启动入口 ====================

def main():
    """主入口"""
    print("=" * 60)
    print("知识图谱数据库API服务")
    print("=" * 60)
    print(f"环境: {settings.app.environment}")
    print(f"调试模式: {settings.app.debug}")
    print(f"服务地址: http://{settings.app.host}:{settings.app.port}")
    print(f"API文档: http://{settings.app.host}:{settings.app.port}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )


if __name__ == "__main__":
    main()
