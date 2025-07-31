# -*- coding: utf-8 -*-
"""
现代主题模块 - 包含深色/浅色主题
"""

def get_modern_dark_theme(font_size=13):
    return f"""
    /* 现代深色主题 */
    QMainWindow {{
        background-color: #2d2d2d;
        color: #ffffff;
        font-family: 'Segoe UI';
    }}
    QPushButton {{
        background: #3a3a3a;
        border: 1px solid #4a4a4a;
        color: #ffffff;
        font-size: {font_size}px;
    }}
    """

def get_light_theme(font_size=13):
    return f"""
    /* 现代浅色主题 */
    QMainWindow {{
        background-color: #f5f5f5;
        color: #333333;
        font-family: 'Segoe UI';
    }}
    QPushButton {{
        background: #e0e0e0;
        border: 1px solid #cccccc;
        color: #333333;
        font-size: {font_size}px;
    }}
    """