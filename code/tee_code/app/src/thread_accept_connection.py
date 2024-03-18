import io
from src.logger import LOGGER
import traceback
import PyPDF2
import newrelic.agent
import json


@newrelic.agent.background_task()
def process_pdf_data(job_id, pdf_data):
    try:
        LOGGER.info(f"Processando job {job_id}")
        total_response = 0
        file = io.BytesIO(pdf_data)
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            total_response += len(page.extract_text())
        return {"jobId": job_id, "charCount": total_response, "message": "SUCESSO"}
    except Exception:
        formatted_exc = traceback.format_exc()
        LOGGER.error(formatted_exc)
        return {"jobId": job_id, "charCount": 0, "message": "ERRO"}


def parse_header(header):
    parts = header.split('#')
    if len(parts) >= 2 and parts[0] == "BEGIN":
        return int(parts[1])
    return None


def accept_connection(connection):
    def handle_connection():
        try:
            buffer = b""
            job_id = None
            processing_started = False

            while True:
                chunk = connection.recv(4096)
                buffer += chunk

                if not processing_started and b'##' in buffer:
                    header_part, _, buffer = buffer.partition(b'##')
                    job_id = parse_header(header_part.decode("utf-8"))
                    processing_started = True

                if b"#END_OF_TRANSMISSION#" in buffer:
                    buffer, _ = buffer.split(b"#END_OF_TRANSMISSION#", 1)
                    break

            processed_result = process_pdf_data(job_id, buffer)
            connection.sendall(json.dumps(processed_result).encode("utf-8"))
        except Exception:
            formatted_exc = traceback.format_exc()
            LOGGER.error(formatted_exc)
        finally:
            connection.close()

    return handle_connection
