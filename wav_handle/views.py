import os
import wave

import numpy as np
from django.http import JsonResponse
# Create your views here.
from django.views.decorators.http import require_http_methods

from analysis_server.settings import BASE_DIR


@require_http_methods(['POST'])
def get_wav(request):
    """
    获取音频文件并保存到' /static/profiles '文件夹中
    :param request:
    :return:
    """
    response = {}
    myFile = None
    for i in request.FILES:
        myFile = request.FILES[i]
    if myFile:
        dir_path = os.path.join(os.path.join(BASE_DIR, 'static'), 'profiles')
        # 文件写入
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
    """
    返回音频文件信息
    :param request:
    :return:
    """
    response = {}
    dir_path = os.path.join(os.path.join(BASE_DIR, 'static'), 'profiles')

    # 文件读取
    f = wave.open(os.path.join(dir_path, 'test.wav'), 'rb')
    params = f.getparams()
    # nchannels, sampwidth, framerate, nframes = params[:4]
    audio_params = params[:4]
    str_data = f.readframes(audio_params[3])
    f.close()

    def data_process():
        # wav音频文件信息部分
        # 分别代表：声道数量，量化位数，采样频率，采样点数
        response['audio_params'] = audio_params

        # 波形图部分
        # 切片距离，每clip_length获取一次数据
        clip_length = 2000
        a = [i for i in range(0, audio_params[3], clip_length)]
        # 波形图数据
        wave_data = np.frombuffer(str_data, dtype=np.short)
        wave_data.shape = -1, 2
        wave_data = wave_data[a, :]
        wave_data = wave_data.T
        # 波形图横轴
        time = np.arange(0, audio_params[3] // clip_length) * (clip_length * 1000 // audio_params[2])
        # 将波形图数据传入响应
        response['time'] = time.tolist()
        response['data'] = wave_data.tolist()

        # 频谱图部分
        # FFT处理的取样长度
        fft_size = len(wave_data[0])
        xs = wave_data[0][:fft_size]
        xf = np.fft.rfft(xs) / fft_size
        # 获取横轴和数据
        np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
        freq = np.linspace(0, audio_params[2] / 2, fft_size // 2 + 1)
        freq = np.round(freq.tolist(), decimals=2)
        xfp = 20 * np.log10(np.clip(np.abs(xf), 1e-20, 1e100))
        # 将频谱图数据传入响应
        response['freq'] = freq.tolist()
        response['xfp'] = xfp.tolist()

    data_process()
    return JsonResponse(response)
