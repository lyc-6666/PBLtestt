#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人中心功能演示 - 添加测试数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import execute_db_query, bcrypt
import random

def add_test_ratings():
    """为admin用户添加一些测试评分和评论"""
    print("=== 添加个人中心测试数据 ===")
    
    # 获取admin用户信息
    admin_user = execute_db_query("SELECT * FROM users WHERE username = 'admin'", fetch_one=True)
    if not admin_user:
        print("admin用户不存在，请先运行app.py初始化数据库")
        return
    
    user_id = admin_user['id']
    print(f"为用户 {admin_user['username']} (ID: {user_id}) 添加测试数据...")
    
    # 获取所有电影
    movies = execute_db_query("SELECT * FROM movies", fetch_all=True)
    if not movies:
        print("没有找到电影数据")
        return
    
    # 为每个电影添加评分和评论
    sample_reviews = [
        "这部电影的剧情非常精彩，演员的表演也很到位，值得推荐！",
        "视觉效果令人震撼，故事情节紧凑，是一部优秀的作品。",
        "虽然有些情节略显拖沓，但总体来说还是不错的观影体验。",
        "导演的拍摄手法独特，配乐也很棒，给人留下了深刻印象。",
        "剧情发展合理，角色塑造丰满，是一部值得一看的好电影。",
    ]
    
    added_count = 0
    for movie in movies:
        # 检查是否已经评分过
        existing_rating = execute_db_query(
            "SELECT * FROM ratings WHERE user_id = ? AND movie_id = ?",
            (user_id, movie['id']),
            fetch_one=True
        )
        
        if not existing_rating:
            # 随机生成评分（4-5分，偏向高分）
            rating = random.choice([4, 4, 5, 5, 5])
            review = random.choice(sample_reviews) if random.random() > 0.3 else ""
            
            # 添加评分
            result = execute_db_query(
                "INSERT INTO ratings (user_id, movie_id, rating, review) VALUES (?, ?, ?, ?)",
                (user_id, movie['id'], rating, review),
                commit=True
            )
            
            if result:
                print(f"  ✓ 为《{movie['title']}》评分: {rating}/5")
                if review:
                    print(f"    评论: {review[:30]}...")
                added_count += 1
    
    # 更新电影的平均评分
    for movie in movies:
        execute_db_query(
            "UPDATE movies SET rating = (SELECT AVG(rating) FROM ratings WHERE movie_id = ?) WHERE id = ?",
            (movie['id'], movie['id']),
            commit=True
        )
    
    print(f"\n成功添加 {added_count} 条评分记录")
    print("现在可以登录admin账户查看个人中心的完整功能了！")

def show_profile_statistics():
    """显示个人中心统计数据"""
    print("\n=== 个人中心统计数据 ===")
    
    # 获取admin用户
    admin_user = execute_db_query("SELECT * FROM users WHERE username = 'admin'", fetch_one=True)
    if not admin_user:
        return
    
    user_id = admin_user['id']
    
    # 获取评分统计
    ratings = execute_db_query(
        '''SELECT r.*, m.title 
           FROM ratings r 
           JOIN movies m ON r.movie_id = m.id 
           WHERE r.user_id = ? 
           ORDER BY r.created_at DESC''',
        (user_id,),
        fetch_all=True
    )
    
    if ratings:
        avg_rating = sum(r['rating'] for r in ratings) / len(ratings)
        highest_rating = max(ratings, key=lambda x: x['rating'])
        lowest_rating = min(ratings, key=lambda x: x['rating'])
        
        print(f"总评分数量: {len(ratings)}")
        print(f"平均评分: {avg_rating:.2f}")
        print(f"最高评分电影: 《{highest_rating['title']}》({highest_rating['rating']}/5)")
        print(f"最低评分电影: 《{lowest_rating['title']}》({lowest_rating['rating']}/5)")
        
        # 显示评分分布
        rating_dist = {}
        for r in ratings:
            rating_dist[r['rating']] = rating_dist.get(r['rating'], 0) + 1
        
        print("\n评分分布:")
        for rating in sorted(rating_dist.keys(), reverse=True):
            bar = '█' * rating_dist[rating]
            print(f"  {rating}分: {rating_dist[rating]}部 {bar}")
    else:
        print("暂无评分记录")

if __name__ == '__main__':
    try:
        add_test_ratings()
        show_profile_statistics()
        
        print("\n=== 使用说明 ===")
        print("1. 启动应用: python app.py")
        print("2. 使用admin账户登录 (用户名: admin, 密码: admin123)")
        print("3. 点击右上角用户名，选择'个人中心'")
        print("4. 在个人中心可以：")
        print("   - 查看和编辑个人信息")
        print("   - 查看所有评分记录")
        print("   - 查看评论历史")
        print("   - 删除评分记录")
        print("   - 查看评分统计信息")
        
    except Exception as e:
        print(f"添加测试数据时出现错误: {e}")
        import traceback
        traceback.print_exc()