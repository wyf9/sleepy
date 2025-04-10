from dataclasses import dataclass, fields
from datetime import datetime
import sqlite3
from typing import List, Optional, Type, TypeVar, Any, Union, get_type_hints

from flask import g

import env
import utils as u

T = TypeVar('T')

@dataclass
class Event:
    id: int
    device_id: str
    show_name: str
    app_name: str
    using: bool
    start_time: datetime
    
@dataclass
class ColorGroup:
    id: int
    group_name: str
    color_hex: str
    set: int

class ColorGroupIndex:
    '''
    ColorGroup 的工具类, 用于生成索引器, 便于根据id查找颜色, 而非操作数据库
    '''
    def __init__(self, groups: List[ColorGroup]):
        # 构建索引：id -> group_name
        if groups is None:
            self.id_to_name = {}
        else:
            self.id_to_name = {g.id: g.group_name for g in groups}
        # 你也可以加 group -> ColorGroup 或其他索引
        if groups is None:
            self.name_to_obj = {}
        else:
            self.name_to_obj = {g.group_name: g for g in groups}

    def get_group_name_by_id(self, id_: int) -> Optional[str]:
        return self.id_to_name.get(id_)

    def get_group_by_name(self, group_name: str) -> Optional[ColorGroup]:
        return self.name_to_obj.get(group_name)

class AutoORM:
    '''
    基于类型注解的自动ORM系统, 用于sqlite数据库查询
    
    提供更好的类型提示, 便于开发
    '''
    
    db_path: str
    conn: sqlite3.Connection
    # cursor: sqlite3.Cursor
    
    def __init__(self, db_path: str, conn: sqlite3.Connection = None):
        self.db_path = db_path
        if conn is None:
            try:
                self.conn = get_db()
            except Exception as e:
                u.warning('[AutoORM.__init__] ')
        else:
            self.conn = conn
    
    def _auto_mapper_factory(self, model: Type[T]) -> callable:
        """动态生成行转换函数（基于模型类型注解）"""
        type_hints = get_type_hints(model)
        field_types = {f.name: type_hints[f.name] for f in fields(model)}

        def _mapper(cursor: sqlite3.Cursor, row: tuple) -> T:
            # 自动匹配字段名和类型
            row_dict = {
                col[0]: self._convert_type(value, field_types[col[0]])
                for col, value in zip(cursor.description, row)
                if col[0] in field_types
            }
            return model(**row_dict)

        return _mapper
    
    def _convert_type(self, value: Any, target_type: type) -> Any:
        """智能类型转换系统"""
        if value is None:
            return None
        if target_type == bool and isinstance(value, int):
            return bool(value)  # 处理SQLite的0/1转bool
        if target_type == datetime and isinstance(value, str):
            return datetime.fromisoformat(value)  # 自动转换ISO时间字符串
        return target_type(value)

    def query(self, model: Type[T], sql: str, params: tuple = ()) -> List[T]:
        """通用查询方法，返回模型实例列表
        
        Args:
            model(Type[T]): 查询所用表的数据模型
            sql(str): 查询sql
            params(tuple): 查询参数
        """
        # 动态切换行工厂
        original_factory = self.conn.row_factory
        self.conn.row_factory = self._auto_mapper_factory(model)
        
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
        except Exception as e:
            print(f"Err: {e}")
        finally:
            self.conn.row_factory = original_factory

    def close(self):
        self.conn.close()
          
class ColorORM:
    orm: AutoORM
    max_GroupId_value: int
    
    def __init__(self) -> None:
        self.orm = get_orm()
        self.cursor = self.orm.conn.cursor()

    def find_group_id(self, group_name: str) -> str | None:
        """在ColorGroup表中根据组名寻找GroupId，返回字符串，未找到则返回None"""
        self.cursor.execute("SELECT id FROM ColorGroup WHERE group_name = ?", (group_name,))
        result = self.cursor.fetchone()
        return str(result[0]) if result else None

    def find_group_color(self, group_name: str) -> str | None:
        """在ColorGroup表中根据组名寻找ColorHex，返回字符串，未找到则返回None"""
        self.cursor.execute("SELECT color_hex FROM ColorGroup WHERE group_name = ?", (group_name,))
        result = self.cursor.fetchone()
        return str(result[0]) if result else None

    def append_row(self, row: Union[list, dict]):
        """向 ColorGroup 表中添加一行数据"""
        if isinstance(row, dict):
            keys = ', '.join(row.keys())
            placeholders = ', '.join(['?'] * len(row))
            values = tuple(row.values())
            sql = f"INSERT INTO ColorGroup ({keys}) VALUES ({placeholders})"
            self.cursor.execute(sql, values)
        elif isinstance(row, list):
            # 留置
            u.warning('[ColorORM] TypeError: Expected a dict, not a list.')
        else:
            u.warning(f'[ColorORM] Expected "row" to be a dict, but got {type(row).__name__}.')

        self.orm.conn.commit()

    def find_matching_color_groups(self, events: tuple[Event]) -> list[ColorGroup]:
        """给定一批 Event 数据类实例，从 ColorGroup 表中找出存在匹配 group_name 的记录"""

        # 提取去重的 group_name（排除 None）
        group_names = list({e.app_name for e in events if hasattr(e, 'app_name') and e.app_name})

        if not group_names:
            return []

        placeholders = ', '.join(['?'] * len(group_names))
        sql = f"""
            SELECT id, group_name, color_hex, [set]
            FROM ColorGroup
            WHERE group_name IN ({placeholders})
        """
        self.orm.query(ColorGroup,sql, group_names)
        return self.orm.query(ColorGroup,sql, group_names)


    def close(self):
        self.cursor.close()
        self.orm.conn.close()
    
    
def get_orm() -> AutoORM:
    db_path = f'{env.util.sqlite_name}.db'
    if 'orm' not in g:
        g.orm = AutoORM(db_path)  # AutoORM 内部会调用 get_db() 从 g 中取得连接
    return g.orm

def get_color_orm() -> ColorORM:
    if 'color_orm' not in g:
        g.color_orm = ColorORM()  # ColorORM 内部会调用 get_db() 从 g 中取得连接
    return g.color_orm
    
def get_db() -> sqlite3.Connection:
    '''不直接用g.db, 获得更好的类型提示'''
    db_path = f'{env.util.sqlite_name}.db'
    if "db" not in g:
        g.db = sqlite3.connect(db_path)
        u.info('[get_db] Database connected.')
    return g.db


if __name__ == "__main__":
    '''测试用例'''
    orm = AutoORM('test.db')
    
    events = orm.query(Event, 
        "SELECT * FROM Events WHERE device_id = ?", 
        ("test_device",)
    )
    
    if events:
        for event in events:
            print(f"""
            {event.device_id} 在 {event.start_time:%Y-%m-%d %H:%M} 
            使用 {event.app_name}（状态：{'使用中' if event.using else '未使用'}）
            """)
    else:
        print(f'events is {events}!')
    
    orm.close()