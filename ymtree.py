import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                             QSplitter, QGroupBox, QMessageBox, QComboBox,
                             QToolBar, QAction, QStatusBar, QFrame, QDialog,
                             QDialogButtonBox, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QTabWidget,
                             QSpinBox, QTextBrowser, QColorDialog, QButtonGroup,
                             QScrollArea, QProgressDialog)
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QSettings, QThread
from database import DatabaseManager
from theme_manager import get_theme_style, get_theme_list

class SaveDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("保存树状图")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        self.load_topics()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 名称输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("图表名称:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入图表名称")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 专题选择
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("选择专题:"))
        self.topic_combo = QComboBox()
        topic_layout.addWidget(self.topic_combo)
        
        self.new_topic_btn = QPushButton("新建专题")
        self.new_topic_btn.clicked.connect(self.create_new_topic)
        topic_layout.addWidget(self.new_topic_btn)
        layout.addLayout(topic_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_topics(self):
        self.topic_combo.clear()
        self.topic_combo.addItem("未分类", None)
        
        if self.db_manager:
            topics = self.db_manager.get_topics()
            for topic in topics:
                self.topic_combo.addItem(topic['name'], topic['id'])
    
    def create_new_topic(self):
        dialog = TopicDialog(self, self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_topics()
    
    def get_save_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'topic_id': self.topic_combo.currentData()
        }

class TopicDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("创建新专题")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 专题名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("专题名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 专题描述
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("专题描述:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_topic)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def save_topic(self):
        name = self.name_edit.text().strip()
        desc = self.desc_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "警告", "请输入专题名称")
            return
        
        try:
            topic_id = self.db_manager.create_topic(name, desc)
            QMessageBox.information(self, "成功", "专题创建成功！")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建专题失败：{str(e)}")

class PreviewDialog(QDialog):
    def __init__(self, parent=None, diagram=None, all_diagrams=None):
        super().__init__(parent)
        self.parent_window = parent
        self.diagram = diagram
        self.all_diagrams = all_diagrams or []
        self.current_index = self.all_diagrams.index(diagram) if diagram in self.all_diagrams else 0
        self.setWindowTitle(f"预览 - {diagram['name']}")
        self.setModal(True)
        self.resize(1000, 800)
        self.init_ui()
        self.load_content()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 树枝图名称显示（移到顶部）
        name_layout = QHBoxLayout()
        name_layout.addStretch()
        self.name_label = QLabel()
        self.name_label.setObjectName("previewNameLabel")
        name_layout.addWidget(self.name_label)
        name_layout.addStretch()
        layout.addLayout(name_layout)
        
        # 导航栏
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("上一个")
        self.prev_btn.clicked.connect(self.prev_diagram)
        nav_layout.addWidget(self.prev_btn)
        
        self.diagram_label = QLabel()
        self.diagram_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.diagram_label)
        
        self.next_btn = QPushButton("下一个")
        self.next_btn.clicked.connect(self.next_diagram)
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
        # 内容区域
        content_layout = QHBoxLayout()
        
        # 左侧：生成结果
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("生成结果:"))
        
        self.result_edit = QTextEdit()
        self.result_edit.setFont(QFont("SimSun", 12))
        left_layout.addWidget(self.result_edit)
        
        content_layout.addWidget(left_panel)
        
        # 右侧：说明内容
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 说明内容标题
        desc_header_layout = QHBoxLayout()
        desc_header_layout.addWidget(QLabel("说明内容 (支持Markdown格式):"))
        
        # 添加Markdown帮助按钮
        self.markdown_help_btn = QPushButton("Markdown语法帮助")
        self.markdown_help_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #d2b48c, stop:1 #bc9a6a);
                color: #2f1b14;
                border: 2px solid #a0522d;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 8px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #deb887, stop:1 #cd853f);
                border-color: #8b4513;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #bc9a6a, stop:1 #a0522d);
                border-color: #654321;
            }
        """)
        self.markdown_help_btn.clicked.connect(self.show_markdown_help)
        desc_header_layout.addWidget(self.markdown_help_btn)
        desc_header_layout.addStretch()
        right_layout.addLayout(desc_header_layout)
        
        # 说明内容编辑区域（类似Typora的所见即所得）
        self.description_edit = QTextEdit()
        self.description_edit.setFont(QFont("SimSun", 12))
        self.description_edit.textChanged.connect(self.on_description_changed)
        # 设置为富文本模式以支持HTML渲染
        self.description_edit.setAcceptRichText(True)
        right_layout.addWidget(self.description_edit)
        
        # 用于存储原始Markdown文本的变量
        self.markdown_text = ""
        self.is_updating = False
        
        content_layout.addWidget(right_panel)
        
        layout.addLayout(content_layout)
        
        self.update_navigation()
        
        # 设置焦点策略以接收键盘事件
        self.setFocusPolicy(Qt.StrongFocus)
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_Up:
            self.prev_diagram()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_Down:
            self.next_diagram()
        else:
            super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件"""
        if event.angleDelta().y() > 0:
            self.prev_diagram()
        else:
            self.next_diagram()
    
    def load_content(self):
        if self.diagram:
            self.result_edit.setPlainText(self.diagram['result'])
            # 说明内容可以从content字段获取，或者设置为空让用户自己编辑
            description_text = self.diagram.get('description', '')
            self.markdown_text = description_text
            
            # 根据内容是否包含Markdown语法来决定显示方式
            if self.has_markdown_syntax(description_text):
                html_content = self.convert_markdown_to_html(description_text)
                self.description_edit.setHtml(html_content)
            else:
                self.description_edit.setPlainText(description_text)
                
            self.setWindowTitle(f"预览 - {self.diagram['name']}")
            self.diagram_label.setText(f"{self.current_index + 1} / {len(self.all_diagrams)}")
            self.name_label.setText(self.diagram['name'])
    
    def update_navigation(self):
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.all_diagrams) - 1)
    
    def prev_diagram(self):
        if self.current_index > 0:
            self.auto_save()  # 自动保存当前修改
            self.current_index -= 1
            self.diagram = self.all_diagrams[self.current_index]
            self.load_content()
            self.update_navigation()
    
    def next_diagram(self):
        if self.current_index < len(self.all_diagrams) - 1:
            self.auto_save()  # 自动保存当前修改
            self.current_index += 1
            self.diagram = self.all_diagrams[self.current_index]
            self.load_content()
            self.update_navigation()
    
    def auto_save(self):
        """自动保存修改，不显示提示信息"""
        try:
            new_result = self.result_edit.toPlainText()
            # 使用存储的原始Markdown文本而不是可能包含HTML的显示文本
            new_description = self.markdown_text if hasattr(self, 'markdown_text') else self.description_edit.toPlainText()
            
            # 调用数据库更新方法，将说明内容保存到content字段
            if self.parent_window.db_manager.update_diagram_content(self.diagram['id'], new_description, new_result):
                # 更新本地数据
                self.diagram['content'] = new_description
                self.diagram['result'] = new_result
                self.diagram['description'] = new_description
                # 更新父窗口的数据
                for i, d in enumerate(self.all_diagrams):
                    if d['id'] == self.diagram['id']:
                        self.all_diagrams[i]['content'] = new_description
                        self.all_diagrams[i]['result'] = new_result
                        self.all_diagrams[i]['description'] = new_description
                        break
        except Exception as e:
            pass  # 静默处理错误，不显示提示
    
    def on_description_changed(self):
        """说明内容改变时的处理 - 类似Typora的实时渲染"""
        if self.is_updating:
            return
            
        # 获取当前文本
        current_text = self.description_edit.toPlainText()
        
        # 检测是否包含Markdown语法
        if self.has_markdown_syntax(current_text):
            # 包含Markdown语法，渲染为HTML
            self.is_updating = True
            html_content = self.convert_markdown_to_html(current_text)
            cursor_position = self.description_edit.textCursor().position()
            self.description_edit.setHtml(html_content)
            # 尝试恢复光标位置（简化处理）
            cursor = self.description_edit.textCursor()
            cursor.setPosition(min(cursor_position, len(self.description_edit.toPlainText())))
            self.description_edit.setTextCursor(cursor)
            self.is_updating = False
        
        # 更新存储的Markdown文本
        self.markdown_text = current_text
    
    def has_markdown_syntax(self, text):
        """检测文本是否包含Markdown语法"""
        import re
        
        # 检测常见的Markdown语法
        markdown_patterns = [
            r'^#{1,6}\s+',  # 标题
            r'\*\*.*?\*\*',  # 粗体
            r'\*.*?\*',      # 斜体
            r'`.*?`',        # 行内代码
            r'```[\s\S]*?```',  # 代码块
            r'\[.*?\]\(.*?\)',  # 链接
            r'^\s*[-*+]\s+',    # 无序列表
            r'^\s*\d+\.\s+',   # 有序列表
            r'^>\s+',           # 引用
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False
    
    def convert_markdown_to_html(self, markdown_text):
        """将Markdown文本转换为HTML"""
        if not markdown_text.strip():
            return ""
        
        # 简单的Markdown转HTML实现
        html = markdown_text
        
        # 标题转换
        import re
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # 粗体和斜体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # 代码块
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # 链接
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # 列表
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if re.match(r'^\s*[-*+]\s+', line):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                item_text = re.sub(r'^\s*[-*+]\s+', '', line)
                result_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                if line.strip():
                    result_lines.append(f'<p>{line}</p>')
                else:
                    result_lines.append('<br>')
        
        if in_list:
            result_lines.append('</ul>')
        
        return '\n'.join(result_lines)
    
    def show_markdown_help(self):
        """显示Markdown语法帮助对话框"""
        help_dialog = MarkdownHelpDialog(self)
        help_dialog.exec_()
    
    def closeEvent(self, event):
        """关闭时自动保存"""
        self.auto_save()
        super().closeEvent(event)

class HistoryDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.parent_window = parent
        self.setWindowTitle("我的树枝图")
        self.setModal(True)
        self.resize(900, 700)
        # 删除确认设置
        self.delete_confirm_disabled = False
        self.delete_confirm_disable_time = None
        self.init_ui()
        self.load_diagrams()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 筛选区域
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("筛选专题:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("全部", None)
        topics = self.db_manager.get_topics()
        for topic in topics:
            self.filter_combo.addItem(topic['name'], topic['id'])
        self.filter_combo.currentIndexChanged.connect(self.filter_diagrams)
        filter_layout.addWidget(self.filter_combo)
        
        # 添加删除主题按钮 - 古朴纸书感设计
        self.delete_topic_btn = QPushButton("删除当前主题")
        self.delete_topic_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #d2b48c, stop:1 #bc9a6a);
                color: #2f1b14;
                border: 2px solid #a0522d;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 6px 12px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #deb887, stop:1 #cd853f);
                border-color: #8b4513;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #bc9a6a, stop:1 #a0522d);
                border-color: #654321;
            }
            QPushButton:disabled {
                background-color: #e8dcc0;
                border-color: #d4c4a8;
                color: #8b7355;
            }
        """)
        self.delete_topic_btn.clicked.connect(self.delete_current_topic)
        self.delete_topic_btn.setEnabled(False)  # 默认禁用
        filter_layout.addWidget(self.delete_topic_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # 表格
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["名称", "专题", "创建时间", "操作"])
        # 现代化表格布局设计 - 基于UI设计最佳实践
        self.table.horizontalHeader().setStretchLastSection(True)  # 最后一列自适应
        
        # 优化列宽分配 - 基于内容重要性和可读性
        self.table.setColumnWidth(0, 250)  # 名称列 - 主要内容，给予充足空间
        self.table.setColumnWidth(1, 150)  # 专题列 - 适中宽度
        self.table.setColumnWidth(2, 200)  # 创建时间列 - 确保完整显示时间格式
        # 操作列使用自适应宽度，确保按钮完整显示
        
        # 现代化表格样式设计
        self.table.setAlternatingRowColors(True)  # 交替行颜色提升可读性
        self.table.setShowGrid(False)  # 隐藏网格线，使用更简洁的设计
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        
        # 设置表格头部样式
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # 表头文字居中
        header.setHighlightSections(False)  # 禁用头部高亮
        
        # 优化行高和间距 - 增加行高以完全显示操作按钮
        self.table.verticalHeader().setDefaultSectionSize(80) # 行高
        
        # 设置古朴纸书感表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #f5f5dc, stop:1 #f0e68c);
                alternate-background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                                          stop:0 #faf0e6, stop:1 #f5deb3);
                color: #8B4513;
                border: 2px solid #daa520;
                border-radius: 8px;
                gridline-color: #daa520;
                font-size: 16px;
                selection-background-color: #deb887;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #daa520;
                color: #8B4513;
                background-color: #f5f5dc;
            }
            QTableWidget::item:alternate {
                background-color: #faf0e6;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #deb887, stop:1 #cd853f);
                color: #2f1b14;
            }
            QTableWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #f0e68c, stop:1 #daa520);
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #daa520, stop:1 #b8860b);
                color: #2f1b14;
                padding: 12px 8px;
                border: 1px solid #b8860b;
                border-radius: 4px;
                font-weight: 600;
                font-size: 16px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #f0e68c, stop:1 #daa520);
            }
            QScrollBar:vertical {
                border: 2px solid #daa520;
                background: #f5f5dc;
                width: 16px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #daa520, stop:1 #b8860b);
                min-height: 20px;
                border-radius: 6px;
                border: 1px solid #b8860b;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #f0e68c, stop:1 #daa520);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # 加载图表数据
        self.load_diagrams()
        self.init_table()
        self.populate_table()
        
        # 连接事件
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # 初始化排序状态
        self.sort_orders = {0: None, 1: None, 2: None, 3: None}  # 各列的排序状态

    def load_diagrams(self, topic_id=None):
        """从数据库加载图表"""
        self.current_diagrams = self.db_manager.get_tree_diagrams(topic_id)

    def filter_diagrams(self):
        """根据选择的专题筛选图表"""
        selected_index = self.filter_combo.currentIndex()
        topic_id = self.filter_combo.itemData(selected_index)
        
        if topic_id:
            # 启用删除主题按钮（当选择了具体主题时）
            self.delete_topic_btn.setEnabled(True)
        else:
            # 禁用删除主题按钮（当选择"全部"时）
            self.delete_topic_btn.setEnabled(False)
        
        self.load_diagrams(topic_id)
        self.update_table()

    def update_table(self):
        """更新表格视图"""
        self.init_table()
        self.populate_table()
        
        # 默认选中第一行并触发预览效果
        if len(self.current_diagrams) > 0:
            self.table.selectRow(0)
            # 使用QTimer延迟执行预览，确保界面完全加载后再触发
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.preview_diagram(0))
    
    def init_table(self):
        """初始化表格"""
        self.table.setRowCount(len(self.current_diagrams))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["名称", "专题", "创建时间", "操作"])
        
        # 设置列宽
        self.table.setColumnWidth(0, 200)  # 名称列
        self.table.setColumnWidth(1, 150)  # 专题列
        self.table.setColumnWidth(2, 200)  # 创建时间列
        self.table.setColumnWidth(3, 200)  # 操作列
        
        # 启用交替行颜色
        self.table.setAlternatingRowColors(True)
    
    def populate_table(self):
        """填充表格数据"""
        for i, diagram in enumerate(self.current_diagrams):
            # 名称
            name_item = QTableWidgetItem(diagram['name'])
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setData(Qt.UserRole, i)  # 存储行索引用于预览
            # 设置古朴纸书感字体颜色和背景色
            name_item.setForeground(QColor("#8B4513"))  # 深棕色，古朴感
            # 确保背景为亮色
            if i % 2 == 0:
                name_item.setBackground(QColor("#f5f5dc"))
            else:
                name_item.setBackground(QColor("#faf0e6"))
            self.table.setItem(i, 0, name_item)
            
            # 专题
            topic_item = QTableWidgetItem(diagram['topic_name'])
            topic_item.setTextAlignment(Qt.AlignCenter)
            # 设置古朴纸书感字体颜色和背景色
            topic_item.setForeground(QColor("#8B4513"))  # 深棕色，古朴感
            # 确保背景为亮色
            if i % 2 == 0:
                topic_item.setBackground(QColor("#f5f5dc"))
            else:
                topic_item.setBackground(QColor("#faf0e6"))
            self.table.setItem(i, 1, topic_item)
            
            # 创建时间 - 格式化为月-日-时-分/年
            created_at = diagram['created_at']
            try:
                # 解析数据库中的时间格式
                from datetime import datetime
                dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                # 格式化为月-日 时:分/年
                formatted_time = f"{dt.month:02d}-{dt.day:02d} {dt.hour:02d}:{dt.minute:02d}/{dt.year}"
            except:
                # 如果解析失败，使用原始格式
                formatted_time = created_at
            
            created_item = QTableWidgetItem(formatted_time)
            created_item.setTextAlignment(Qt.AlignCenter)
            # 设置古朴纸书感字体颜色和背景色
            created_item.setForeground(QColor("#8B4513"))  # 深棕色，古朴感
            # 确保背景为亮色
            if i % 2 == 0:
                created_item.setBackground(QColor("#f5f5dc"))
            else:
                created_item.setBackground(QColor("#faf0e6"))
            self.table.setItem(i, 2, created_item)
            
            # 操作列 - 现代化按钮设计
            btn_widget = QWidget()
            # 确保操作列背景为亮色
            if i % 2 == 0:
                btn_widget.setStyleSheet("background-color: #f5f5dc;")
            else:
                btn_widget.setStyleSheet("background-color: #faf0e6;")
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(15, 15, 15, 15)  # 增加边距提升视觉效果
            btn_layout.setSpacing(15)  # 增加按钮间距
            btn_layout.setAlignment(Qt.AlignCenter)  # 水平居中对齐
            
            # 查看按钮 - 古朴纸书感设计
            view_btn = QPushButton("查看")
            view_btn.setFixedSize(80, 45)  # 增大按钮尺寸提升可点击性
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #3c2e26;
                    border: 2px solid #b8860b;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #deb887;
                    border-color: #daa520;
                }
                QPushButton:pressed {
                    background-color: #cd853f;
                    border-color: #a0522d;
                }
            """)
            view_btn.clicked.connect(lambda checked, row=i: self.preview_diagram(row))
            btn_layout.addWidget(view_btn)
            
            # 删除按钮 - 古朴纸书感设计
            delete_btn = QPushButton("删除")
            delete_btn.setFixedSize(80, 45)  # 与查看按钮保持一致的尺寸
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #2f1b14;
                    border: 2px solid #a0522d;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #d2b48c;
                    border-color: #8b4513;
                }
                QPushButton:pressed {
                    background-color: #bc9a6a;
                    border-color: #654321;
                }
            """)
            delete_btn.clicked.connect(lambda checked, row=i: self.delete_diagram(row))
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(i, 3, btn_widget)
    
    def on_cell_clicked(self, row, column):
        """处理单元格点击事件"""
        # 移除单击预览功能，只通过查看按钮触发预览
        pass
    
    def on_header_clicked(self, logical_index):
        """处理表头点击事件"""
        if logical_index == 0:  # 名称列不响应
            return
            
        # 切换排序状态
        current_order = self.sort_orders[logical_index]
        if current_order is None or current_order == 'desc':
            self.sort_orders[logical_index] = 'asc'
            reverse = False
        else:
            self.sort_orders[logical_index] = 'desc'
            reverse = True
            
        # 重置其他列的排序状态
        for i in self.sort_orders:
            if i != logical_index:
                self.sort_orders[i] = None
        
        # 执行排序
        if logical_index == 1:  # 专题列
            self.current_diagrams.sort(key=lambda x: x['topic_name'], reverse=reverse)
        elif logical_index == 2:  # 创建时间列
            self.current_diagrams.sort(key=lambda x: x['created_at'], reverse=reverse)
            
        self.update_table()
    
    def preview_diagram(self, index):
        """预览树枝图"""
        if 0 <= index < len(self.current_diagrams):
            diagram = self.current_diagrams[index]
            dialog = PreviewDialog(self, diagram, self.current_diagrams)
            dialog.exec_()
    
    def on_cell_double_clicked(self, row, column):
        """双击编辑功能"""
        if row >= len(self.current_diagrams):
            return
            
        diagram = self.current_diagrams[row]
        
        if column == 0:  # 名称列
            self.edit_diagram_name(row, diagram)
        elif column == 1:  # 专题列
            self.edit_diagram_topic(row, diagram)
    
    def edit_diagram_name(self, row, diagram):
        """编辑图表名称"""
        from PyQt5.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(self, "编辑名称", "请输入新的名称:", text=diagram['name'])
        if ok and new_name.strip() and new_name.strip() != diagram['name']:
            try:
                self.db_manager.update_diagram_name(diagram['id'], new_name.strip())
                diagram['name'] = new_name.strip()
                self.table.item(row, 0).setText(new_name.strip())
                QMessageBox.information(self, "成功", "名称修改成功！")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
    
    def edit_diagram_topic(self, row, diagram):
        """编辑图表专题"""
        from PyQt5.QtWidgets import QInputDialog
        
        # 获取所有专题
        topics = self.db_manager.get_topics()
        topic_names = ["未分类"] + [topic['name'] for topic in topics] + ["+ 新建专题"]
        topic_ids = [None] + [topic['id'] for topic in topics] + ["new"]
        
        # 获取当前专题名称
        current_topic = "未分类"
        if diagram.get('topic_id'):
            for topic in topics:
                if topic['id'] == diagram['topic_id']:
                    current_topic = topic['name']
                    break
        
        current_index = topic_names.index(current_topic) if current_topic in topic_names else 0
        
        new_topic, ok = QInputDialog.getItem(self, "选择专题", "请选择专题:", topic_names, current_index, False)
        if ok and new_topic != current_topic:
            try:
                if new_topic == "+ 新建专题":
                    # 使用TopicDialog创建新专题，保持界面一致性
                    dialog = TopicDialog(self, self.db_manager)
                    if dialog.exec_() == QDialog.Accepted:
                        # 重新获取专题列表，找到新创建的专题
                        updated_topics = self.db_manager.get_topics()
                        if len(updated_topics) > len(topics):
                            # 找到新创建的专题（最后一个）
                            new_topic_data = updated_topics[-1]
                            self.db_manager.update_diagram_topic(diagram['id'], new_topic_data['id'])
                            diagram['topic_id'] = new_topic_data['id']
                            self.table.item(row, 1).setText(new_topic_data['name'])
                            QMessageBox.information(self, "成功", "专题创建并修改成功！")
                else:
                    # 选择现有专题
                    new_topic_id = topic_ids[topic_names.index(new_topic)]
                    self.db_manager.update_diagram_topic(diagram['id'], new_topic_id)
                    diagram['topic_id'] = new_topic_id
                    self.table.item(row, 1).setText(new_topic)
                    QMessageBox.information(self, "成功", "专题修改成功！")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"修改失败：{str(e)}")
    
    def delete_diagram(self, row):
        """删除图表"""
        if row >= len(self.current_diagrams):
            return
            
        diagram = self.current_diagrams[row]
        
        # 检查是否需要确认
        need_confirm = True
        if self.delete_confirm_disabled and self.delete_confirm_disable_time:
            import time
            # 检查是否在1小时内
            if time.time() - self.delete_confirm_disable_time < 3600:  # 3600秒 = 1小时
                need_confirm = False
            else:
                self.delete_confirm_disabled = False
                self.delete_confirm_disable_time = None
        
        if need_confirm:
            from PyQt5.QtWidgets import QCheckBox
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("确认删除")
            msg_box.setText(f"确定要删除树枝图 '{diagram['name']}' 吗？")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            
            # 添加复选框
            checkbox = QCheckBox("1小时内不再提醒")
            msg_box.setCheckBox(checkbox)
            
            result = msg_box.exec_()
            
            if result != QMessageBox.Yes:
                return
                
            # 处理复选框状态
            if checkbox.isChecked():
                import time
                self.delete_confirm_disabled = True
                self.delete_confirm_disable_time = time.time()
        
        # 执行删除
        try:
            self.db_manager.delete_diagram(diagram['id'])
            self.current_diagrams.remove(diagram)
            self.update_table()
            QMessageBox.information(self, "成功", "删除成功！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"删除失败：{str(e)}")
    

    

    
    def delete_current_topic(self):
        """删除当前选中的主题"""
        current_topic_id = self.filter_combo.currentData()
        if not current_topic_id:
            QMessageBox.warning(self, "警告", "请先选择要删除的主题")
            return
        
        # 获取当前主题名称
        current_topic_name = self.filter_combo.currentText()
        
        # 检查该主题下是否有树枝图
        diagrams_in_topic = self.db_manager.get_tree_diagrams(current_topic_id)
        
        if diagrams_in_topic:
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"主题 '{current_topic_name}' 下还有 {len(diagrams_in_topic)} 个树枝图。\n\n删除主题后，这些树枝图将被移动到'未分类'。\n\n确定要删除此主题吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
        else:
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除主题 '{current_topic_name}' 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除主题（数据库会自动将相关图表的topic_id设为NULL）
                self.db_manager.delete_topic(current_topic_id)
                
                # 重新加载筛选下拉框
                self.reload_filter_combo()
                
                # 重新加载图表数据
                self.load_diagrams()
                
                QMessageBox.information(self, "成功", f"主题 '{current_topic_name}' 删除成功！")
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除主题失败：{str(e)}")
    
    def reload_filter_combo(self):
        """重新加载筛选下拉框"""
        current_selection = self.filter_combo.currentData()
        self.filter_combo.clear()
        self.filter_combo.addItem("全部", None)
        
        topics = self.db_manager.get_topics()
        for topic in topics:
            self.filter_combo.addItem(topic['name'], topic['id'])
        
        # 如果之前选择的主题还存在，保持选择；否则选择"全部"
        if current_selection:
            index = self.filter_combo.findData(current_selection)
            if index >= 0:
                self.filter_combo.setCurrentIndex(index)
            else:
                self.filter_combo.setCurrentIndex(0)  # 选择"全部"
        else:
            self.filter_combo.setCurrentIndex(0)  # 选择"全部"
    

    

    


class YMTreeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.settings = QSettings("YMTree", "YMTreeGenerator")
        self.setWindowTitle("义脉树枝图生成器")
        self.setGeometry(100, 100, 1200, 800)
        self.initUI()
        self.load_settings()
        
    def initUI(self):
        # 应用默认主题
        self.setStyleSheet(get_theme_style("classic"))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 创建顶部工具栏
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 添加主题选择到工具栏
        theme_label = QLabel("主题模式：")
        toolbar.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedWidth(150)
        
        # 添加主题选项
        themes = get_theme_list()
        for theme_tuple in themes:
            theme_name, theme_key = theme_tuple
            self.theme_combo.addItem(theme_name, theme_key)
        
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        toolbar.addWidget(self.theme_combo)
        toolbar.addSeparator()
        
        # 添加字号调整到工具栏
        font_label = QLabel("字号大小：")
        toolbar.addWidget(font_label)
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.setFixedWidth(80)
        
        # 添加字号选项
        font_sizes = [18, 20, 22, 24, 26, 28, 30]
        for size in font_sizes:
            self.font_size_combo.addItem(f"{size}px", size)
        
        # 默认选择20px
        default_index = self.font_size_combo.findData(20)
        if default_index >= 0:
            self.font_size_combo.setCurrentIndex(default_index)
        
        self.font_size_combo.currentIndexChanged.connect(self.change_font_size)
        toolbar.addWidget(self.font_size_combo)
        toolbar.addSeparator()
        
        # 添加检查更新按钮到工具栏
        update_btn = QPushButton("检查更新")
        update_btn.setFixedWidth(120)
        update_btn.clicked.connect(self.check_for_updates)
        toolbar.addWidget(update_btn)
        
        # 添加状态栏
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 创建主内容区域
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)
        
        # 左侧面板 - 文本输入区
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)
        
        # 添加输入区标题
        input_title = QLabel("内容输入")
        input_title.setObjectName("inputTitle")
        left_layout.addWidget(input_title)
        
        # 添加输入格式说明
        format_label = QLabel("输入格式：第一行为主题，每增加一级目录增加一个短线(-)")
        format_label.setObjectName("formatLabel")
        format_label.setToolTip(
            "1. 第一行表示主题名称，行首无短线。\n"
            "2. 目录每增加一级，行首短线多一条，短线须为半角。\n"
            "3. 允许有空行，自动忽略空行。\n"
            "4. 若无法对齐，请调整字母、数字或标点为全角。\n"
            "5. 若无法对齐，请调整字体为宋体。"
        )
        left_layout.addWidget(format_label)
        
        # 添加文本编辑器
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont("Consolas", 12))  # 使用等宽字体
        self.input_text.setLineWrapMode(QTextEdit.NoWrap)  # 禁用自动换行
        self.input_text.setPlaceholderText("在此输入树状结构内容...")
        left_layout.addWidget(self.input_text)
        
        # 中间按钮区
        center_panel = QWidget()
        center_panel.setObjectName("centerPanel")
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(15, 15, 15, 15)
        center_layout.setSpacing(15)
        center_layout.setAlignment(Qt.AlignCenter)
        
        # 操作区标题
        action_title = QLabel("操作中心")
        action_title.setObjectName("actionTitle")
        action_title.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(action_title)
        
        # 生成按钮
        generate_btn = QPushButton("生成义脉树枝图")
        generate_btn.setObjectName("generateBtn")
        generate_btn.setMinimumHeight(50)
        generate_btn.setMinimumWidth(160)
        generate_btn.clicked.connect(self.generate_tree)
        center_layout.addWidget(generate_btn)
        
        # 复制结果按钮
        copy_btn = QPushButton("复制结果")
        copy_btn.setObjectName("copyBtn")
        copy_btn.setMinimumHeight(45)
        copy_btn.setMinimumWidth(160)
        copy_btn.clicked.connect(self.copy_result)
        center_layout.addWidget(copy_btn)
        
        # 保存结果按钮
        save_btn = QPushButton("保存结果")
        save_btn.setObjectName("saveBtn")
        save_btn.setMinimumHeight(45)
        save_btn.setMinimumWidth(160)
        save_btn.clicked.connect(self.save_result)
        center_layout.addWidget(save_btn)
        
        # 我的树枝图按钮
        history_btn = QPushButton("我的树枝图")
        history_btn.setObjectName("historyBtn")
        history_btn.setMinimumHeight(45)
        history_btn.setMinimumWidth(160)
        history_btn.clicked.connect(self.show_history)
        center_layout.addWidget(history_btn)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #4a4a4a;")
        center_layout.addWidget(separator)
        
        # 清空按钮
        clear_btn = QPushButton("清空内容")
        clear_btn.setObjectName("clearBtn")
        clear_btn.setMinimumHeight(40)
        clear_btn.setMinimumWidth(160)
        clear_btn.clicked.connect(self.clear_all)
        center_layout.addWidget(clear_btn)
        
        # 右侧面板 - 预览区
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)
        
        # 预览区标题
        preview_title = QLabel("预览结果")
        preview_title.setObjectName("previewTitle")
        right_layout.addWidget(preview_title)
        

        
        # 预览文本区
        self.preview_text = QTextEdit()
        self.preview_text.setFont(QFont("NSimSun", 10))  # 使用等宽字体
        self.preview_text.setReadOnly(False)  # 设为可编辑
        self.preview_text.setPlaceholderText("生成的树状图将在这里显示，您也可以直接编辑调整...")
        right_layout.addWidget(self.preview_text)
        
        # 使用QSplitter实现可调节大小的面板
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        
        # 设置初始比例 (40%, 10%, 50%)
        main_splitter.setSizes([400, 100, 500])
        
        # 设置最小宽度
        left_panel.setMinimumWidth(200)
        center_panel.setMinimumWidth(150)
        right_panel.setMinimumWidth(200)
        
        # 设置拉伸因子
        main_splitter.setStretchFactor(0, 4)  # 左侧面板
        main_splitter.setStretchFactor(1, 1)  # 中间面板
        main_splitter.setStretchFactor(2, 5)  # 右侧面板
        
        # 保存splitter引用以便后续保存状态
        self.main_splitter = main_splitter
        
        content_layout.addWidget(main_splitter)
        
        main_layout.addWidget(content_widget, 1)  # 设置拉伸因子为1，使其占据大部分空间
        
        # 添加惟海法师开示到底部中间
        wisdom_label = QLabel("知识树是活的，要在人生中生长")
        wisdom_label.setObjectName("wisdomLabel")
        wisdom_font = QFont("华文行楷", 24)
        wisdom_font.setBold(True)
        wisdom_label.setFont(wisdom_font)
        wisdom_label.setAlignment(Qt.AlignCenter)
        wisdom_label.setStyleSheet("margin: 10px 0; padding: 10px;")
        main_layout.addWidget(wisdom_label)
        
        # 应用默认样式
        # self.theme_combo.setCurrentIndex(0)  # 默认使用第一个主题

    def change_theme(self, index=None):
        """切换主题"""
        theme_data = self.theme_combo.currentData()
        font_size = self.font_size_combo.currentData() if hasattr(self, 'font_size_combo') else 13
        
        # 应用选中的主题
        theme_style = get_theme_style(theme_data, font_size)
        self.setStyleSheet(theme_style)
        
        # 保存主题设置（仅在用户手动切换时保存）
        if index is not None:
            self.save_settings()
    
    def change_font_size(self, index):
        """改变字号大小"""
        # 重新应用当前主题以更新字号
        self.change_theme()
        # 保存字号设置
        self.save_settings()
    
    def load_settings(self):
        """加载用户设置"""
        # 加载主题设置
        theme = self.settings.value("theme", "classic")
        theme_index = self.theme_combo.findData(theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        else:
            self.theme_combo.setCurrentIndex(0)  # 默认选择第一个主题
        
        # 加载字号设置
        font_size = int(self.settings.value("font_size", 13))
        font_index = self.font_size_combo.findData(font_size)
        if font_index >= 0:
            self.font_size_combo.setCurrentIndex(font_index)
        
        # 加载窗口大小和位置
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # 恢复分割器状态
        if hasattr(self, 'main_splitter'):
            splitter_state = self.settings.value("splitter_state")
            if splitter_state:
                self.main_splitter.restoreState(splitter_state)
            else:
                # 如果没有保存的状态，使用默认大小
                splitter_sizes = self.settings.value("splitter_sizes")
                if splitter_sizes:
                    # 转换为整数列表
                    sizes = [int(size) for size in splitter_sizes]
                    self.main_splitter.setSizes(sizes)
        
        # 应用设置
        self.change_theme()
    
    def save_settings(self):
        """保存用户设置"""
        # 保存主题设置
        theme_data = self.theme_combo.currentData()
        self.settings.setValue("theme", theme_data)
        
        # 保存字号设置
        font_size = self.font_size_combo.currentData()
        self.settings.setValue("font_size", font_size)
        
        # 保存窗口大小和位置
        self.settings.setValue("geometry", self.saveGeometry())
        
        # 保存分割器状态
        if hasattr(self, 'main_splitter'):
            self.settings.setValue("splitter_state", self.main_splitter.saveState())
            self.settings.setValue("splitter_sizes", self.main_splitter.sizes())
    
    def closeEvent(self, event):
        """窗口关闭时保存设置"""
        self.save_settings()
        event.accept()
    def clear_all(self):
        self.input_text.clear()
        self.preview_text.clear()

    def copy_result(self):
        result_text = self.preview_text.toPlainText()
        if result_text.strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(result_text)
    


    def generate_tree(self):
        input_text = self.input_text.toPlainText()
        if not input_text.strip():
            self.preview_text.clear()
            return

        try:
            lines = [line for line in input_text.split('\n') if line.strip()]
            if not lines:
                self.preview_text.setPlainText("")
                return

            root_nodes = self._parse_to_tree(lines)

            final_output = []
            for root in root_nodes:
                grid, max_x, max_y = self._draw_tree_to_grid(root)
                tree_str = "\n".join([''.join(row[:max_x]).rstrip() for row in grid[:max_y]])
                final_output.append(tree_str)

            # 直接显示结果
            self.preview_text.setPlainText("\n\n".join(final_output))
            self.statusBar().showMessage("义脉树枝图已生成！", 5000)

        except Exception as e:
            import traceback
            self.preview_text.setText(f"生成失败：\n{traceback.format_exc()}")
            self.statusBar().showMessage("生成过程中出现错误", 5000)

    def _get_display_width(self, s):
        """计算字符串的显示宽度，考虑中英文字符的实际显示宽度"""
        width = 0
        for char in s:
            # 中文字符、全角符号等宽字符
            if ('\u4e00' <= char <= '\u9fff' or  # 中日韩统一表意文字
                '\u3000' <= char <= '\u303f' or  # 中日韩符号和标点
                '\uff00' <= char <= '\uffef' or  # 全角ASCII、全角标点
                '\u2e80' <= char <= '\u2eff' or  # 中日韩部首补充
                '\u2f00' <= char <= '\u2fdf' or  # 康熙部首
                '\u3040' <= char <= '\u309f' or  # 平假名
                '\u30a0' <= char <= '\u30ff'):   # 片假名
                width += 2
            else:
                # 英文字符、数字、半角符号
                width += 1
        return width

    def _parse_to_tree(self, lines):
        class Node:
            def __init__(self, text, depth, get_width_func):
                self.text = text
                self.depth = depth
                self.children = []
                self.parent = None
                self.x = 0
                self.y = 0
                self.width = get_width_func(text)
                self.subtree_height = 0
                self.abs_y = 0

        root_nodes = []
        parent_stack = []

        for line in lines:
            # 跳过空行
            if not line.strip():
                continue

            # 计算深度
            stripped_line = line.lstrip('-')
            depth = len(line) - len(stripped_line)
            text = stripped_line.strip()

            # 跳过空文本
            if not text:
                continue

            # 创建节点
            node = Node(text, depth, self._get_display_width)

            if not parent_stack:
                root_nodes.append(node)
                parent_stack.append(node)
                continue

            # 调整父节点栈
            while parent_stack and parent_stack[-1].depth >= depth:
                parent_stack.pop()

            if parent_stack:
                parent = parent_stack[-1]
                parent.children.append(node)
                node.parent = parent
            else:
                root_nodes.append(node)
            
            parent_stack.append(node)
        
        return root_nodes

    def _draw_tree_to_grid(self, root):
        # 1. 计算每个节点的位置
        self._layout_tree(root)
        
        # 2. 确定网格尺寸
        max_x, max_y = self._get_grid_size(root)
        
        # 创建网格，使用全角空格作为默认字符
        grid = [['　'] * (max_x + 20) for _ in range(max_y + 10)]

        # 3. 在网格上绘制树
        self._draw_on_grid(root, grid)

        return grid, max_x + 20, max_y + 10

    def _layout_tree(self, node, x=0, y=0):
        """计算树状图的布局位置 - 按照正确的义脉树枝图格式"""
        node.x = x
        node.y = y
        
        if not node.children:
            return
        
        if len(node.children) == 1:
            # 单个子节点，水平排列在同一行
            child = node.children[0]
            child_x = x + self._get_display_width(node.text) + 1
            self._layout_tree(child, child_x, y)
        elif len(node.children) == 2:
            # 两个子节点：第一个在上方，第二个在下方
            child_x = x + self._get_display_width(node.text) + 1
            self._layout_tree(node.children[0], child_x, y - 1)
            self._layout_tree(node.children[1], child_x, y + 1)
        else:
            # 多个子节点：第一个在上方，其余依次向下，中间有垂直连接线
            child_x = x + self._get_display_width(node.text) + 1
            self._layout_tree(node.children[0], child_x, y - 1)
            for i in range(1, len(node.children)):
                self._layout_tree(node.children[i], child_x, y + i)

    def _get_grid_size(self, node):
        """计算网格尺寸"""
        max_x = 0
        max_y = 0
        min_y = 0
        
        def traverse(n):
            nonlocal max_x, max_y, min_y
            max_x = max(max_x, n.x + self._get_display_width(n.text))
            max_y = max(max_y, n.y)
            min_y = min(min_y, n.y)
            for child in n.children:
                traverse(child)
        
        traverse(node)
        
        # 调整所有节点的y坐标，确保最小y为0
        if min_y < 0:
            def shift_y(n, offset):
                n.y += offset
                for child in n.children:
                    shift_y(child, offset)
            shift_y(node, -min_y)
            max_y += -min_y
        
        return max_x, max_y

    def _draw_on_grid(self, node, grid):
        """按照正确的义脉树枝图格式绘制树状图"""
        # 绘制节点文本
        if 0 <= node.y < len(grid):
            for i, char in enumerate(node.text):
                if node.x + i < len(grid[0]):
                    grid[node.y][node.x + i] = char

        # 绘制到子节点的连接线
        if node.children:
            text_width = self._get_display_width(node.text)
            connect_x = node.x + text_width
            
            if len(node.children) == 1:
                # 单个子节点，水平连接，使用─
                if 0 <= node.y < len(grid) and connect_x < len(grid[0]):
                    grid[node.y][connect_x] = '─'
            elif len(node.children) == 2:
                # 两个子节点的情况
                if 0 <= node.y < len(grid) and connect_x < len(grid[0]):
                    grid[node.y][connect_x] = '┤'
                
                # 绘制子节点的分支符号
                for i, child in enumerate(node.children):
                    if 0 <= child.y < len(grid) and connect_x < len(grid[0]):
                        if i == 0:
                            grid[child.y][connect_x] = '┌'  # 上方子节点
                        else:
                            grid[child.y][connect_x] = '└'  # 下方子节点
            else:
                # 多个子节点的情况
                child_ys = [child.y for child in node.children]
                min_y = min(child_ys)
                max_y = max(child_ys)
                
                # 在父节点位置绘制分支起点
                if 0 <= node.y < len(grid) and connect_x < len(grid[0]):
                    grid[node.y][connect_x] = '┤'
                
                # 绘制垂直连接线和子节点分支符号
                for y in range(min_y, max_y + 1):
                    if 0 <= y < len(grid) and connect_x < len(grid[0]) and y != node.y:
                        if y in child_ys:
                            # 子节点位置的分支符号
                            child_index = child_ys.index(y)
                            if child_index == 0:
                                grid[y][connect_x] = '┌'  # 第一个子节点
                            elif child_index == len(node.children) - 1:
                                grid[y][connect_x] = '└'  # 最后一个子节点
                            else:
                                grid[y][connect_x] = '├'  # 中间子节点
                        else:
                            # 中间的垂直连接线
                            grid[y][connect_x] = '│'
            
            # 递归绘制子节点
            for child in node.children:
                self._draw_on_grid(child, grid)

    def copy_result(self):
        result_text = self.preview_text.toPlainText()
        if result_text.strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(result_text)
            QMessageBox.information(self, "提示", "结果已复制到剪贴板！")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容，请先生成树状图！")
            
    def save_result(self):
        """保存生成的树状图"""
        result_text = self.preview_text.toPlainText()
        if not result_text.strip():
            QMessageBox.warning(self, "警告", "没有可保存的内容，请先生成树状图！")
            return
        
        dialog = SaveDialog(self, self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            save_data = dialog.get_save_data()
            name = save_data['name']
            topic_id = save_data['topic_id']
            
            if not name:
                QMessageBox.warning(self, "警告", "请输入图表名称！")
                return
            
            try:
                input_content = self.input_text.toPlainText()
                self.db_manager.save_tree_diagram(name, topic_id, input_content, result_text)
                QMessageBox.information(self, "成功", "树状图保存成功！")
                self.statusBar().showMessage(f"已保存: {name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")
    
    def show_history(self):
        """显示我的树枝图"""
        dialog = HistoryDialog(self, self.db_manager)
        dialog.exec_()
    
    def check_for_updates(self):
        """检查更新"""
        try:
            import json
            from PyQt5.QtWidgets import QProgressDialog
            
            # 显示检查进度
            progress = QProgressDialog("正在检查更新...", "取消", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # 读取本地版本信息
            try:
                with open('version.json', 'r', encoding='utf-8') as f:
                    local_version = json.load(f)
            except FileNotFoundError:
                QMessageBox.warning(self, "警告", "未找到版本信息文件")
                progress.close()
                return
            
            # 检查GitHub仓库配置
            if local_version.get('github_repo') == 'your-username/YMTreeGenerator':
                progress.close()
                self.show_setup_github_dialog(local_version)
                return
            
            # 尝试检查GitHub最新版本
            try:
                import requests
                repo_url = f"https://api.github.com/repos/{local_version['github_repo']}/releases/latest"
                
                # 配置SSL和连接设置以避免连接错误
                import ssl
                import urllib3
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry
                
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                # 创建一个session来处理SSL配置和重试机制
                session = requests.Session()
                
                # 配置重试策略
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                
                # 创建适配器
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                # 设置请求头和SSL配置
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                session.verify = False  # 临时禁用SSL验证以避免连接问题
                
                response = session.get(repo_url, timeout=30)
                progress.close()
                
                if response.status_code == 200:
                    latest_release = response.json()
                    latest_version = latest_release['tag_name'].lstrip('v')
                    current_version = local_version['version']
                    
                    if self.compare_versions(latest_version, current_version) > 0:
                        # 有新版本
                        self.show_update_dialog(latest_release, local_version)
                    else:
                        QMessageBox.information(self, "检查更新", "当前已是最新版本！")
                elif response.status_code == 404:
                    progress.close()
                    QMessageBox.information(self, "提示", "该仓库暂未发布任何版本\n\n这可能是因为：\n1. 仓库作者还未创建release版本\n2. 这是一个新建的仓库\n\n当前版本：" + local_version['version'])
                else:
                    progress.close()
                    QMessageBox.warning(self, "错误", f"GitHub服务器返回错误：{response.status_code}")
                    
            except ImportError:
                progress.close()
                QMessageBox.warning(self, "错误", "缺少requests库，无法检查更新\n请安装requests库：pip install requests")
            except Exception as e:
                progress.close()
                QMessageBox.warning(self, "网络错误", f"检查更新失败：{str(e)}\n\n可能的原因：\n1. 网络连接问题\n2. GitHub API访问限制\n3. 防火墙阻止访问")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"检查更新时发生未知错误：{str(e)}")
    
    def show_setup_github_dialog(self, local_version):
        """显示GitHub配置指导对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit
        import webbrowser
        
        dialog = QDialog(self)
        dialog.setWindowTitle("配置GitHub更新源")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 说明文字
        info_label = QLabel("检测到GitHub仓库配置未完成，请按以下步骤配置：")
        info_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 配置步骤
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setMaximumHeight(300)
        steps_content = """
1. 在GitHub上创建新仓库（如：YMTreeGenerator）

2. 上传项目源码到仓库

3. 创建Release版本：
   - 点击仓库页面的"Releases"
   - 点击"Create a new release"
   - 设置Tag版本号（如：v1.0.0）
   - 上传打包好的exe文件
   - 发布Release

4. 修改version.json文件中的github_repo字段：
   将"your-username/YMTreeGenerator"替换为实际的仓库路径
   例如："zhangsan/YMTreeGenerator"

5. 重新打包程序并分发

注意：需要安装requests库才能使用更新检查功能
命令：pip install requests
        """
        steps_text.setPlainText(steps_content)
        layout.addWidget(steps_text)
        
        # GitHub仓库输入
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("GitHub仓库路径："))
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("例如：username/YMTreeGenerator")
        repo_layout.addWidget(self.repo_input)
        layout.addLayout(repo_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(lambda: self.save_github_config(dialog))
        button_layout.addWidget(save_btn)
        
        github_btn = QPushButton("打开GitHub")
        github_btn.clicked.connect(lambda: webbrowser.open("https://github.com"))
        button_layout.addWidget(github_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def save_github_config(self, dialog):
        """保存GitHub配置"""
        import json
        
        repo_path = self.repo_input.text().strip()
        if not repo_path:
            QMessageBox.warning(dialog, "错误", "请输入GitHub仓库路径")
            return
        
        if '/' not in repo_path:
            QMessageBox.warning(dialog, "错误", "仓库路径格式错误，应为：username/repository")
            return
        
        try:
            # 读取当前配置
            with open('version.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新配置
            config['github_repo'] = repo_path
            config['download_url'] = f"https://github.com/{repo_path}/releases/latest"
            
            # 保存配置
            with open('version.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(dialog, "成功", "GitHub配置已保存！\n\n请重新打包程序以应用更改。")
            dialog.accept()
            
        except Exception as e:
            QMessageBox.warning(dialog, "错误", f"保存配置失败：{str(e)}")
    
    def compare_versions(self, version1, version2):
        """比较版本号"""
        def version_tuple(v):
            return tuple(map(int, (v.split("."))))
        
        v1 = version_tuple(version1)
        v2 = version_tuple(version2)
        
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0
    
    def show_update_dialog(self, latest_release, local_version):
        """显示更新对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
        import webbrowser
        
        dialog = QDialog(self)
        dialog.setWindowTitle("发现新版本")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 版本信息
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"当前版本：{local_version['version']}"))
        info_layout.addWidget(QLabel(f"最新版本：{latest_release['tag_name']}"))
        info_layout.addWidget(QLabel(f"发布时间：{latest_release['published_at'][:10]}"))
        layout.addLayout(info_layout)
        
        # 更新说明
        layout.addWidget(QLabel("更新说明："))
        changelog = QTextEdit()
        changelog.setReadOnly(True)
        changelog.setMaximumHeight(200)
        changelog.setPlainText(latest_release.get('body', '暂无更新说明'))
        layout.addWidget(changelog)
        
        # 检查是否有可下载的文件
        assets = latest_release.get("assets", [])
        download_asset = None
        
        # 查找可下载的文件
        for asset in assets:
            if asset.get("name", "").endswith((".zip", ".exe", ".msi")):
                download_asset = asset
                break
        
        # 按钮
        button_layout = QHBoxLayout()
        
        if download_asset:
            # 有可下载文件，提供自动更新选项
            auto_update_btn = QPushButton("自动更新")
            auto_update_btn.clicked.connect(lambda: self.auto_update(download_asset, latest_release['tag_name'], dialog))
            button_layout.addWidget(auto_update_btn)
            
            manual_download_btn = QPushButton("手动下载")
            manual_download_btn.clicked.connect(lambda: self.download_update(latest_release['html_url']))
            button_layout.addWidget(manual_download_btn)
        else:
            # 没有可下载文件，只提供手动下载
            download_btn = QPushButton("前往下载")
            download_btn.clicked.connect(lambda: self.download_update(latest_release['html_url']))
            button_layout.addWidget(download_btn)
        
        later_btn = QPushButton("稍后提醒")
        later_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(later_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def auto_update(self, download_asset, version, parent_dialog):
        """自动更新程序"""
        try:
            import requests
            import os
            from PyQt5.QtWidgets import QProgressDialog
            from PyQt5.QtCore import Qt
            
            download_url = download_asset.get("browser_download_url")
            file_name = download_asset.get("name")
            file_size = download_asset.get("size", 0)
            
            if not download_url:
                QMessageBox.warning(self, "自动更新", "无法获取下载链接，请尝试手动下载。")
                return
            
            parent_dialog.close()
            
            # 创建进度对话框
            progress_dialog = QProgressDialog("正在下载更新...", "取消", 0, 100, self)
            progress_dialog.setWindowTitle("自动更新")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.show()
            
            # 创建临时下载目录
            temp_dir = os.path.join(os.path.dirname(__file__), "temp_update")
            os.makedirs(temp_dir, exist_ok=True)
            
            download_path = os.path.join(temp_dir, file_name)
            
            # 下载文件
            # 配置SSL和连接设置以避免连接错误
            import ssl
            import urllib3
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # 创建一个session来处理SSL配置和重试机制
            session = requests.Session()
            
            # 配置重试策略
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            # 创建适配器
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # 设置请求头和SSL配置
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            session.verify = False  # 临时禁用SSL验证以避免连接问题
            
            response = session.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            downloaded_size = 0
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if progress_dialog.wasCanceled():
                        f.close()
                        os.remove(download_path)
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if file_size > 0:
                            progress = int((downloaded_size / file_size) * 100)
                            progress_dialog.setValue(progress)
                            progress_dialog.setLabelText(f"正在下载更新... {downloaded_size // 1024}KB / {file_size // 1024}KB")
                        
                        QApplication.processEvents()
            
            progress_dialog.close()
            
            # 下载完成，询问是否立即安装
            reply = QMessageBox.question(self, "下载完成", 
                f"更新文件已下载完成！\n\n文件: {file_name}\n版本: {version}\n\n是否立即安装更新？\n\n注意：程序将会关闭并启动安装程序。",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.install_update(download_path, file_name)
            else:
                QMessageBox.information(self, "更新文件已保存", 
                    f"更新文件已保存到：\n{download_path}\n\n您可以稍后手动安装。")
                
        except requests.exceptions.RequestException as e:
            # 网络错误，提供备用方案
            reply = QMessageBox.question(self, "下载失败", 
                f"自动下载失败：\n{str(e)}\n\n是否尝试手动下载？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                # 打开手动下载链接
                download_url = download_asset.get("browser_download_url")
                if download_url:
                    QDesktopServices.openUrl(QUrl(download_url))
                    QMessageBox.information(self, "手动下载", 
                        "已在浏览器中打开下载链接。\n\n下载完成后，请手动安装更新文件。")
        except Exception as e:
            QMessageBox.warning(self, "更新失败", f"自动更新过程中发生错误：\n{str(e)}\n\n建议尝试手动下载更新。")
    
    def install_update(self, file_path, file_name):
        """安装更新"""
        try:
            import subprocess
            import sys
            
            if file_name.endswith('.exe'):
                # 如果是exe文件，直接运行安装程序
                subprocess.Popen([file_path], shell=True)
                QApplication.quit()
            elif file_name.endswith('.zip'):
                # 如果是zip文件，提示用户手动解压
                reply = QMessageBox.question(self, "安装更新", 
                    f"下载的是压缩包文件，需要手动解压安装。\n\n是否打开文件所在位置？",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                
                if reply == QMessageBox.Yes:
                    # 打开文件所在目录
                    import subprocess
                    subprocess.Popen(['explorer', '/select,', file_path.replace('/', '\\')])
            else:
                # 其他文件类型，打开文件所在位置
                import subprocess
                subprocess.Popen(['explorer', '/select,', file_path.replace('/', '\\')])
                
        except Exception as e:
            QMessageBox.warning(self, "安装失败", f"启动安装程序时发生错误：\n{str(e)}")
    
    def download_update(self, download_url):
        """下载更新"""
        import webbrowser
        webbrowser.open(download_url)
        QMessageBox.information(self, "提示", "已在浏览器中打开下载页面，请下载最新版本并手动安装。")

class MarkdownHelpDialog(QDialog):
    """Markdown语法帮助对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Markdown语法帮助")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 帮助内容
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml(self.get_markdown_help_content())
        
        # 设置样式
        help_text.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #faf0e6, stop:1 #f5deb3);
                color: #8B4513;
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        scroll_layout.addWidget(help_text)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #d2b48c, stop:1 #bc9a6a);
                color: #2f1b14;
                border: 2px solid #a0522d;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #deb887, stop:1 #cd853f);
                border-color: #8b4513;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #bc9a6a, stop:1 #a0522d);
                border-color: #654321;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def get_markdown_help_content(self):
        """获取Markdown帮助内容"""
        return """
        <h1 style="color: #8B4513; text-align: center; margin-bottom: 20px;">📝 Markdown语法使用指南</h1>
        
        <div style="background: #f5f5dc; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #a0522d; margin-top: 0;">🎯 支持的语法</h2>
            <p style="color: #8B4513; margin-bottom: 10px;">本编辑器支持以下Markdown语法，输入后会自动渲染为对应格式：</p>
        </div>
        
        <h3 style="color: #a0522d; border-bottom: 2px solid #daa520; padding-bottom: 5px;">📋 标题</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background: #f0e68c;">
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">语法</th>
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">效果</th>
            </tr>
            <tr>
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;"># 一级标题</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><h1 style="margin: 0; color: #8B4513;">一级标题</h1></td>
            </tr>
            <tr style="background: #faf0e6;">
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">## 二级标题</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><h2 style="margin: 0; color: #8B4513;">二级标题</h2></td>
            </tr>
            <tr>
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">### 三级标题</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><h3 style="margin: 0; color: #8B4513;">三级标题</h3></td>
            </tr>
            <tr style="background: #faf0e6;">
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">#### 四级标题</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><h4 style="margin: 0; color: #8B4513;">四级标题</h4></td>
            </tr>
        </table>
        
        <h3 style="color: #a0522d; border-bottom: 2px solid #daa520; padding-bottom: 5px;">✨ 文本格式</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background: #f0e68c;">
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">语法</th>
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">效果</th>
            </tr>
            <tr>
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">**粗体文本**</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><strong>粗体文本</strong></td>
            </tr>
            <tr style="background: #faf0e6;">
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">*斜体文本*</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><em>斜体文本</em></td>
            </tr>
            <tr>
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">`行内代码`</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><code style="background: #f5deb3; padding: 2px 4px; border-radius: 3px;">行内代码</code></td>
            </tr>
        </table>
        
        <h3 style="color: #a0522d; border-bottom: 2px solid #daa520; padding-bottom: 5px;">🔗 链接</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background: #f0e68c;">
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">语法</th>
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">效果</th>
            </tr>
            <tr>
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">[链接文本](https://example.com)</td>
                <td style="border: 1px solid #daa520; padding: 8px;"><a href="https://example.com" style="color: #8b4513;">链接文本</a></td>
            </tr>
        </table>
        
        <h3 style="color: #a0522d; border-bottom: 2px solid #daa520; padding-bottom: 5px;">📝 列表</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background: #f0e68c;">
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">语法</th>
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">效果</th>
            </tr>
            <tr>
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace; vertical-align: top;">- 项目1<br>- 项目2<br>- 项目3</td>
                <td style="border: 1px solid #daa520; padding: 8px;">
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>项目1</li>
                        <li>项目2</li>
                        <li>项目3</li>
                    </ul>
                </td>
            </tr>
            <tr style="background: #faf0e6;">
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace; vertical-align: top;">1. 第一项<br>2. 第二项<br>3. 第三项</td>
                <td style="border: 1px solid #daa520; padding: 8px;">
                    <ol style="margin: 0; padding-left: 20px;">
                        <li>第一项</li>
                        <li>第二项</li>
                        <li>第三项</li>
                    </ol>
                </td>
            </tr>
        </table>
        
        <h3 style="color: #a0522d; border-bottom: 2px solid #daa520; padding-bottom: 5px;">💡 引用</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background: #f0e68c;">
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">语法</th>
                <th style="border: 1px solid #daa520; padding: 8px; color: #2f1b14;">效果</th>
            </tr>
            <tr>
                <td style="border: 1px solid #daa520; padding: 8px; font-family: monospace;">&gt; 这是一段引用文本</td>
                <td style="border: 1px solid #daa520; padding: 8px;">
                    <blockquote style="margin: 0; padding: 10px; background: #f5deb3; border-left: 4px solid #daa520;">
                        这是一段引用文本
                    </blockquote>
                </td>
            </tr>
        </table>
        
        <div style="background: #f0e68c; padding: 15px; border-radius: 8px; border: 2px solid #daa520; margin-top: 20px;">
            <h3 style="color: #2f1b14; margin-top: 0;">🎨 使用技巧</h3>
            <ul style="color: #8B4513; margin-bottom: 0;">
                <li><strong>实时预览：</strong>输入Markdown语法后会自动渲染为对应格式</li>
                <li><strong>混合使用：</strong>可以在同一段文本中混合使用多种语法</li>
                <li><strong>纯文本模式：</strong>如果不使用任何Markdown语法，将显示为普通文本</li>
                <li><strong>自动保存：</strong>编辑内容会自动保存，无需手动操作</li>
            </ul>
        </div>
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YMTreeGenerator()
    window.show()
    sys.exit(app.exec_())