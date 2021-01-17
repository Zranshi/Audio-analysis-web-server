import os

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse, HttpRequest
import json
import wave
import numpy as np
import pandas as pd
from analysis_server.settings import BASE_DIR


@require_http_methods(['POST'])
def get_wav(request):
    response = {}
    myFile = None
    for i in request.FILES:
        myFile = request.FILES[i]
    if myFile:
        dir_path = os.path.join(os.path.join(BASE_DIR, 'static'), 'profiles')
        destination = open(os.path.join(dir_path, 'test.wav'), 'wb+')
        for chunk in myFile.chunks():
            destination.write(chunk)
        destination.close()
        response['state'] = 'success'
    else:
        response['state'] = 'error'
    return JsonResponse(response)


@require_http_methods(['GET'])
def show_data(request):
    response = {}
    dir_path = os.path.join(os.path.join(BASE_DIR, 'static'), 'profiles')
    f = wave.open(os.path.join(dir_path, 'test.wav'), 'rb')
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    str_data = f.readframes(nframes)
    f.close()
    wave_data = np.frombuffer(str_data, dtype=np.short)
    wave_data.shape = -1, 2
    a = [i for i in range(0, nframes, 2000)]
    wave_data = wave_data[a, :]
    wave_data = wave_data.T
    # time = np.arange(0, nframes // 2000) * (1000.0 / framerate)
    response['nchannels'] = nchannels
    response['sampwidth'] = sampwidth
    response['framerate'] = framerate
    response['nframes'] = nframes
    response['data'] = wave_data.tolist()
    # response['time'] = time.tolist()
    return JsonResponse(response)
