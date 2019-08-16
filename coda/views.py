from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Log


def index(request):
    return HttpResponse("Hello, world! You're at the coda backend.")


@csrf_exempt
def add_new_acc_to_coda(request):
    # return HttpResponse("Post req: " + str(request.POST))
    # return JsonResponse(request.POST)
    Log.objects.create(text=json.dumps(request.POST))
    return HttpResponse(json.dumps(request.POST))
