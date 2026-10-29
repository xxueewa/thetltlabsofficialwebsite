import json
import logging
import os

from dotenv import load_dotenv
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Activity, Project

load_dotenv()
logger = logging.getLogger(__name__)

@ensure_csrf_cookie
@require_GET
def index(request):
    activities = Activity.objects.all()
    projects = Project.objects.all()
    return render(request, "pages/index.html", {
        "activities": activities,
        "projects": projects,
        "localdev": settings.DEBUG,
    })


@require_GET
def get_blobs(request):
    from vercel.blob import sync as sync_client
    from vercel.api import session

    def resolve_credentials() -> blob.syncBlobCredentials:
        return blob.syncBlobCredentials(
            token=settings.VERCEL_OIDC_TOKEN,
            store_id=settings.BLOB_STORE_ID
        )

    options = blob.syncBlobCredentials(credentials_factory=resolve_credentials)

    projects = Project.objects.all()
    # blobs = []
    # for project in projects:
    #     video_path = project.video
    result = sync_client.get_blob("/video/OrdinarynoteDemo.mp4")
    with session(service_option=[options]):
        metadata = blob.head_blob("/video/OrdinarynoteDemo.mp4")
    return render
