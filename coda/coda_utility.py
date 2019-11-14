import requests
from django.conf import settings

CODA_ALL_ACCOUNTS_COLUMN_ID = settings.CODA_ALL_ACCOUNTS_COLUMN_ID
CODA_LEADS_COLUMN_ID = settings.CODA_LEADS_COLUMN_ID
CODA_PAYOUT_COLUMN_ID = settings.CODA_PAYOUT_COLUMN_ID
CODA_API_URL = settings.CODA_API_URL


def coda_get_table(coda_api_token, coda_doc_id, coda_table_id):
    headers = {'Authorization': 'Bearer {}'.format(coda_api_token)}
    d = {'coda_url': CODA_API_URL,
         'doc_id': coda_doc_id,
         'table_id': coda_table_id}

    uri = '{coda_url}/docs/{doc_id}/tables/{table_id}'.format(**d)
    res = requests.get(uri, headers=headers).json()

    return res


def coda_get_column_list(coda_api_token, coda_doc_id, coda_table_id):
    headers = {'Authorization': 'Bearer {}'.format(coda_api_token)}
    d = {'coda_url': CODA_API_URL,
         'doc_id': coda_doc_id,
         'table_id': coda_table_id}

    uri = '{coda_url}/docs/{doc_id}/tables/{table_id}/columns'.format(**d)
    res = requests.get(uri, headers=headers).json()

    return res


def coda_list_formulas(coda_api_token, coda_doc_id):
    headers = {'Authorization': 'Bearer {}'.format(coda_api_token)}
    d = {'coda_url': CODA_API_URL,
         'doc_id': coda_doc_id}

    uri = '{coda_url}/docs/{doc_id}/formulas'.format(**d)
    res = requests.get(uri, headers=headers).json()

    return res


def coda_get_formula(coda_api_token, coda_doc_id, coda_formula_id_or_name):
    headers = {'Authorization': 'Bearer {}'.format(coda_api_token)}
    d = {'coda_url': CODA_API_URL,
         'doc_id': coda_doc_id,
         'formula_id_or_name': coda_formula_id_or_name}

    uri = '{coda_url}/docs/{doc_id}/formulas/{formula_id_or_name}'.format(**d)
    res = requests.get(uri, headers=headers).json()

    return res.get('value')


def coda_insert_row(coda_api_token, coda_doc_id, coda_table_id, payload_list):
    headers = {'Authorization': 'Bearer {}'.format(coda_api_token)}
    d = {'coda_url': CODA_API_URL,
         'doc_id': coda_doc_id,
         'table_id': coda_table_id}

    uri = '{coda_url}/docs/{doc_id}/tables/{table_id}/rows'.format(**d)
    payload = {
        'rows': [
            {
                'cells': payload_list,
            },
        ],
    }

    for d in payload_list:
        if d.get('value') is None:
            d['value'] = ''

    req = requests.post(uri, headers=headers, json=payload)
    req.raise_for_status()  # Throw if there was an error.
    return req.status_code


def coda_add_new_go_acc(acc_id, acc_status, fb_login='', fb_pass='', username='', acc_type='GO', cc_num='', acc_comment='',
                        rent_start_date='', amo_lead_id='', amo_contact_id='', acc_wall_raws='', acc_age='',
                        acc_friends_quantity='', acc_chat_activity=''):
    payload_list = [
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Номер аккаунта'], 'value': acc_id},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Статус аккаунта'], 'value': acc_status},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Login'], 'value': fb_login},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Password'], 'value': fb_pass},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Тип аккаунта'], 'value': acc_type},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Номер карты'], 'value': cc_num},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Name'], 'value': username},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Комментарий'], 'value': acc_comment},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Дата передачи в аренду'], 'value': rent_start_date},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Сделка в AMO'], 'value': amo_lead_id},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Контакт в AMO'], 'value': amo_contact_id},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Кол-во записей на стене'], 'value': acc_wall_raws},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Возраст аккаунта'], 'value': acc_age},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Кол-во друзей'], 'value': acc_friends_quantity},
        {'column': CODA_ALL_ACCOUNTS_COLUMN_ID['Активность переписки'], 'value': acc_chat_activity},
    ]

    return coda_insert_row(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_ALL_ACCOUNTS_TABLE_ID,
                           payload_list)


def coda_add_new_lead(fb_login='', fb_pass='', fb_link='', acc_number='', username='', lead_contact='', lead_status='Победа',
                      lead_comment='', cc_number='', ref=''):
    payload_list = [
        {'column': CODA_LEADS_COLUMN_ID['Name'], 'value': username},
        {'column': CODA_LEADS_COLUMN_ID['Login'], 'value': fb_login},
        {'column': CODA_LEADS_COLUMN_ID['Password'], 'value': fb_pass},
        {'column': CODA_LEADS_COLUMN_ID['Status'], 'value': lead_status},
        {'column': CODA_LEADS_COLUMN_ID['Комментарий'], 'value': lead_comment},
        {'column': CODA_LEADS_COLUMN_ID['Номер аккаунта'], 'value': acc_number},
        {'column': CODA_LEADS_COLUMN_ID['Карта человека'], 'value': cc_number},
        {'column': CODA_LEADS_COLUMN_ID['Реферер'], 'value': ref},
        {'column': CODA_LEADS_COLUMN_ID['Контакт для связи'], 'value': lead_contact},
        {'column': CODA_LEADS_COLUMN_ID['Ссылка на профиль'], 'value': fb_link},
    ]

    return coda_insert_row(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_LEADS_TABLE_ID,
                           payload_list)


def coda_add_new_payout(lead_id, value, purpose, status='Ожидание', comment='', ref_id=''):
    payload_list = [
        {'column': CODA_PAYOUT_COLUMN_ID['Клиент'], 'value': lead_id},
        {'column': CODA_PAYOUT_COLUMN_ID['Сумма'], 'value': value},
        {'column': CODA_PAYOUT_COLUMN_ID['Статус'], 'value': status},
        {'column': CODA_PAYOUT_COLUMN_ID['Назначение'], 'value': purpose},
        {'column': CODA_PAYOUT_COLUMN_ID['Комментарий'], 'value': comment},
        {'column': CODA_PAYOUT_COLUMN_ID['Реферал'], 'value': ref_id},
    ]

    return coda_insert_row(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_PAYOUT_TABLE_ID,
                           payload_list)
