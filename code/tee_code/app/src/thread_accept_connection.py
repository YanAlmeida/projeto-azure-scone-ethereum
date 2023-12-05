import json
from typing import List, Dict, Any
from src.user_types import Job


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


def accept_connection(conn):
    """
    Função para recebimento de dados e retorno de função para thread de processamento/resposta
    :return:
    """
    
    def process_data():
        with conn:
            data = conn.recv(1024)
            json_data = json.loads(data.decode('utf-8'))
            result = json.dumps(generate_count_chars(json_data)).encode("utf-8")
            conn.sendall(result)

    return process_data
