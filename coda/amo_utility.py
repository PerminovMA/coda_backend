import json
import requests


def amo_auth(amo_user_login, amo_user_hash, amo_domain):
    """Function for auth in AMO.
    @:arg amo_user_login: login in AMO (email)
    @:arg amo_user_hash: API KEY in AMO
    @:returns tuple: (True or False (Auth success), received obj if success, else Error string)

    """

    auth_url = amo_domain + "/private/api/auth.php?type=json"
    post_fields = {'USER_HASH': amo_user_hash,
                   'USER_LOGIN': amo_user_login}

    r = requests.post(auth_url, data=post_fields)

    try:
        if r.json()['response']['auth'] is True:
            return True, r.cookies['session_id']
        else:
            return False, "Error: Auth not success. Plz, see received data: " + r.text
    except (KeyError, json.decoder.JSONDecodeError):
        return False, "Error: Unexpected answer. Data: " + r.text


def get_amo_contact_id_by_lead_id(amo_lead_id, amo_domain, session_key):
    url = amo_domain + "/api/v2/leads?id=" + str(amo_lead_id)
    cookies = dict(session_id=session_key)

    r = requests.get(url, cookies=cookies)

    if r.status_code == 204:
        return False, "Error: Lead with that id is not exists. Data: " + r.text

    try:
        amo_contact_id = r.json()['_embedded']['items'][0]['main_contact']['id']
        return True, amo_contact_id
    except KeyError:
        return False, "Error: Unexpected answer. Data: " + r.text


def get_amo_contact_info_by_id(amo_contact_id, amo_domain, session_key):
    url = amo_domain + "/api/v2/contacts/?id=" + str(amo_contact_id)
    cookies = dict(session_id=session_key)

    r = requests.get(url, cookies=cookies)

    try:
        amo_data = r.json()['_embedded']['items'][0]
        custom_fields = amo_data['custom_fields']
    except KeyError:
        return False, "Error: Unexpected answer. Data: " + r.text

    def get_field_by_name_from_custom_fields(field_name, fields_list):  # This function help get data from amo data
        for field in fields_list:
            if field.get('name') == field_name:
                return field['values'][0].get('value')

    useful_data = {
        "amo_user_id": amo_data.get('id'),
        "name": amo_data.get('name'),
        "phone_number": get_field_by_name_from_custom_fields('Телефон', custom_fields),
        "responsible_user_id": amo_data.get('responsible_user_id'),
        "telegram_username": get_field_by_name_from_custom_fields('Username', custom_fields),
        "chat_id": get_field_by_name_from_custom_fields('Chat ID', custom_fields),
        "ref_id": get_field_by_name_from_custom_fields('REFID', custom_fields),
        "amo_account_id": amo_data.get('account_id'),
        "facebook_link": get_field_by_name_from_custom_fields('Ссылка на ваш аккаунт Facebook', custom_fields),
        "cc_number": get_field_by_name_from_custom_fields('Номер карты', custom_fields),
        "fb_login": get_field_by_name_from_custom_fields('Логин Facebook', custom_fields),
        "fb_password": get_field_by_name_from_custom_fields('Пароль Facebook', custom_fields),
    }

    return True, useful_data
