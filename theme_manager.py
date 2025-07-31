# -*- coding: utf-8 -*-
"""
主题管理器 - 古朴纸书感主题
温暖的米黄色调，营造古典书卷气息
"""

def get_vintage_paper_theme(font_size=13):
    """古朴纸书感主题 - 温暖的米黄色调，营造古典书卷气息"""
    return f"""
    /* 主窗口 */
    QMainWindow {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #faf6f0, stop:1 #f0ead6);
        color: #3c2e26;
        font-family: "Microsoft YaHei", "SimHei", sans-serif;
    }}
    
    QWidget {{
        background-color: transparent;
        color: #3c2e26;
        font-size: {font_size}px;
    }}
    
    /* 工具栏 */
    QToolBar {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f0ead6, stop:1 #e8dcc0);
        border: none;
        padding: 12px;
        spacing: 15px;
        border-bottom: 2px solid #d4c4a8;

    }}
    
    QToolBar QLabel {{
        color: #5d4e37;
        font-weight: 600;
        margin-right: 10px;
        font-size: {font_size}px;

    }}
    
    /* 下拉框 */
    QComboBox {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #faf6f0, stop:1 #f0ead6);
        border: 2px solid #d4c4a8;
        border-radius: 8px;
        padding: 10px 15px;
        color: #3c2e26;
        font-size: {font_size}px;
        min-width: 130px;
        font-weight: 500;
    }}
    
    QComboBox:hover {{
        border-color: #b8860b;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #fff8f0, stop:1 #f5f0e6);

    }}
    
    QComboBox:focus {{
        border-color: #8b7355;
        outline: none;

    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 25px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 6px solid #5d4e37;
        margin-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: #faf6f0;
        border: 2px solid #d4c4a8;
        border-radius: 8px;
        selection-background-color: #deb887;
        color: #3c2e26;
        padding: 6px;
        font-size: {font_size}px;
    }}
    
    /* 按钮样式 */
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #deb887, stop:1 #cd853f);
        border: 2px solid #b8860b;
        border-radius: 8px;
        color: #ffffff;
        font-size: {font_size}px;
        font-weight: 600;
        padding: 10px 18px;
        min-height: 22px;

    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f0d68c, stop:1 #daa520);
        border-color: #daa520;


    }}
    
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #cd853f, stop:1 #b8860b);


    }}
    
    QPushButton:disabled {{
        background-color: #e8dcc0;
        border-color: #d4c4a8;
        color: #a0a0a0;
    }}
    
    /* 主要操作按钮 */
    QPushButton#generateBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #daa520, stop:1 #b8860b);
        border: 2px solid #8b7355;
        font-size: 14px;
        font-weight: 700;
        padding: 14px 28px;
        min-height: 24px;
        color: #2f1b14;
    }}
    
    QPushButton#generateBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #ffd700, stop:1 #daa520);
        border-color: #a0522d;
    }}
    
    QPushButton#generateBtn:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #b8860b, stop:1 #8b6914);
        border-color: #654321;
    }}
    
    /* 次要按钮 */
    QPushButton#copyBtn, QPushButton#saveBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #e8dcc0, stop:1 #d4c4a8);
        border: 2px solid #c4b49a;
        color: #5d4e37;
        font-size: 13px;
    }}
    
    QPushButton#copyBtn:hover, QPushButton#saveBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f0e6d2, stop:1 #e0d0b6);
        border-color: #b8a88c;
    }}
    
    /* 危险按钮 */
    QPushButton#clearBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #d2b48c, stop:1 #bc9a6a);
        border: 2px solid #a0522d;
        color: #2f1b14;
        font-size: 13px;
    }}
    
    QPushButton#clearBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #deb887, stop:1 #cd853f);
        border-color: #8b4513;
    }}
    
    /* 信息按钮 */
    QPushButton#historyBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f5deb3, stop:1 #deb887);
        border: 2px solid #d2b48c;
        color: #3c2e26;
        font-size: 13px;
    }}
    
    QPushButton#historyBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #fff8dc, stop:1 #f5deb3);
        border-color: #daa520;
    }}
    

    
    /* 文本编辑器 */
    QTextEdit {{
        background-color: #fefcf8;
        border: 2px solid #d4c4a8;
        border-radius: 8px;
        color: #3c2e26;
        font-family: "Times New Roman", "SimSun", serif;
        font-size: {font_size}px;
        padding: 15px;
        line-height: 1.6;
        selection-background-color: #deb887;
    }}
    
    QTextEdit:focus {{
        border-color: #8b7355;
        outline: none;

        background-color: #fffef9;
    }}
    
    /* 标签 */
    QLabel {{
        color: #3c2e26;
        font-size: {font_size}px;
        font-weight: 500;
    }}
    
    QLabel#formatLabel {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f0ead6, stop:1 #e8dcc0);
        border: 2px solid #d4c4a8;
        border-radius: 8px;
        padding: 10px 15px;
        color: #5d4e37;
        font-size: {font_size - 1}px;
        font-style: italic;
    }}
    
    QLabel#previewLabel {{
        font-size: {font_size + 2}px;
        font-weight: 700;
        color: #5d4e37;
        
    }}
    
    QLabel#wisdomLabel {{
        color: #8b4513;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f5f0e6, stop:1 #ede0d0);
        border: 2px solid #d4c4a8;
        border-radius: 12px;
        padding: 15px 25px;
        
    }}
    
    /* 状态栏 */
    QStatusBar {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f0ead6, stop:1 #e8dcc0);
        border-top: 2px solid #d4c4a8;
        color: #5d4e37;
        font-size: {font_size - 1}px;
        padding: 8px;
    }}
    
    /* 对话框 */
    QDialog {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #faf6f0, stop:1 #f0ead6);
        color: #3c2e26;
        border: 2px solid #d4c4a8;
        border-radius: 12px;
    }}
    
    /* 表格 */
    QTableWidget {{
        background-color: #fefcf8;
        border: 2px solid #d4c4a8;
        border-radius: 8px;
        gridline-color: #e8dcc0;
        font-size: {font_size + 2}px;
        selection-background-color: #deb887;
        alternate-background-color: #fefcf8;
        color: #3c2e26;
    }}
    
    QTableWidget::item {{
        background-color: #fefcf8;
        color: #3c2e26;
        padding: 8px;
        border: none;
    }}
    
    QTableWidget::item:alternate {{
        background-color: #fefcf8;
    }}
    
    QTableWidget::item:selected {{
        background-color: #deb887;
        color: #3c2e26;
    }}
    
    QHeaderView::section {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f0ead6, stop:1 #e8dcc0);
        border: 1px solid #d4c4a8;
        padding: 8px 12px;
        color: #5d4e37;
        font-weight: 600;
        font-size: {font_size + 2}px;
    }}
    
    QTableWidget::item:hover:first-child {{
        background-color: inherit !important;
    }}
    
    QTableWidget::item:selected:first-child {{
        background-color: inherit !important;
    }}
    
    /* 滚动条 */
    QScrollBar:vertical {{
        background: #f0ead6;
        width: 16px;
        border-radius: 8px;
        border: 1px solid #d4c4a8;
    }}
    
    QScrollBar::handle:vertical {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                  stop:0 #deb887, stop:1 #cd853f);
        border-radius: 6px;
        min-height: 30px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                  stop:0 #f0d68c, stop:1 #daa520);
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* 输入框 */
    QLineEdit {{
        background-color: #fefcf8;
        border: 2px solid #d4c4a8;
        border-radius: 6px;
        padding: 8px 12px;
        color: #3c2e26;
        font-size: {font_size}px;
        selection-background-color: #deb887;
    }}
    
    QLineEdit:focus {{
        border-color: #8b7355;
        outline: none;
        
        background-color: #fffef9;
    }}
    
    /* 消息框 */
    QMessageBox {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #faf6f0, stop:1 #f0ead6);
        color: #3c2e26;
    }}
    
    /* 分组框 */
    QGroupBox {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f8f4f0, stop:1 #f0ead6);
        border: 2px solid #d4c4a8;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 15px;
        font-size: {font_size}px;
        font-weight: 600;
        color: #5d4e37;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px 0 8px;
        background-color: #faf6f0;
        border: 1px solid #d4c4a8;
        border-radius: 4px;
    }}
    
    /* 复选框 */
    QCheckBox {{
        color: #3c2e26;
        font-size: {font_size}px;
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid #d4c4a8;
        border-radius: 4px;
        background-color: #fefcf8;
    }}
    
    QCheckBox::indicator:checked {{
        background-color: #deb887;
        border-color: #b8860b;
    }}
    
    QCheckBox::indicator:checked::after {{
        content: "✓";
        color: #5d4e37;
        font-weight: bold;
    }}
    
    /* 面板样式 */
    QWidget#leftPanel {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #faf8f5, stop:1 #f2ede3);
        border: 2px solid #e8dcc0;
        border-radius: 12px;
        margin: 5px;
        
    }}
    
    QWidget#rightPanel {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #faf8f5, stop:1 #f2ede3);
        border: 2px solid #e8dcc0;
        border-radius: 12px;
        margin: 5px;
        
    }}
    
    QWidget#centerPanel {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #f5f2ed, stop:1 #ede6d8);
        border: 2px solid #d4c4a8;
        border-radius: 12px;
        margin: 5px;
        
    }}
    """

# 主题映射字典
THEME_MAP = {
    ("古朴纸书感", "classic"): get_vintage_paper_theme
}

def get_theme_list():
    """获取可用主题列表"""
    return list(THEME_MAP.keys())

def get_theme_style(theme_name, font_size=13):
    """根据主题名称获取样式表"""
    if theme_name in THEME_MAP:
        return THEME_MAP[theme_name](font_size)
    else:
        # 默认返回古朴纸书感主题
        return get_vintage_paper_theme(font_size)