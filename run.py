#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电影推荐系统 - 启动脚本

功能：
- 自动安装依赖包
- 检查环境配置
- 启动Flask应用
"""

import os
import sys
import subprocess
import platform

def check_environment():
    """检查Python环境和依赖"""
    print("=" * 60)
    print("电影推荐系统 - 环境检查")
    print("=" * 60)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"✓ Python版本: {platform.python_version()}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("✗ 需要Python 3.7或更高版本")
        return False
    
    # 检查必要的目录
    required_dirs = ['templates', 'uploads']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}")
        else:
            print(f"✓ 目录存在: {dir_name}")
    
    return True

def install_requirements():
    """安装依赖包"""
    print("\n" + "=" * 60)
    print("安装依赖包")
    print("=" * 60)
    
    if not os.path.exists('requirements.txt'):
        print("✗ requirements.txt 文件不存在")
        return False
    
    try:
        # 使用pip安装依赖
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        return False

def main():
    """主函数"""
    # 环境检查
    if not check_environment():
        print("\n环境检查失败，请解决问题后重新运行")
        sys.exit(1)
    
    # 安装依赖
    if not install_requirements():
        print("\n依赖安装失败，请手动安装依赖包")
        print("命令: pip install -r requirements.txt")
        sys.exit(1)
    
    # 启动应用
    print("\n" + "=" * 60)
    print("启动电影推荐系统")
    print("=" * 60)
    
    try:
        from app import app
        
        print("✓ 应用启动成功！")
        print("\n访问信息：")
        print("  ▪ 本地访问: http://127.0.0.1:5000")
        print("  ▪ 网络访问: http://你的IP地址:5000")
        print("\n测试账号：")
        print("  ▪ 管理员: admin / admin123")
        print("  ▪ 普通用户: 注册新账号")
        print("\n按 Ctrl+C 停止服务")
        print("=" * 60)
        
        # 启动Flask应用
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"✗ 导入应用失败: {e}")
        print("请检查app.py文件是否存在且语法正确")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()