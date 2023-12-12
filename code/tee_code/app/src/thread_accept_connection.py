import json
from typing import List, Dict, Any
from src.user_types import Job


def receive_data(conn: 'Connection') -> str:
    """
    Função que recebe os dados a partir de uma conexão TCP
    :param conn: Objeto representando a conexão
    :return: Dados recebidos na forma de string
    """
    buffer_size = 64*1024  # 64 KB
    delimiter = '#END_OF_TRANSMISSION#'
    data = ''
    while True:
        chunk = conn.recv(buffer_size).decode('utf-8')
        if not chunk:
            # Connection closed
            break
        data += chunk
        if data.endswith(delimiter):
            # End of transmission
            break
    return data.rstrip(delimiter)


def generate_count_chars(messages: List[Job]) -> List[Dict[str, Any]]:
    """
    Função que processa os dados recebidos
    :param messages: Jobs a serem processados
    :return: Função representando a thread
    """

    def count_chars(message):
        try:
            return {"jobId": message["jobId"],
                             "charCount": len(
                                 message["message"]),
                             "message": "SUCESSO"}
        except:
            return {"jobId": message["jobId"],
                             "charCount": 0,
                             "message": "FALHA"}

    return [count_chars(message) for message in messages]


def accept_connection(conn: 'Connection'):
    """
    Função para recebimento de dados e retorno de função para thread de processamento/resposta
    :return:
    """
    
    def process_data():
        with conn:
            data = receive_data(conn)
            json_data = json.loads(data)
            result = json.dumps(generate_count_chars(json_data)).encode("utf-8")
            conn.sendall(result)

    return process_data
