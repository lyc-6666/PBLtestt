# 电影推荐系统

一个基于 Flask + SQLite 的完整电影推荐网站，包含用户端和管理员端功能。

## 🎬 系统功能

### 用户端功能
- ✅ 用户注册/登录
- ✅ 电影浏览和搜索
- ✅ 按分类查看电影
- ✅ 电影详情查看
- ✅ 评分和评论功能
- ✅ 响应式设计，支持移动端

### 管理员端功能
- ✅ 管理员登录
- ✅ 电影管理（添加、删除）
- ✅ 用户管理
- ✅ 系统统计信息
- ✅ 本地图片上传功能

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip 包管理工具

### 安装步骤

1. **克隆或下载项目**
   ```bash
   # 如果是git仓库
   git clone <repository-url>
   cd PBLtest
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行系统**
   ```bash
   # 方式1：使用启动脚本（推荐）
   python run.py
   
   # 方式2：直接运行应用
   python app.py
   ```

4. **访问系统**
   - 打开浏览器访问：`http://127.0.0.1:5000`
   - 管理员账号：`admin` / `admin123`
   - 普通用户：注册新账号

## 📁 项目结构

```
PBLtest/
├── app.py                 # 主应用文件
├── run.py                # 启动脚本
├── requirements.txt      # 依赖包列表
├── movie_system.db      # SQLite数据库文件
├── uploads/             # 图片上传目录
│   └── .gitkeep
└── templates/           # HTML模板文件
    ├── base.html        # 基础模板
    ├── index.html       # 首页
    ├── login.html       # 登录页面
    ├── register.html    # 注册页面
    ├── movie_detail.html # 电影详情页
    ├── category.html    # 分类页面
    ├── search.html      # 搜索页面
    ├── admin_panel.html # 管理员面板
    └── admin_add_movie.html # 添加电影页面
```

## 🔧 技术栈

### 后端技术
- **Flask**: Python轻量级Web框架
- **SQLite**: 嵌入式数据库
- **bcrypt**: 密码加密
- **Werkzeug**: 文件上传处理

### 前端技术
- **Bootstrap 5**: 响应式UI框架
- **Font Awesome**: 图标库
- **JavaScript**: 交互功能
- **HTML5/CSS3**: 现代网页标准

### 安全特性
- 密码加密存储
- SQL注入防护
- 文件上传安全检查
- 会话管理

## 🎯 核心功能详解

### 1. 用户认证系统
- 用户注册（用户名、密码、邮箱）
- 用户登录（支持普通用户和管理员）
- 密码加密存储（bcrypt）
- 会话管理

### 2. 电影管理系统
- 电影信息存储（标题、导演、年份、类型、简介）
- 电影海报支持（URL链接 + 本地上传）
- 电影分类管理
- 电影搜索功能（标题、导演、类型、简介）

### 3. 评分评论系统
- 1-5星评分系统
- 用户评论功能
- 平均评分计算
- 个人评分记录

### 4. 管理员功能
- 电影CRUD操作
- 用户管理
- 系统统计
- 批量操作

## 🔒 安全措施

1. **密码安全**
   - 使用bcrypt加密密码
   - 密码强度验证
   - 防止暴力破解

2. **数据验证**
   - 表单数据验证
   - SQL注入防护
   - XSS攻击防护

3. **文件上传安全**
   - 文件类型限制
   - 文件大小限制（5MB）
   - 文件名安全处理

## 📊 数据库设计

### 主要数据表

1. **users** - 用户表
   - id, username, password, email, role, created_at

2. **movies** - 电影表
   - id, title, director, year, genre, description, image_url, rating, created_at

3. **categories** - 分类表
   - id, name

4. **movie_categories** - 电影分类关联表
   - id, movie_id, category_id

5. **ratings** - 评分表
   - id, user_id, movie_id, rating, review, created_at

## 🛠️ 开发说明

### 自定义配置
在 `app.py` 中可以修改以下配置：

```python
# 数据库配置
DATABASE = 'movie_system.db'

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

# 会话密钥
app.secret_key = 'your-secret-key-here'
```

### 添加新功能
1. 在 `app.py` 中添加新的路由函数
2. 在 `templates/` 目录下创建对应的HTML模板
3. 更新数据库结构（如果需要）
4. 测试功能

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 更改端口
   python app.py --port 5001
   ```

2. **依赖安装失败**
   ```bash
   # 使用国内镜像源
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **数据库初始化失败**
   - 删除 `movie_system.db` 文件重新启动
   - 检查文件读写权限

4. **图片上传失败**
   - 检查 `uploads/` 目录权限
   - 确认文件大小不超过5MB
   - 检查文件格式是否支持

### 日志查看
应用运行时会在控制台输出详细日志，包括：
- 数据库操作日志
- 用户操作日志
- 错误和异常信息

## 📈 性能优化建议
  
1. **数据库优化**
   - 为常用查询字段添加索引
   - 使用数据库连接池
   - 定期清理无用数据

2. **前端优化**
   - 图片懒加载
   - 静态资源CDN
   - 浏览器缓存优化
  
3. **服务器优化**
   - 使用Gunicorn部署
   - 配置Nginx反向代理
   - 启用Gzip压缩

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- Flask 开发团队
- Bootstrap 团队
- Font Awesome 团队
- 所有贡献者

## 📞 技术支持

如有问题或建议，请通过以下方式联系：
- 创建GitHub Issue
- 发送邮件到项目维护者

---

**电影推荐系统** - 让电影发现变得更简单！ 🎥✨