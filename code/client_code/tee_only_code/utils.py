import lorem
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import socket
import json
import PyPDF2


def read_pdf(size):
    total_response = ''
    reader = PyPDF2.PdfReader(f'./output_{size}.pdf')
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        total_response += page.extract_text()
    return total_response


def send_data_to_tee(message):
    """
    Função para envio dos dados ao TEE e dos resultados à blockchain
    :return:
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('20.36.185.90', 9090))
        final_string = json.dumps(message) + "#END_OF_TRANSMISSION#"
        sock.sendall(final_string.encode("utf-8"))
        received = sock.recv(64*1024).decode("utf-8") #64 KB

    return json.loads(received)
