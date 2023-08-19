from typing import Tuple, List
from db_context_manager import DBConnection


def select(db_config: dict, sql: str) -> Tuple[Tuple, List[str]]:
    """
    Выполняет запрос (SELECT) к БД с указанным конфигом и запросом.
    Args:
        db_config: dict - Конфиг для подключения к БД.
        sql: str - SQL-запрос.
    Return:
        Кортеж с результатом запроса и описанеим колонок запроса.
    """
    with DBConnection(db_config) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')
        cursor.execute(sql)
        schema = [column[0] for column in cursor.description]
        result = cursor.fetchall()
    return result, schema


def select_dict(db_config, sql):
    with DBConnection(db_config) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')

        cursor.execute(sql)
        schema = [column[0] for column in cursor.description]
        result = [dict(zip(schema, row)) for row in cursor.fetchall()]

    return result


def call_proc(db_config, proc_name, *args):
    with DBConnection(db_config) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')
        param_list = list(*args)
        print('param_list=', param_list)
        res = cursor.callproc(proc_name, param_list)

    return res
