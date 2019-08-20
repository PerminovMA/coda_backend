from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Log, AmoUser, AmoLead, FBAccount
from .amo_utility import amo_auth, get_amo_contact_id_by_lead_id, get_amo_contact_info_by_id
from django.conf import settings
from .coda_utility import coda_get_formula, coda_add_new_go_acc, coda_add_new_payout, coda_add_new_lead
import datetime


def index(request):
    return HttpResponse("Hello, world! You're at the coda backend.")


@csrf_exempt
def add_new_acc_to_coda(request):
    # request.POST = {"leads[status][0][id]": "4244005",
    #                 "leads[status][0][status_id]": "29269078",
    #                 "leads[status][0][pipeline_id]": "1967815",
    #                 "leads[status][0][old_status_id]": "29269075",
    #                 "leads[status][0][old_pipeline_id]": "1967815",
    #                 "account[subdomain]": "watchrussians"}

    amo_lead_id = request.POST.get("leads[status][0][id]")
    amo_lead_status_id = request.POST.get("leads[status][0][status_id]")

    if amo_lead_id:

        # BEGIN: Get data from AMO
        amo_auth_result, amo_session_id_or_error = amo_auth(settings.AMO_USER_LOGIN, settings.AMO_USER_HASH,
                                                            settings.AMO_URL)
        if amo_auth_result:  # AMO auth success
            req_result, amo_contact_id_or_error = get_amo_contact_id_by_lead_id(amo_lead_id, settings.AMO_URL,
                                                                                amo_session_id_or_error)
            if req_result:  # AMO contact id received
                amo_contact_id = amo_contact_id_or_error
                req_result, amo_contact_data_or_error = get_amo_contact_info_by_id(amo_contact_id, settings.AMO_URL,
                                                                                   amo_session_id_or_error)
                if req_result:  # AMO data received, create or update AmoUser
                    amo_user, created = AmoUser.objects.update_or_create(amo_user_id=amo_contact_id,
                                                                         defaults=amo_contact_data_or_error)
                else:
                    log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                                 text="Cant get info about AMO contact. Reason: {}".format(
                                                     amo_contact_data_or_error))
                    return HttpResponse("Error: Cant get info about AMO contact. Log_id: " + str(log_obj.id))
            else:
                log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                             text="Cant get AMO contact by lead id. Reason: {}".format(
                                                 amo_contact_id_or_error))
                return HttpResponse("Error: Cant get AMO contact. Log_id: " + str(log_obj.id))
        else:
            log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                         text="Cant auth in AMO. Reason: {}".format(amo_session_id_or_error))
            return HttpResponse("Error: Cant auth in AMO. Log_id: " + str(log_obj.id))
        # END: Get data from AMO

        # BEGIN: Create AmoLead
        if amo_lead_status_id:
            amo_lead, created = AmoLead.objects.get_or_create(amo_user=amo_user, amo_lead_id=amo_lead_id,
                                                              amo_status_id=amo_lead_status_id)
        else:
            amo_lead, created = AmoLead.objects.get_or_create(amo_user=amo_user, amo_lead_id=amo_lead_id)
            if created:
                Log.objects.create(log_type=Log.INFO_TYPE, function_name=add_new_acc_to_coda.__name__,
                                   text="Info: Lead created without status id. Amo lead id: " + str(amo_lead.id))

        if not created and amo_lead.sold:
            log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                         text="Error: this AMO lead is already exists and Sold. Lead id: " + str(
                                             amo_lead.id))
            return HttpResponse("Error: AMO lead is already exist and Sold. Log id: " + str(log_obj.id))
        # END: Create AmoLead

        # BEGIN: Send data to coda
        last_go_acc_id = coda_get_formula(settings.CODA_API_KEY, settings.CODA_DOC_ID,
                                          settings.CODA_LAST_GO_ACC_FORMULA_ID)  # get max go account index from coda

        # If max local acc index more than received index use local acc index + 1
        last_created_fb_acc = FBAccount.objects.last()
        if last_created_fb_acc and int(last_created_fb_acc.get_acc_index_number) > int(last_go_acc_id):
            last_go_acc_id = last_created_fb_acc.get_acc_index_number
            Log.objects.create(log_type=Log.WARNING_TYPE, function_name=add_new_acc_to_coda.__name__,
                               text="Warning: Received max go acc index from amo not relevant. Set index: {}".format(
                                   int(last_go_acc_id) + 1))

        if last_go_acc_id:  # Last go account number received
            new_go_acc_id = FBAccount.GO_TYPE + str(int(last_go_acc_id) + 1)

            req_result = coda_add_new_go_acc(acc_id=new_go_acc_id,
                                             acc_status='Подготовка',
                                             username=amo_user.name,
                                             fb_login=amo_user.fb_login,
                                             fb_pass=amo_user.fb_password,
                                             acc_type=FBAccount.GO_TYPE,
                                             cc_num=amo_user.cc_number,
                                             acc_comment='Добавлен из AMOCRM',
                                             rent_start_date=datetime.datetime.now().strftime("%d/%m/%Y")
                                             )
            if req_result != 202:  # Error
                log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                             text="Error: Cant create new GO acc in coda. AmoUser.id is {}".format(
                                                 amo_user.id))
                return HttpResponse("Error: Cant create new GO acc in coda. Log id: " + str(log_obj.id))
            FBAccount.objects.create(amo_lead=amo_lead, acc_name=new_go_acc_id, acc_type=FBAccount.GO_TYPE)

            req_result = coda_add_new_lead(fb_login=amo_user.fb_login,
                                           fb_pass=amo_user.fb_password,
                                           fb_link=amo_user.facebook_link,
                                           acc_number=new_go_acc_id,
                                           username=amo_user.name,
                                           lead_contact="tg: {}".format(amo_user.telegram_username),
                                           lead_status='Победа',
                                           lead_comment='Заявка из АМО',
                                           cc_number=amo_user.cc_number,
                                           ref=amo_user.ref_id if amo_user.ref_id else ''
                                           )

            if req_result != 202:  # Error
                log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                             text="Error: Cant create new Lead in coda. AmoUser.id is {}".format(
                                                 amo_user.id))
                return HttpResponse("Error: Cant create new Lead in coda. Log id: " + str(log_obj.id))

            # if everything ok, create payout request
            if amo_user.ref_id:
                req_result1 = coda_add_new_payout(new_go_acc_id, 10, 'Аванс за аренду', comment='Заявка из АМО',
                                                  ref_id='')
                req_result2 = coda_add_new_payout(amo_user.ref_id, 10, 'Бонус за реферала', comment='Заявка из АМО',
                                                  ref_id=new_go_acc_id)

                if req_result1 != 202 or req_result2 != 202:
                    log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                                 text="Error: Cant create new payout req AmoUser.id is {}".format(
                                                     amo_user.id))
                    return HttpResponse("Error: Cant create new payout req. Log id: {}".format(log_obj.id))
            else:
                req_result = coda_add_new_payout(new_go_acc_id, 10, 'Аванс за аренду', comment='Заявка из АМО',
                                                 ref_id='')

                if req_result != 202:
                    log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                                 text="Error: Cant create new payout req AmoUser.id is {}".format(
                                                     amo_user.id))
                    return HttpResponse("Error: Cant create new payout req. Log id: {}".format(log_obj.id))

            amo_lead.sold = True
            amo_lead.save()

            Log.objects.create(log_type=Log.INFO_TYPE, function_name=add_new_acc_to_coda.__name__,
                               text="All done! AmoUser.id is {}".format(amo_user.id))

            return HttpResponse("Everything OK!")

        else:
            log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                         text="Cant get last go account number.")
            return HttpResponse("Error: Cant get last go account number. Log id: " + str(log_obj.id))
        # END: Send data to coda

    else:
        log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                     text="Error: You need provide more data. amo_lead_id is not provided. Provided data: " + json.dumps(
                                         request.POST))
        return HttpResponse("Error: You need provide more data. Log_id: " + str(log_obj.id))
