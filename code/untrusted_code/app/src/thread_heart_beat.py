from src.smart_contract import get_contract
import time
from src.logger import LOGGER

HEART_BEAT_INTERVAL = 600   # seconds


def heart_beat():
    """
    Thread para envios constantes de heartbeats ao contrato
    :return:
    """
    while True:
        get_contract().heartBeat()
        LOGGER.info('Heartbeat enviado com sucesso')
        time.sleep(HEART_BEAT_INTERVAL)
