from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Log, AmoUser, AmoLead


def index(request):
    return HttpResponse("Hello, world! You're at the coda backend.")


@csrf_exempt
def add_new_acc_to_coda(request):
    request.POST = {"leads[status][0][id]": "3779241",
                    "leads[status][0][status_id]": "29269078",
                    "leads[status][0][pipeline_id]": "1967815",
                    "leads[status][0][old_status_id]": "29269075",
                    "leads[status][0][old_pipeline_id]": "1967815",
                    "account[id]": "28584955",
                    "account[subdomain]": "watchrussians"}

    amo_lead_id = request.POST.get("leads[status][0][id]")
    amo_account_id = request.POST.get("account[id]")
    amo_lead_status_id = request.POST.get("leads[status][0][status_id]")

    # TEMP CODE ##### TODO
    amo_user = AmoUser.objects.last()
    if not amo_user:
        amo_user = AmoUser.objects.create(amo_user_id='1')
    #######

    if amo_lead_id and amo_account_id:
        if amo_lead_status_id:
            amo_lead, created = AmoLead.objects.get_or_create(amo_user=amo_user, amo_lead_id=amo_lead_id, amo_account_id=amo_account_id, amo_status_id=amo_lead_status_id)
        else:
            amo_lead, created = AmoLead.objects.get_or_create(amo_user=amo_user, amo_lead_id=amo_lead_id, amo_account_id=amo_account_id)
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
        log_obj = Log.objects.create(log_type=Log.ERROR_TYPE, function_name=add_new_acc_to_coda.__name__, text="Error: You need provide more data. Provided data: " + json.dumps(request.POST))
        return HttpResponse("Error: You need provide more data. Log_id: " + str(log_obj.id))
