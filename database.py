import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "ymtree.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库，创建必要的表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建专题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建层级表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                level_order INTEGER NOT NULL,
                level_name TEXT NOT NULL,
                level_description TEXT,
                FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE,
                UNIQUE(topic_id, level_order)
            )
        ''')
        
        # 创建树状图表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tree_diagrams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                topic_id INTEGER,
                content TEXT NOT NULL,
                result TEXT NOT NULL,
                color_tag TEXT DEFAULT '#FFFFFF',
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE SET NULL
            )
        ''')
        
        # 检查并添加新字段（用于数据库升级）
        try:
            cursor.execute("ALTER TABLE tree_diagrams ADD COLUMN color_tag TEXT DEFAULT '#FFFFFF'")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE tree_diagrams ADD COLUMN sort_order INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        conn.commit()
        conn.close()
    
    def create_topic(self, name: str, description: str = "") -> int:
        """创建新专题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO topics (name, description) VALUES (?, ?)",
                (name, description)
            )
            topic_id = cursor.lastrowid
            conn.commit()
            return topic_id
        except sqlite3.IntegrityError:
            raise ValueError(f"专题名称 '{name}' 已存在")
        finally:
            conn.close()
    
    def get_topics(self) -> List[Dict]:
        """获取所有专题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, description, created_at FROM topics ORDER BY name")
        topics = []
        for row in cursor.fetchall():
            topics.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return topics
    
    def create_level(self, topic_id: int, level_order: int, level_name: str, level_description: str = "") -> int:
        """为专题创建层级"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO levels (topic_id, level_order, level_name, level_description) VALUES (?, ?, ?, ?)",
                (topic_id, level_order, level_name, level_description)
            )
            level_id = cursor.lastrowid
            conn.commit()
            return level_id
        except sqlite3.IntegrityError:
            raise ValueError(f"层级顺序 {level_order} 在该专题中已存在")
        finally:
            conn.close()
    
    def get_levels_by_topic(self, topic_id: int) -> List[Dict]:
        """获取专题的所有层级"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, level_order, level_name, level_description FROM levels WHERE topic_id = ? ORDER BY level_order",
            (topic_id,)
        )
        levels = []
        for row in cursor.fetchall():
            levels.append({
                'id': row[0],
                'level_order': row[1],
                'level_name': row[2],
                'level_description': row[3]
            })
        
        conn.close()
        return levels
    
    def save_tree_diagram(self, name: str, topic_id: Optional[int], content: str, result: str) -> int:
        """保存树状图"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO tree_diagrams (name, topic_id, content, result) VALUES (?, ?, ?, ?)",
            (name, topic_id, content, result)
        )
        diagram_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return diagram_id
    
    def get_tree_diagrams(self, topic_id: Optional[int] = None) -> List[Dict]:
        """获取树状图列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if topic_id:
            cursor.execute(
                """SELECT td.id, td.name, td.content, td.result, td.created_at, td.updated_at, 
                          t.name as topic_name, td.color_tag, td.sort_order
                   FROM tree_diagrams td
                   LEFT JOIN topics t ON td.topic_id = t.id
                   WHERE td.topic_id = ?
                   ORDER BY td.sort_order ASC, td.created_at DESC""",
                (topic_id,)
            )
        else:
            cursor.execute(
                """SELECT td.id, td.name, td.content, td.result, td.created_at, td.updated_at, 
                          t.name as topic_name, td.color_tag, td.sort_order
                   FROM tree_diagrams td
                   LEFT JOIN topics t ON td.topic_id = t.id
                   ORDER BY td.sort_order ASC, td.created_at DESC"""
            )
        
        diagrams = []
        for row in cursor.fetchall():
            diagrams.append({
                'id': row[0],
                'name': row[1],
                'content': row[2],
                'result': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'topic_name': row[6] or "未分类",
                'color_tag': row[7] or '#FFFFFF',
                'sort_order': row[8] or 0
            })
        
        conn.close()
        return diagrams
    
    def delete_tree_diagram(self, diagram_id: int) -> bool:
        """删除树状图"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tree_diagrams WHERE id = ?", (diagram_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def update_tree_diagram(self, diagram_id: int, name: str, content: str, result: str) -> bool:
        """更新树状图"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tree_diagrams SET name = ?, content = ?, result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, content, result, diagram_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def update_diagram_color(self, diagram_id: int, color_tag: str) -> bool:
        """更新树状图颜色标记"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tree_diagrams SET color_tag = ? WHERE id = ?",
            (color_tag, diagram_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def update_diagram_sort_order(self, diagram_id: int, sort_order: int) -> bool:
        """更新树状图排序"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tree_diagrams SET sort_order = ? WHERE id = ?",
            (sort_order, diagram_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def batch_update_sort_orders(self, diagram_orders: List[Tuple[int, int]]) -> bool:
        """批量更新树状图排序"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.executemany(
                "UPDATE tree_diagrams SET sort_order = ? WHERE id = ?",
                [(order, diagram_id) for diagram_id, order in diagram_orders]
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_diagram_content(self, diagram_id: int, content: str, result: str) -> bool:
        """更新图表内容和结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tree_diagrams SET content = ?, result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (content, result, diagram_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def update_diagram_name(self, diagram_id: int, name: str) -> bool:
        """更新图表名称"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tree_diagrams SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, diagram_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def update_diagram_topic(self, diagram_id: int, topic_id: Optional[int]) -> bool:
        """更新图表专题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tree_diagrams SET topic_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (topic_id, diagram_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def delete_diagram(self, diagram_id: int) -> bool:
        """删除图表（别名方法）"""
        return self.delete_tree_diagram(diagram_id)
    
    def delete_topic(self, topic_id: int) -> bool:
        """删除专题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 首先将该专题下的所有图表的topic_id设为NULL（移动到未分类）
            cursor.execute(
                "UPDATE tree_diagrams SET topic_id = NULL WHERE topic_id = ?",
                (topic_id,)
            )
            
            # 删除专题
            cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            return deleted
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()