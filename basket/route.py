import os

from flask import Blueprint, request, render_template, current_app, session, redirect, url_for

from coursework.db_context_manager import DBConnection

from coursework.db_work import select_dict
from coursework.sql_provider import SQLProvider

from coursework.cache.wrapper import fetch_from_cache


blueprint_order = Blueprint('bp_order', __name__, template_folder='templates', static_folder='static')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/start_order', methods=['GET', 'POST'])
def order_index():
    db_config = current_app.config['db_config']
    cache_config = current_app.config['cache_config']
    cached_select = fetch_from_cache('all_items_cached', cache_config)(select_dict)
    if request.method == 'GET':
        sql = provider.get('all_items.sql')
        items = cached_select(db_config, sql)
        basket_items = session.get('basket', {})
        return render_template('basket_order.html', items=items, basket=basket_items)
    else:
        prod_id = request.form['prod_id']
        sql = provider.get('select_item.sql', prod_id=prod_id)
        item = select_dict(db_config, sql)[0]

        add_to_basket(prod_id, item)

        return redirect(url_for('bp_order.order_index'))


@blueprint_order.route('/save_order', methods=['GET', 'POST'])
def save_order():
    user_id = session.get('user_id')
    current_basket = session.get('basket', {})
    order_id = save_order_with_list(current_app.config['db_config'], user_id, current_basket)
    if order_id:
        session.pop('basket')
        return render_template('order_created.html', order_id=order_id)
    else:
        return 'Something get wrong'


@blueprint_order.route('/clear-basket')
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(url_for('bp_order.order_index'))


def save_order_with_list(dbconfig, user_id, current_basket):
    with DBConnection(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Cursor doesn`t created')
        print(user_id)
        _sql1 = provider.get('insert_order.sql', user_id=user_id)
        print(_sql1)
        result1 = cursor.execute(_sql1)     # Количество строк на которые будут изменения в БД
        if result1 == 1:
            _sql2 = provider.get('select_order_id.sql', user_id=user_id)
            cursor.execute(_sql2)
            order_id = cursor.fetchall()[0][0]

            if order_id:
                for key in current_basket:
                    prod_amount = current_basket[key]['amount']
                    _sql3 = provider.get('insert_order_list.sql', order_id=order_id, prod_id=key,
                                         prod_amount=prod_amount)
                    cursor.execute(_sql3)
                return order_id


def add_to_basket(prod_id, item):
    curr_basket = session.get('basket', {})

    if prod_id in curr_basket:
        curr_basket[prod_id]['amount'] += 1
    else:
        curr_basket[prod_id] = {
            'b_name': item['b_name'],
            'b_cost': item['b_cost'],
            'amount': 1
        }
        session['basket'] = curr_basket
        session.permanent = True
    return True
