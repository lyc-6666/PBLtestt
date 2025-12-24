# 个人中心功能说明

## 功能概述

为电影推荐系统添加了完整的个人中心功能，让用户可以管理个人信息、查看评分历史和评论记录。

## 主要功能

### 1. 个人信息管理
- **查看个人信息**：显示用户名、邮箱、注册时间等基本信息
- **编辑邮箱地址**：用户可以更新自己的邮箱
- **修改密码**：支持密码修改功能，需要输入新密码和确认密码

### 2. 我的评分
- **评分记录列表**：显示用户对所有电影的评分，包括：
  - 电影海报、标题、导演、年份
  - 评分星级显示
  - 评分时间
- **评分统计信息**：
  - 已评分电影总数
  - 平均评分
  - 最高评分电影
- **删除评分**：用户可以删除自己的评分记录

### 3. 我的评论
- **评论历史**：显示用户发表的所有评论
- **评论详情**：包括评论内容、对应电影、评分和时间
- **快速访问**：可以点击电影标题快速跳转到电影详情页

## 技术实现

### 后端路由
- `/profile` - 个人中心主页
- `/update_profile` - 更新个人信息（POST）
- `/delete_rating/<rating_id>` - 删除评分记录

### 数据库查询
```sql
-- 获取用户评分记录（包含电影信息）
SELECT r.*, m.title, m.year, m.director, m.image_url 
FROM ratings r 
JOIN movies m ON r.movie_id = m.id 
WHERE r.user_id = ? 
ORDER BY r.created_at DESC

-- 获取用户评论记录
SELECT r.*, m.title 
FROM ratings r 
JOIN movies m ON r.movie_id = m.id 
WHERE r.user_id = ? AND r.review IS NOT NULL AND r.review != ''
ORDER BY r.created_at DESC
```

### 前端特性
- 响应式设计，适配移动端
- 使用Bootstrap 5和Font Awesome图标
- 标签页切换界面
- 实时表单验证
- 确认对话框（删除操作）

## 安全特性

1. **权限验证**：所有个人中心功能都需要登录才能访问
2. **数据隔离**：用户只能查看和操作自己的数据
3. **密码加密**：使用bcrypt进行密码加密存储
4. **输入验证**：对邮箱格式、密码长度等进行验证
5. **SQL注入防护**：使用参数化查询

## 使用方法

1. 启动应用：`python app.py`
2. 登录账户
3. 点击右上角用户名下拉菜单
4. 选择"个人中心"
5. 在不同标签页中查看和管理个人信息

## 测试

项目包含完整的测试脚本：
- `test_profile_feature.py` - 功能测试脚本
- `demo_profile_data.py` - 测试数据生成脚本

运行测试：
```bash
python test_profile_feature.py
python demo_profile_data.py
```

## 文件结构

```
templates/
├── profile.html          # 个人中心页面模板
├── base.html             # 更新了导航栏链接

app.py                    # 添加了个人中心相关路由

test_profile_feature.py    # 功能测试脚本
demo_profile_data.py      # 测试数据脚本
PROFILE_FEATURE.md        # 本说明文档
```

## 扩展可能

未来可以考虑添加的功能：
1. 头像上传功能
2. 收藏电影功能
3. 观影历史记录
4. 个人评分统计图表
5. 好友系统和社交功能
6. 推荐偏好设置