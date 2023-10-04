from src.smart_contract import get_contract
import time

HEART_BEAT_INTERVAL = 20  # seconds


def heart_beat():
    """
    Thread para envios constantes de heartbeats ao contrato
    :return:
    """
    while True:
        get_contract().heartBeat()
        time.sleep(HEART_BEAT_INTERVAL)
