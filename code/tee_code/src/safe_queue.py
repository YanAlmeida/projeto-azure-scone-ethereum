import queue

QUEUE = queue.Queue()


def get_queue() -> queue.Queue:
    """
    Função para retorno de fila centralizada na aplicação
    :return: Fila (Queue)
    """
    return QUEUE
