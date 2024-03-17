from django.shortcuts import render
from django.http import HttpResponse

from server.settings import logger
from wfit.tasks import run_workflow_integrator


def test(request):

    return HttpResponse("Ok")


def run_wfit(request):
    try:
        logger.info("run_wfit called")
        status = run_workflow_integrator()
        if status:
            return HttpResponse("Done")
        return HttpResponse("Failed")
    except Exception as err:
        return HttpResponse(f"Error: {err}")
