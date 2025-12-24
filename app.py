#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电影推荐系统 - 主应用文件
功能：
- 用户注册/登录
- 电影浏览、搜索、分类
- 评分和评论
- 管理员功能（添加/删除电影）
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import sqlite3
import bcrypt
from datetime import datetime
import os
import sys
import uuid
from werkzeug.utils import secure_filename

# 创建Flask应用实例
app = Flask(__name__)
app.secret_key = 'movie_recommendation_system_secret_key_2024'

# SQLite数据库配置
DATABASE = 'movie_system.db'

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'avi'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB（视频文件较大）

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 获取数据库连接
def get_db_connection():
    """获取数据库连接，设置行工厂为sqlite3.Row"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return conn

# 数据库操作辅助函数
def execute_db_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    执行数据库查询的通用函数
    
    Args:
        query: SQL查询语句
        params: 查询参数
        fetch_one: 是否获取单条记录
        fetch_all: 是否获取所有记录
        commit: 是否提交事务
    
    Returns:
        查询结果或操作状态
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if commit:
            conn.commit()
        
        if fetch_one:
            result = cursor.fetchone()
            return dict(result) if result else None
        elif fetch_all:
            results = cursor.fetchall()
            return [dict(row) for row in results]
        
        return cursor.lastrowid if cursor.lastrowid else True
    except Exception as e:
        print(f"数据库操作错误: {e}")
        import traceback
        traceback.print_exc()
        if conn and commit:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

# 检查用户是否登录的辅助函数
def check_login():
    """检查用户是否已登录"""
    return 'user_id' in session

# 检查用户是否是管理员
def check_admin():
    """检查用户是否具有管理员权限"""
    if not check_login():
        return False
    return session.get('role') == 'admin'

# 检查图片文件扩展名是否允许
def allowed_image_file(filename):
    """检查图片文件扩展名是否在允许的范围内"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# 检查视频文件扩展名是否允许
def allowed_video_file(filename):
    """检查视频文件扩展名是否在允许的范围内"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

# 处理图片文件上传
def handle_image_upload(file):
    """
    处理图片文件上传
    
    Args:
        file: 上传的文件对象
    
    Returns:
        保存的文件路径或None
    """
    if file and file.filename and allowed_image_file(file.filename):
        # 生成唯一文件名，避免文件名冲突
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # 保存文件
        file.save(file_path)
        # 返回相对路径，用于存储在数据库中
        return file_path
    return None

# 处理视频文件上传
def handle_video_upload(file):
    """
    处理视频文件上传
    
    Args:
        file: 上传的文件对象
    
    Returns:
        保存的文件路径或None
    """
    if file and file.filename and allowed_video_file(file.filename):
        # 生成唯一文件名，避免文件名冲突
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # 保存文件
        file.save(file_path)
        # 返回相对路径，用于存储在数据库中
        return file_path
    return None

# 创建数据库和表
def setup_database():
    """初始化数据库，创建必要的表结构"""
    try:
        print("正在初始化数据库...")
        
        # 连接到SQLite数据库
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建电影表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                director VARCHAR(100),
                year INTEGER,
                genre VARCHAR(100),
                description TEXT,
                image_url VARCHAR(500),
                video_url VARCHAR(500),  -- 视频URL字段
                video_type VARCHAR(20) DEFAULT 'external',  -- 视频类型：external(外部链接) / upload(本地上传)
                rating FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建分类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        ''')
        
        # 创建电影分类关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movie_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER,
                category_id INTEGER,
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # 创建评分表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id INTEGER,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        # 检查并添加视频相关字段（如果表已存在）
        try:
            cursor.execute("ALTER TABLE movies ADD COLUMN video_url VARCHAR(500)")
            print("已添加video_url字段")
        except sqlite3.OperationalError:
            print("video_url字段已存在")
        
        try:
            cursor.execute("ALTER TABLE movies ADD COLUMN video_type VARCHAR(20) DEFAULT 'external'")
            print("已添加video_type字段")
        except sqlite3.OperationalError:
            print("video_type字段已存在")
        
        # 检查是否有用户数据
        cursor.execute("SELECT * FROM users")
        users_exist = cursor.fetchone()
        if not users_exist:
            # 添加默认管理员账号
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                ('admin', hashed_password, 'admin@movie.com', 'admin')
            )
            print("已创建管理员账号")
        
        # 检查是否有分类数据
        cursor.execute("SELECT * FROM categories")
        categories_exist = cursor.fetchone()
        if not categories_exist:
            # 添加默认电影分类
            categories = [
                '动作片', '喜剧片', '爱情片', '科幻片', 
                '恐怖片', '剧情片', '动画片', '纪录片'
            ]
            for category in categories:
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            print("已添加电影分类")
        
        # 检查是否有电影数据
        cursor.execute("SELECT * FROM movies")
        movies_exist = cursor.fetchone()
        if not movies_exist:
            # 添加示例电影数据 - 包含视频URL
            sample_movies = [
                ('盗梦空间', '克里斯托弗·诺兰', 2010, '科幻/悬疑', '一个专业的小偷，擅长潜入他人梦境窃取机密。', 'https://picsum.photos/seed/inception/300/450.jpg', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 8.8),
                ('肖申克的救赎', '弗兰克·德拉邦特', 1994, '剧情', '一个被错误定罪的男人在监狱中寻找希望和自由的故事。', 'https://picsum.photos/seed/shawshank/300/450.jpg', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4', 9.3),
                ('泰坦尼克号', '詹姆斯·卡梅隆', 1997, '爱情/灾难', '一艘豪华游轮上的爱情故事与海难。', 'https://picsum.photos/seed/titanic/300/450.jpg', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', 7.8),
                ('阿凡达', '詹姆斯·卡梅隆', 2009, '科幻/动作', '一个残疾的前海军陆战队员在一个外星球上的冒险。', 'https://picsum.photos/seed/avatar/300/450.jpg', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', 7.8),
                ('复仇者联盟：终局之战', '罗素兄弟', 2019, '动作/科幻', '超级英雄们集结，对抗终极威胁的史诗之战。', 'https://picsum.photos/seed/avengers/300/450.jpg', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4', 8.4),
            ]
            
            for movie in sample_movies:
                cursor.execute(
                    "INSERT INTO movies (title, director, year, genre, description, image_url, video_url, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    movie
                )
                
                # 获取刚插入的电影ID
                movie_id = cursor.lastrowid
                
                # 为电影分配分类（简单地将电影类型映射到分类）
                genre_to_category = {
                    '科幻/悬疑': 4,  # 科幻片
                    '剧情': 6,       # 剧情片
                    '爱情/灾难': 3,  # 爱情片
                    '科幻/动作': 4,  # 科幻片
                }
                
                if movie[3] in genre_to_category:
                    cursor.execute(
                        "INSERT INTO movie_categories (movie_id, category_id) VALUES (?, ?)",
                        (movie_id, genre_to_category[movie[3]])
                    )
            print("已添加示例电影数据")
        
        # 提交所有更改
        conn.commit()
        conn.close()
        print("数据库初始化完成！")
        print("管理员账号: admin")
        print("管理员密码: admin123")
        print(f"数据库文件已创建: {os.path.abspath(DATABASE)}")
        return True
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==============================
# 路由定义开始
# ==============================

# 首页路由
@app.route('/')
def index():
    """首页：显示所有电影和分类"""
    # 获取所有电影（按创建时间倒序）
    movies = execute_db_query("SELECT * FROM movies ORDER BY created_at DESC", fetch_all=True)
    
    # 获取所有分类
    categories = execute_db_query("SELECT * FROM categories", fetch_all=True)
    
    return render_template('index.html', 
                         movies=movies, 
                         categories=categories, 
                         user=session)

# 用户注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册功能"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        
        # 基本验证
        if not username or not password:
            return render_template('register.html', error='用户名和密码是必填的')
        
        if len(password) < 6:
            return render_template('register.html', error='密码长度至少6位')
        
        # 检查用户名是否已存在
        existing_user = execute_db_query(
            "SELECT * FROM users WHERE username = ?", 
            (username,), 
            fetch_one=True
        )
        
        if existing_user:
            return render_template('register.html', error='用户名已存在')
        
        try:
            # 加密密码
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # 创建新用户
            user_id = execute_db_query(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email),
                commit=True
            )
            
            if user_id:
                # 自动登录
                session['user_id'] = user_id
                session['username'] = username
                session['role'] = 'user'
                return redirect(url_for('index'))
            else:
                return render_template('register.html', error='注册失败，请重试')
                
        except Exception as e:
            print(f"注册错误: {e}")
            return render_template('register.html', error='注册失败，请重试')
    
    return render_template('register.html')

# 用户登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录功能"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='用户名和密码是必填的')
        
        # 查询用户
        user = execute_db_query(
            "SELECT * FROM users WHERE username = ?", 
            (username,), 
            fetch_one=True
        )
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # 登录成功
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # 根据角色重定向
            if user['role'] == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

# 用户注销路由
@app.route('/logout')
def logout():
    """用户注销功能"""
    session.clear()
    return redirect(url_for('index'))

# 电影详情页路由
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """电影详情页面"""
    # 获取电影信息
    movie = execute_db_query(
        "SELECT * FROM movies WHERE id = ?", 
        (movie_id,), 
        fetch_one=True
    )
    
    if not movie:
        return "电影不存在", 404
    
    # 获取电影的评分和评论
    ratings = execute_db_query(
        '''SELECT r.*, u.username 
           FROM ratings r 
           JOIN users u ON r.user_id = u.id 
           WHERE r.movie_id = ? 
           ORDER BY r.created_at DESC''',
        (movie_id,),
        fetch_all=True
    )
    
    # 获取用户对该电影的评分（如果已登录）
    user_rating = None
    if check_login():
        user_rating = execute_db_query(
            "SELECT * FROM ratings WHERE user_id = ? AND movie_id = ?",
            (session['user_id'], movie_id),
            fetch_one=True
        )
    
    return render_template('movie_detail.html', 
                         movie=movie, 
                         ratings=ratings, 
                         user_rating=user_rating,
                         user=session)

# 评分和评论路由
@app.route('/rate_movie/<int:movie_id>', methods=['POST'])
def rate_movie(movie_id):
    """用户评分和评论功能"""
    if not check_login():
        return redirect(url_for('login'))
    
    try:
        rating = int(request.form.get('rating', 0))
        review = request.form.get('review', '').strip()
        
        if rating < 1 or rating > 5:
            return redirect(url_for('movie_detail', movie_id=movie_id))
        
        # 检查是否已经评分过
        existing_rating = execute_db_query(
            "SELECT * FROM ratings WHERE user_id = ? AND movie_id = ?",
            (session['user_id'], movie_id),
            fetch_one=True
        )
        
        if existing_rating:
            # 更新现有评分
            result = execute_db_query(
                "UPDATE ratings SET rating = ?, review = ? WHERE user_id = ? AND movie_id = ?",
                (rating, review, session['user_id'], movie_id),
                commit=True
            )
        else:
            # 添加新评分
            result = execute_db_query(
                "INSERT INTO ratings (user_id, movie_id, rating, review) VALUES (?, ?, ?, ?)",
                (session['user_id'], movie_id, rating, review),
                commit=True
            )
        
        if result is not None:
            # 更新电影平均评分
            execute_db_query(
                "UPDATE movies SET rating = (SELECT AVG(rating) FROM ratings WHERE movie_id = ?) WHERE id = ?",
                (movie_id, movie_id),
                commit=True
            )
        
        return redirect(url_for('movie_detail', movie_id=movie_id))
    except Exception as e:
        print(f"评分操作失败: {e}")
        return redirect(url_for('movie_detail', movie_id=movie_id))

# 分类页面路由
@app.route('/category/<int:category_id>')
def category(category_id):
    """按分类显示电影"""
    # 获取分类信息
    category_info = execute_db_query(
        "SELECT * FROM categories WHERE id = ?", 
        (category_id,), 
        fetch_one=True
    )
    
    if not category_info:
        return "分类不存在", 404
    
    # 获取该分类下的电影
    movies = execute_db_query(
        '''SELECT m.* FROM movies m 
           JOIN movie_categories mc ON m.id = mc.movie_id 
           WHERE mc.category_id = ? 
           ORDER BY m.created_at DESC''',
        (category_id,),
        fetch_all=True
    )
    
    # 获取所有分类
    categories = execute_db_query("SELECT * FROM categories", fetch_all=True)
    
    return render_template('category.html', 
                         movies=movies, 
                         category=category_info,
                         categories=categories,
                         user=session)

# 搜索功能路由
@app.route('/search')
def search():
    """电影搜索功能"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    # 执行搜索（标题、导演、类型、描述）
    search_pattern = f'%{query}%'
    movies = execute_db_query(
        "SELECT * FROM movies WHERE title LIKE ? OR director LIKE ? OR genre LIKE ? OR description LIKE ? ORDER BY created_at DESC",
        (search_pattern, search_pattern, search_pattern, search_pattern),
        fetch_all=True
    )
    
    # 获取所有分类
    categories = execute_db_query("SELECT * FROM categories", fetch_all=True)
    
    return render_template('search.html', 
                         movies=movies, 
                         query=query,
                         categories=categories,
                         user=session)

# ==============================
# 管理员功能路由
# ==============================

# 管理员面板路由
@app.route('/admin')
def admin_panel():
    """管理员面板"""
    # 检查是否登录且是管理员
    if not check_login() or not check_admin():
        return redirect(url_for('login'))
    
    # 获取所有电影
    movies = execute_db_query("SELECT * FROM movies ORDER BY created_at DESC", fetch_all=True)
    
    # 获取所有用户
    users = execute_db_query("SELECT * FROM users ORDER BY created_at DESC", fetch_all=True)
    
    return render_template('admin_panel.html', 
                         movies=movies, 
                         users=users,
                         user=session)

# 管理员添加电影路由
@app.route('/admin/add_movie', methods=['GET', 'POST'])
def admin_add_movie():
    """管理员添加电影功能"""
    # 检查是否登录且是管理员
    if not check_login() or not check_admin():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # 打印调试信息
        print("表单数据:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
        
        # 检查是否有文件上传
        if 'image_file' in request.files:
            print("有图片文件上传")
            file = request.files['image_file']
            print(f"图片文件信息: {file.filename}")
        else:
            print("无图片文件上传")
        
        if 'video_file' in request.files:
            print("有视频文件上传")
            file = request.files['video_file']
            print(f"视频文件信息: {file.filename}")
        else:
            print("无视频文件上传")
        
        title = request.form.get('title', '').strip()
        director = request.form.get('director', '').strip()
        year = request.form.get('year', '').strip()
        genre = request.form.get('genre', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        video_url = request.form.get('video_url', '').strip()
        categories = request.form.getlist('categories')
        
        # 处理图片文件上传
        uploaded_image_path = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                uploaded_image_path = handle_image_upload(file)
                if uploaded_image_path:
                    print(f"图片文件已上传: {uploaded_image_path}")
                else:
                    print("图片文件上传失败")
        
        # 处理视频文件上传
        uploaded_video_path = None
        if 'video_file' in request.files:
            file = request.files['video_file']
            if file and file.filename:
                uploaded_video_path = handle_video_upload(file)
                if uploaded_video_path:
                    print(f"视频文件已上传: {uploaded_video_path}")
                else:
                    print("视频文件上传失败")
        
        # 简单验证
        if not title or not director or not year or not genre or not description:
            error_msg = '所有字段都是必填的'
            print(f"验证失败: {error_msg}")
            categories_list = execute_db_query("SELECT * FROM categories", fetch_all=True)
            return render_template('admin_add_movie.html', 
                                     categories=categories_list, 
                                     user=session, 
                                     error=error_msg)
        
        try:
            # 处理图片URL或上传的文件
            final_image_url = None
            
            # 优先使用上传的文件
            if uploaded_image_path:
                # 将文件路径转换为URL格式，以便在网页中显示
                final_image_url = f'/{uploaded_image_path}'
                print(f"使用上传的文件作为图片URL: {final_image_url}")
            # 如果有URL，则使用URL
            elif image_url:
                final_image_url = image_url
                print(f"使用提供的URL: {final_image_url}")
            # 如果都没有，则使用默认图片
            else:
                final_image_url = f"https://picsum.photos/seed/{title.replace(' ', '')}/300/450.jpg"
                print(f"使用默认图片: {final_image_url}")
            
            # 处理视频URL或上传的文件
            final_video_url = None
            video_type = 'external'  # 默认使用外部链接
            
            # 优先使用上传的视频文件
            if uploaded_video_path:
                final_video_url = f'/{uploaded_video_path}'
                video_type = 'upload'
                print(f"使用上传的视频文件: {final_video_url}")
            # 如果有视频URL，则使用URL
            elif video_url:
                final_video_url = video_url
                print(f"使用提供的视频URL: {final_video_url}")
            
            # 添加电影
            movie_id = execute_db_query(
                "INSERT INTO movies (title, director, year, genre, description, image_url, video_url, video_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, director, year, genre, description, final_image_url, final_video_url, video_type),
                commit=True
            )
            
            print(f"电影插入结果: {movie_id}")
            
            if not movie_id:
                error_msg = '添加电影失败，请重试'
                print(f"插入失败: {error_msg}")
                categories_list = execute_db_query("SELECT * FROM categories", fetch_all=True)
                return render_template('admin_add_movie.html', 
                                     categories=categories_list, 
                                     user=session, 
                                     error=error_msg)
            
            # 添加分类关联
            if categories:
                print(f"添加分类关联: {categories}")
                for category_id in categories:
                    result = execute_db_query(
                        "INSERT INTO movie_categories (movie_id, category_id) VALUES (?, ?)",
                        (movie_id, category_id),
                        commit=True
                    )
                    print(f"分类关联插入结果: {result}")
            
            return redirect(url_for('admin_panel'))
        except Exception as e:
            error_msg = f'添加电影失败: {str(e)}'
            print(f"异常: {error_msg}")
            import traceback
            traceback.print_exc()
            categories_list = execute_db_query("SELECT * FROM categories", fetch_all=True)
            return render_template('admin_add_movie.html', 
                                 categories=categories_list, 
                                 user=session, 
                                 error=error_msg)
    
    # 获取所有分类
    categories = execute_db_query("SELECT * FROM categories", fetch_all=True)
    
    return render_template('admin_add_movie.html', categories=categories, user=session)

# 管理员编辑电影路由 - GET显示编辑表单
@app.route('/admin/edit_movie/<int:movie_id>', methods=['GET'])
def admin_edit_movie(movie_id):
    """管理员编辑电影功能 - 显示编辑表单"""
    # 检查是否登录且是管理员
    if not check_login() or not check_admin():
        return redirect(url_for('login'))
    
    # 获取电影信息
    movie = execute_db_query(
        "SELECT * FROM movies WHERE id = ?", 
        (movie_id,), 
        fetch_one=True
    )
    
    if not movie:
        return "电影不存在", 404
    
    # 获取电影的分类
    movie_categories = execute_db_query(
        "SELECT category_id FROM movie_categories WHERE movie_id = ?",
        (movie_id,),
        fetch_all=True
    )
    
    # 获取所有分类
    categories = execute_db_query("SELECT * FROM categories", fetch_all=True)
    
    # 将电影的分类ID转换为列表
    selected_categories = [cat['category_id'] for cat in movie_categories]
    
    return render_template('admin_edit_movie.html', 
                         movie=movie, 
                         categories=categories, 
                         selected_categories=selected_categories,
                         user=session)

# 管理员编辑电影路由 - POST处理编辑提交
@app.route('/admin/edit_movie/<int:movie_id>', methods=['POST'])
def admin_edit_movie_submit(movie_id):
    """管理员编辑电影功能 - 处理编辑提交"""
    # 检查是否登录且是管理员
    if not check_login() or not check_admin():
        return redirect(url_for('login'))
    
    # 检查电影是否存在
    existing_movie = execute_db_query(
        "SELECT * FROM movies WHERE id = ?", 
        (movie_id,), 
        fetch_one=True
    )
    
    if not existing_movie:
        return "电影不存在", 404
    
    if request.method == 'POST':
        # 打印调试信息
        print("编辑电影表单数据:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
        
        title = request.form.get('title', '').strip()
        director = request.form.get('director', '').strip()
        year = request.form.get('year', '').strip()
        genre = request.form.get('genre', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        video_url = request.form.get('video_url', '').strip()
        categories = request.form.getlist('categories')
        
        # 处理图片文件上传
        uploaded_image_path = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                uploaded_image_path = handle_image_upload(file)
                if uploaded_image_path:
                    print(f"图片文件已上传: {uploaded_image_path}")
                else:
                    print("图片文件上传失败")
        
        # 处理视频文件上传
        uploaded_video_path = None
        if 'video_file' in request.files:
            file = request.files['video_file']
            if file and file.filename:
                uploaded_video_path = handle_video_upload(file)
                if uploaded_video_path:
                    print(f"视频文件已上传: {uploaded_video_path}")
                else:
                    print("视频文件上传失败")
        
        # 简单验证
        if not title or not director or not year or not genre or not description:
            error_msg = '所有字段都是必填的'
            print(f"验证失败: {error_msg}")
            
            # 重新获取数据用于渲染模板
            movie = execute_db_query(
                "SELECT * FROM movies WHERE id = ?", 
                (movie_id,), 
                fetch_one=True
            )
            movie_categories = execute_db_query(
                "SELECT category_id FROM movie_categories WHERE movie_id = ?",
                (movie_id,),
                fetch_all=True
            )
            categories_list = execute_db_query("SELECT * FROM categories", fetch_all=True)
            selected_categories = [cat['category_id'] for cat in movie_categories]
            
            return render_template('admin_edit_movie.html', 
                                 movie=movie, 
                                 categories=categories_list, 
                                 selected_categories=selected_categories,
                                 user=session, 
                                 error=error_msg)
        
        try:
            # 处理图片URL或上传的文件
            final_image_url = existing_movie['image_url']  # 默认使用原图片
            
            # 优先使用上传的文件
            if uploaded_image_path:
                # 将文件路径转换为URL格式，以便在网页中显示
                final_image_url = f'/{uploaded_image_path}'
                print(f"使用上传的文件作为图片URL: {final_image_url}")
            # 如果有URL，则使用URL
            elif image_url:
                final_image_url = image_url
                print(f"使用提供的URL: {final_image_url}")
            
            # 处理视频URL或上传的文件
            final_video_url = existing_movie['video_url']  # 默认使用原视频
            video_type = existing_movie['video_type']  # 默认使用原类型
            
            # 优先使用上传的视频文件
            if uploaded_video_path:
                final_video_url = f'/{uploaded_video_path}'
                video_type = 'upload'
                print(f"使用上传的视频文件: {final_video_url}")
            # 如果有视频URL，则使用URL
            elif video_url:
                final_video_url = video_url
                video_type = 'external'
                print(f"使用提供的视频URL: {final_video_url}")
            
            # 更新电影信息
            result = execute_db_query(
                """UPDATE movies SET 
                   title = ?, director = ?, year = ?, genre = ?, description = ?, 
                   image_url = ?, video_url = ?, video_type = ? 
                   WHERE id = ?""",
                (title, director, year, genre, description, final_image_url, final_video_url, video_type, movie_id),
                commit=True
            )
            
            print(f"电影更新结果: {result}")
            
            if result is None:
                error_msg = '更新电影失败，请重试'
                print(f"更新失败: {error_msg}")
                
                # 重新获取数据用于渲染模板
                movie = execute_db_query(
                    "SELECT * FROM movies WHERE id = ?", 
                    (movie_id,), 
                    fetch_one=True
                )
                movie_categories = execute_db_query(
                    "SELECT category_id FROM movie_categories WHERE movie_id = ?",
                    (movie_id,),
                    fetch_all=True
                )
                categories_list = execute_db_query("SELECT * FROM categories", fetch_all=True)
                selected_categories = [cat['category_id'] for cat in movie_categories]
                
                return render_template('admin_edit_movie.html', 
                                     movie=movie, 
                                     categories=categories_list, 
                                     selected_categories=selected_categories,
                                     user=session, 
                                     error=error_msg)
            
            # 更新分类关联：先删除旧的，再添加新的
            execute_db_query("DELETE FROM movie_categories WHERE movie_id = ?", (movie_id,), commit=True)
            
            if categories:
                print(f"更新分类关联: {categories}")
                for category_id in categories:
                    execute_db_query(
                        "INSERT INTO movie_categories (movie_id, category_id) VALUES (?, ?)",
                        (movie_id, category_id),
                        commit=True
                    )
            
            return redirect(url_for('admin_panel'))
        except Exception as e:
            error_msg = f'更新电影失败: {str(e)}'
            print(f"异常: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # 重新获取数据用于渲染模板
            movie = execute_db_query(
                "SELECT * FROM movies WHERE id = ?", 
                (movie_id,), 
                fetch_one=True
            )
            movie_categories = execute_db_query(
                "SELECT category_id FROM movie_categories WHERE movie_id = ?",
                (movie_id,),
                fetch_all=True
            )
            categories_list = execute_db_query("SELECT * FROM categories", fetch_all=True)
            selected_categories = [cat['category_id'] for cat in movie_categories]
            
            return render_template('admin_edit_movie.html', 
                                 movie=movie, 
                                 categories=categories_list, 
                                 selected_categories=selected_categories,
                                 user=session, 
                                 error=error_msg)

# 管理员删除电影路由
@app.route('/admin/delete_movie/<int:movie_id>')
def admin_delete_movie(movie_id):
    """管理员删除电影功能"""
    # 检查是否登录且是管理员
    if not check_login() or not check_admin():
        return redirect(url_for('login'))
    
    try:
        # 删除电影相关的评分和分类关联
        execute_db_query("DELETE FROM ratings WHERE movie_id = ?", (movie_id,), commit=True)
        execute_db_query("DELETE FROM movie_categories WHERE movie_id = ?", (movie_id,), commit=True)
        
        # 删除电影
        result = execute_db_query("DELETE FROM movies WHERE id = ?", (movie_id,), commit=True)
        
        if result:
            print(f"电影 {movie_id} 删除成功")
        else:
            print(f"电影 {movie_id} 删除失败")
        
        return redirect(url_for('admin_panel'))
    except Exception as e:
        print(f"删除电影错误: {e}")
        return redirect(url_for('admin_panel'))

# 添加访问上传文件的静态路由
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的静态访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 处理文件上传大小超限的错误
@app.errorhandler(413)
def too_large(e):
    """处理文件上传大小超限的错误"""
    error_msg = '上传的文件太大，请选择小于5MB的图片文件'
    categories = execute_db_query("SELECT * FROM categories", fetch_all=True)
    return render_template('admin_add_movie.html', 
                         categories=categories, 
                         user=session, 
                         error=error_msg)

# 应用启动入口
if __name__ == '__main__':
    # 初始化数据库
    if setup_database():
        print("数据库初始化成功，启动应用...")
        print("访问 http://127.0.0.1:5000 使用应用")
        print("管理员账号: admin")
        print("管理员密码: admin123")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("数据库初始化失败，无法启动应用")