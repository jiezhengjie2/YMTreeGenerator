import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                             QSplitter, QGroupBox, QMessageBox, QComboBox,
                             QToolBar, QAction, QStatusBar, QFrame, QDialog,
                             QDialogButtonBox, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QTabWidget,
                             QSpinBox, QTextBrowser, QColorDialog)
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from database import DatabaseManager
from src.modern_theme import get_modern_dark_theme, get_light_theme

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
        self.name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; padding: 15px;")
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
        right_layout.addWidget(QLabel("说明内容:"))
        
        self.description_edit = QTextEdit()
        self.description_edit.setFont(QFont("SimSun", 12))
        right_layout.addWidget(self.description_edit)
        
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
            self.description_edit.setPlainText(self.diagram.get('description', ''))
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
            new_description = self.description_edit.toPlainText()
            
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
        
        # 添加删除主题按钮
        self.delete_topic_btn = QPushButton("删除当前主题")
        self.delete_topic_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #FF8C42, stop:1 #E67E22);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 500;
                padding: 6px 12px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #FF9C52, stop:1 #FF8C42);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #E67E22, stop:1 #D35400);
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
        """)
        self.delete_topic_btn.clicked.connect(self.delete_current_topic)
        self.delete_topic_btn.setEnabled(False)  # 默认禁用
        filter_layout.addWidget(self.delete_topic_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["颜色", "名称", "专题", "创建时间", "操作"])
        # 现代化表格布局设计 - 基于UI设计最佳实践
        self.table.horizontalHeader().setStretchLastSection(True)  # 最后一列自适应
        
        # 优化列宽分配 - 基于内容重要性和可读性
        self.table.setColumnWidth(0, 40)   # 颜色列 - 最小化，仅显示颜色指示器
        self.table.setColumnWidth(1, 200)  # 名称列 - 主要内容，给予充足空间
        self.table.setColumnWidth(2, 120)  # 专题列 - 适中宽度
        self.table.setColumnWidth(3, 160)  # 创建时间列 - 确保完整显示时间格式
        # 操作列使用自适应宽度，确保按钮完整显示
        
        # 现代化表格样式设计
        self.table.setAlternatingRowColors(True)  # 交替行颜色提升可读性
        self.table.setShowGrid(False)  # 隐藏网格线，使用更简洁的设计
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        
        # 设置表格头部样式
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setHighlightSections(False)  # 禁用头部高亮
        
        # 优化行高和间距
        self.table.verticalHeader().setDefaultSectionSize(60)  # 增加行高提升可读性和按钮显示效果
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 现代化表格样式 - 基于现代UI设计原则
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8f9fa;
                selection-background-color: #e3f2fd;
                gridline-color: transparent;
                border: 1px solid #e1e5e9;
                border-radius: 12px;
                font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                font-size: 14px;
                outline: none;
            }
            QTableWidget::item {
                padding: 16px 12px;
                border: none;
                color: #1f2937;
                background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QTableWidget::item:hover {
                background-color: #f3f4f6;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #f9fafb, stop:1 #f3f4f6);
                color: #374151;
                padding: 16px 12px;
                border: none;
                border-bottom: 1px solid #e5e7eb;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                           stop:0 #f3f4f6, stop:1 #e5e7eb);
            }
            QHeaderView::section:first {
                border-top-left-radius: 12px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 12px;
            }
            QScrollBar:vertical {
                background-color: #f9fafb;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #d1d5db;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9ca3af;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        # 连接单元格点击事件
        self.table.cellClicked.connect(self.on_cell_clicked)
        # 连接单元格双击事件
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        # 连接表头点击事件
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        layout.addWidget(self.table)
        
        # 初始化排序状态
        self.sort_orders = {0: None, 1: None, 2: None, 3: None, 4: None}  # 各列的排序状态
        
        # 移除右下角关闭按钮
    
    def load_diagrams(self):
        self.current_diagrams = self.db_manager.get_tree_diagrams()
        self.update_table()
    
    def filter_diagrams(self):
        topic_id = self.filter_combo.currentData()
        if topic_id:
            self.current_diagrams = self.db_manager.get_tree_diagrams(topic_id)
            # 启用删除主题按钮（当选择了具体主题时）
            self.delete_topic_btn.setEnabled(True)
        else:
            self.current_diagrams = self.db_manager.get_tree_diagrams()
            # 全部专题时按创建时间排序
            self.current_diagrams.sort(key=lambda x: x['created_at'], reverse=True)
            # 禁用删除主题按钮（当选择"全部"时）
            self.delete_topic_btn.setEnabled(False)
        self.update_table()
    
    def update_table(self):
        self.table.setRowCount(len(self.current_diagrams))
        for i, diagram in enumerate(self.current_diagrams):
            # 颜色标记
            color_item = QTableWidgetItem()
            color = diagram.get('color_tag', '#FFFFFF')
            color_item.setBackground(QColor(color))
            color_item.setToolTip(f"颜色: {color}")
            color_item.setData(Qt.UserRole, diagram['id'])  # 存储diagram id
            self.table.setItem(i, 0, color_item)
            
            # 名称
            name_item = QTableWidgetItem(diagram['name'])
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setData(Qt.UserRole, i)  # 存储行索引用于预览
            self.table.setItem(i, 1, name_item)
            
            # 专题
            topic_item = QTableWidgetItem(diagram['topic_name'])
            topic_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, topic_item)
            
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
            self.table.setItem(i, 3, created_item)
            
            # 操作列 - 现代化按钮设计
            btn_widget = QWidget()
            btn_widget.setStyleSheet("QWidget { background-color: transparent; }")  # 设置透明背景
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(12, 10, 12, 10)  # 增加边距提升视觉效果
            btn_layout.setSpacing(12)  # 增加按钮间距
            
            # 查看按钮 - 现代化设计
            view_btn = QPushButton("查看")
            view_btn.setFixedSize(72, 36)  # 增大按钮尺寸提升可点击性
            view_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                               stop:0 #3b82f6, stop:1 #2563eb);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 4px 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                               stop:0 #60a5fa, stop:1 #3b82f6);
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                               stop:0 #357ABD, stop:1 #2E6BA8);
                }
            """)
            view_btn.clicked.connect(lambda checked, row=i: self.preview_diagram(row))
            btn_layout.addWidget(view_btn)
            
            # 删除按钮 - 现代化设计
            delete_btn = QPushButton("删除")
            delete_btn.setFixedSize(72, 36)  # 与查看按钮保持一致的尺寸
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                               stop:0 #ef4444, stop:1 #dc2626);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 4px 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                               stop:0 #f87171, stop:1 #ef4444);
                    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                               stop:0 #dc2626, stop:1 #b91c1c);
                }
            """)
            delete_btn.clicked.connect(lambda checked, row=i: self.delete_diagram(row))
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(i, 4, btn_widget)
    
    def on_cell_clicked(self, row, column):
        """处理单元格点击事件"""
        if column == 0:  # 颜色列
            self.set_color_for_row(row)
        # 移除单击预览功能，只通过查看按钮触发预览
    
    def on_header_clicked(self, logical_index):
        """处理表头点击事件"""
        if logical_index == 1:  # 名称列不响应
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
        if logical_index == 0:  # 颜色列 - 按颜色值排序
            self.current_diagrams.sort(key=lambda x: x.get('color_tag', '#FFFFFF'), reverse=reverse)
        elif logical_index == 2:  # 专题列
            self.current_diagrams.sort(key=lambda x: x['topic_name'], reverse=reverse)
        elif logical_index == 3:  # 创建时间列
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
        
        if column == 1:  # 名称列
            self.edit_diagram_name(row, diagram)
        elif column == 2:  # 专题列
            self.edit_diagram_topic(row, diagram)
    
    def edit_diagram_name(self, row, diagram):
        """编辑图表名称"""
        from PyQt5.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(self, "编辑名称", "请输入新的名称:", text=diagram['name'])
        if ok and new_name.strip() and new_name.strip() != diagram['name']:
            try:
                self.db_manager.update_diagram_name(diagram['id'], new_name.strip())
                diagram['name'] = new_name.strip()
                self.table.item(row, 1).setText(new_name.strip())
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
                            self.table.item(row, 2).setText(new_topic_data['name'])
                            QMessageBox.information(self, "成功", "专题创建并修改成功！")
                else:
                    # 选择现有专题
                    new_topic_id = topic_ids[topic_names.index(new_topic)]
                    self.db_manager.update_diagram_topic(diagram['id'], new_topic_id)
                    diagram['topic_id'] = new_topic_id
                    self.table.item(row, 2).setText(new_topic)
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
            self.all_diagrams = [d for d in self.all_diagrams if d['id'] != diagram['id']]
            self.update_table()
            QMessageBox.information(self, "成功", "删除成功！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"删除失败：{str(e)}")
    

    
    def set_color_for_row(self, row):
        """为指定行设置颜色"""
        if row >= 0 and row < len(self.current_diagrams):
            diagram = self.current_diagrams[row]
            current_color = QColor(diagram.get('color_tag', '#FFFFFF'))
            
            color = QColorDialog.getColor(current_color, self, "选择颜色")
            if color.isValid():
                try:
                    # 更新数据库
                    self.db_manager.update_diagram_color(diagram['id'], color.name())
                    # 刷新显示
                    self.load_diagrams()
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"设置颜色失败：{str(e)}")
    
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
        # 应用现代深色主题
        self.setStyleSheet(get_modern_dark_theme())
        
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
        
        # 添加现代主题选项
        self.theme_combo.addItem("深色主题", "dark")
        self.theme_combo.addItem("浅色主题", "light")
        
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        toolbar.addWidget(self.theme_combo)
        toolbar.addSeparator()
        
        # 添加字号调整到工具栏
        font_label = QLabel("字号大小：")
        toolbar.addWidget(font_label)
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.setFixedWidth(80)
        
        # 添加字号选项
        font_sizes = [10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24]
        for size in font_sizes:
            self.font_size_combo.addItem(f"{size}px", size)
        
        # 默认选择13px
        default_index = self.font_size_combo.findData(13)
        if default_index >= 0:
            self.font_size_combo.setCurrentIndex(default_index)
        
        self.font_size_combo.currentIndexChanged.connect(self.change_font_size)
        toolbar.addWidget(self.font_size_combo)
        toolbar.addSeparator()
        
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
        input_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 8px;")
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
        action_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 10px;")
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
        preview_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 8px;")
        right_layout.addWidget(preview_title)
        
        # 预览文本区
        self.preview_text = QTextEdit()
        self.preview_text.setFont(QFont("Consolas", 12))  # 使用等宽字体
        self.preview_text.setReadOnly(False)  # 设为可编辑
        self.preview_text.setPlaceholderText("生成的树状图将在这里显示，您也可以直接编辑调整...")
        right_layout.addWidget(self.preview_text)
        
        # 添加面板到内容区域
        content_layout.addWidget(left_panel, 4)  # 比例4
        content_layout.addWidget(center_panel, 1)  # 比例1
        content_layout.addWidget(right_panel, 5)  # 比例5
        
        main_layout.addWidget(content_widget, 1)  # 设置拉伸因子为1，使其占据大部分空间
        
        # 添加惟海法师开示到底部中间
        wisdom_label = QLabel("惟海禅师：知识树是活的，要在人生中生长")
        wisdom_label.setObjectName("wisdomLabel")
        wisdom_font = QFont("华文行楷", 24)
        wisdom_font.setBold(True)
        wisdom_label.setFont(wisdom_font)
        wisdom_label.setAlignment(Qt.AlignCenter)
        wisdom_label.setStyleSheet("margin: 10px 0; padding: 10px;")
        main_layout.addWidget(wisdom_label)
        
        # 应用默认样式
        self.theme_combo.setCurrentIndex(0)  # 默认使用第一个主题

    def change_theme(self, index=None):
        """切换主题"""
        theme_data = self.theme_combo.currentData()
        font_size = self.font_size_combo.currentData() if hasattr(self, 'font_size_combo') else 13
        
        if theme_data == "dark":
            self.setStyleSheet(get_modern_dark_theme(font_size))
        elif theme_data == "light":
            self.setStyleSheet(get_light_theme(font_size))
        
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
        theme = self.settings.value("theme", "dark")
        theme_index = 0 if theme == "dark" else 1
        self.theme_combo.setCurrentIndex(theme_index)
        
        # 加载字号设置
        font_size = int(self.settings.value("font_size", 13))
        font_index = self.font_size_combo.findData(font_size)
        if font_index >= 0:
            self.font_size_combo.setCurrentIndex(font_index)
        
        # 加载窗口大小和位置
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
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

            self.preview_text.setPlainText("\n\n".join(final_output))
            self.preview_text.setFont(QFont("NSimSun", 10))
            self.statusBar().showMessage("义脉树枝图已生成！", 5000)

        except Exception as e:
            import traceback
            self.preview_text.setText(f"生成失败：\n{traceback.format_exc()}")
            self.statusBar().showMessage("生成过程中出现错误", 5000)

    def _get_display_width(self, s):
        return sum(2 if '\u4e00' <= char <= '\u9fff' else 1 for char in s)

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
        """计算树状图的布局位置 - 严格按案例格式布局"""
        node.x = x
        node.y = y
        
        if not node.children:
            return
        
        text_width = self._get_display_width(node.text)
        
        if len(node.children) == 1:
            # 单个子节点，水平排列
            child = node.children[0]
            # 子节点紧跟在连接线后面
            child_x = x + text_width + 1  # 父节点文字后直接连接
            self._layout_tree(child, child_x, y)
        else:
            # 多个子节点，垂直分支
            # 连接符位置：紧贴父节点文字右侧
            connect_x = x + text_width
            # 子节点位置：连接符右侧1个字符位置
            child_x = connect_x + 1
            
            # 计算子节点的垂直分布
            num_children = len(node.children)
            
            # 第一个子节点在父节点上方
            self._layout_tree(node.children[0], child_x, y - 1)
            
            # 其余子节点依次向下排列
            for i in range(1, num_children):
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
        """严格按照案例格式绘制树状图"""
        # 绘制节点文本
        if 0 <= node.y < len(grid):
            for i, char in enumerate(node.text):
                if node.x + i < len(grid[0]):
                    grid[node.y][node.x + i] = char

        # 绘制到子节点的连接线
        if node.children:
            text_width = self._get_display_width(node.text)
            
            if len(node.children) == 1:
                # 单个子节点，水平连接
                child = node.children[0]
                if 0 <= child.y < len(grid):
                    # 绘制水平连接线
                    for x in range(node.x + text_width, child.x):
                        if x < len(grid[0]):
                            grid[child.y][x] = '─'
            else:
                # 多个子节点，垂直分支
                # 连接符位置：紧贴父节点文字右侧
                connect_x = node.x + text_width
                
                # 找到子节点的y坐标范围
                child_ys = [child.y for child in node.children]
                min_y = min(child_ys)
                max_y = max(child_ys)
                
                # 在父节点行绘制分支起点符号
                if 0 <= node.y < len(grid) and connect_x < len(grid[0]):
                    if len(node.children) == 2:
                        grid[node.y][connect_x] = '┤'  # 两个子节点用┤
                    else:
                        grid[node.y][connect_x] = '┼'  # 三个或更多子节点用┼
                
                # 绘制垂直连接线
                for y in range(min_y, max_y + 1):
                    if 0 <= y < len(grid) and connect_x < len(grid[0]) and y != node.y:
                        grid[y][connect_x] = '│'
                
                # 绘制每个子节点的分支符号
                for i, child in enumerate(node.children):
                    if 0 <= child.y < len(grid) and connect_x < len(grid[0]):
                        # 根据位置确定分支符号
                        if i == 0:
                            grid[child.y][connect_x] = '┌'  # 第一个子节点
                        elif i == len(node.children) - 1:
                            grid[child.y][connect_x] = '└'  # 最后一个子节点
                        else:
                            grid[child.y][connect_x] = '├'  # 中间的子节点
            
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YMTreeGenerator()
    window.show()
    sys.exit(app.exec_())