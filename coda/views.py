from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world! You're at the coda backend.")


def add_new_acc_to_coda(request):
    return HttpResponse("Post req: " + str(request.POST))

