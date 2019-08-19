from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Log, AmoUser, AmoLead
from .amo_utility import amo_auth, get_amo_contact_id_by_lead_id, get_amo_contact_info_by_id
from django.conf import settings


def index(request):
    return HttpResponse("Hello, world! You're at the coda backend.")


@csrf_exempt
def add_new_acc_to_coda(request):
    request.POST = {"leads[status][0][id]": "4016739",
                    "leads[status][0][status_id]": "29269078",
                    "leads[status][0][pipeline_id]": "1967815",
                    "leads[status][0][old_status_id]": "29269075",
                    "leads[status][0][old_pipeline_id]": "1967815",
                    "account[subdomain]": "watchrussians"}

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

        # Create AMO Lead
        if amo_lead_status_id:
            amo_lead, created = AmoLead.objects.get_or_create(amo_user=amo_user, amo_lead_id=amo_lead_id,
                                                              amo_status_id=amo_lead_status_id)
        else:
            amo_lead, created = AmoLead.objects.get_or_create(amo_user=amo_user, amo_lead_id=amo_lead_id)
            if created:
                Log.objects.create(log_type=Log.INFO_TYPE, function_name=add_new_acc_to_coda.__name__,
                                   text="Info: Lead created without status id. Amo lead id: " + str(amo_lead.id))

        if not created:
            log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                         text="Error: this AMO lead is already exists. Lead id: " + str(amo_lead.id))
            return HttpResponse("Error: AMO lead is already exist. Log id: " + str(log_obj.id))
        else:
            return HttpResponse("Lead created")

    else:
        log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__,
                                     text="Error: You need provide more data. amo_lead_id is not provided. Provided data: " + json.dumps(
                                         request.POST))
        return HttpResponse("Error: You need provide more data. Log_id: " + str(log_obj.id))
