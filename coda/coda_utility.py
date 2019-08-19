import requests
import datetime

# TEMP BLOCK # TODO

from django.conf import settings

settings.configure()
settings.CODA_API_KEY = "ec2db341-09e3-4e4f-9252-a62388dd6095"
settings.CODA_DOC_ID = "IuphEtBZK-"
settings.CODA_API_URL = "https://coda.io/apis/v1beta1"
settings.CODA_ALL_ACCOUNTS_TABLE_ID = "grid-av2Ob-DeZY"
settings.CODA_PAYOUT_TABLE_ID = "grid-Bz-2Sjgr1T"
settings.CODA_LEADS_TABLE_ID = "grid-roUTZPp95C"  # таблица с заявками
settings.CODA_LAST_GO_ACCOUNT_FORMULA_ID = 'f-ZOCLuICyTr'

CODA_ALL_ACCOUNTS_COLUMN_ID = {  # Matching coda column names and column ids
    'Номер аккаунта': 'c-RvB-WgUOno',
    'Статус аккаунта': 'c-dSp_SI1Mwh',
    'Login': 'c-F-7VgB7kmw',
    'Password': 'c-LwRIc0U-YR',
    'Тип аккаунта': 'c-AKh7JJmaIb',
    'Номер карты': 'c-tS9cJOGC2a',
    'Name': 'c-fXN-y591bK',
    'Комментарий': 'c-cMb-K_wjMP',
    'Заявка': 'c-ZnVtxZ_4yj',  # ref to leads table
    'Дата передачи в аренду': 'c-u7AH-f6Fl3',
}

CODA_LEADS_COLUMN_ID = {  # Matching coda column names and column ids
    'Name': 'c-Lnmya8GCpa',
    'Login': 'c-1lkzoPM4RP',
    'Password': 'c-S3UiIV4mSf',
    'Status': 'c-U0KLApVjKx',
    'Комментарий': 'c-n6LsyDxvNs',
    'Номер аккаунта': 'c-mMQziDLpkv',  # ref to accounts table
    'Карта человека': 'c-1-9kcMwgUK',
    'Реферер': 'c-YabKOSp_qk',  # ref to other lead
    'Контакт для связи': 'c-qeV8SKjjRK',
    'Ссылка на профиль': 'c-6cen9HGTW1',
}
##

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
    req = requests.post(uri, headers=headers, json=payload)
    req.raise_for_status()  # Throw if there was an error.
    return req.json()


def coda_add_new_go_acc(acc_id, acc_status, fb_login, fb_pass, username='', acc_type='GO', cc_num='', acc_comment='',
                        rent_start_date=''):
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
    ]

    return coda_insert_row(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_ALL_ACCOUNTS_TABLE_ID,
                           payload_list)


def coda_add_new_lead(fb_login, fb_pass, fb_link='', acc_number='', username='', lead_contact='', lead_status='Победа',
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


# print(coda_get_column_list(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_LEADS_TABLE_ID))
# print(coda_list_formulas(settings.CODA_API_KEY, settings.CODA_DOC_ID))
# print(coda_get_formula(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_LAST_GO_ACCOUNT_FORMULA_ID))
# print(coda_insert_row(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_ALL_ACCOUNTS_TABLE_ID))

last_go_acc_id = coda_get_formula(settings.CODA_API_KEY, settings.CODA_DOC_ID, settings.CODA_LAST_GO_ACCOUNT_FORMULA_ID)
new_go_acc_id = 'GO' + str(int(last_go_acc_id) + 1)

print(coda_add_new_go_acc(acc_id=new_go_acc_id,
                          acc_status='Подготовка',
                          username='My Name',
                          fb_login='My Login',
                          fb_pass='My Password',
                          acc_type='GO',
                          cc_num='123',
                          acc_comment='Добавлен из AMOCRM',
                          rent_start_date=datetime.datetime.now().strftime("%d/%m/%Y")
                          ))

print(coda_add_new_lead(fb_login='My login',
                        fb_pass='My pass',
                        fb_link='My fb link',
                        acc_number=new_go_acc_id,
                        username='My username',
                        lead_contact='My lead contact',
                        lead_status='Победа',
                        lead_comment='Заявка из АМО',
                        cc_number='12345',
                        ref='My referer'
                        ))
