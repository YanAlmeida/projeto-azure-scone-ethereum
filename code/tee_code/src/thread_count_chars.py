from src.safe_queue import get_queue


def generate_count_chars(message):

    def count_chars():
        try:
            get_queue().put({"jobId": message["jobId"],
                                        "charCount": len(
                                            message["message"]),
                                        "message": "SUCESSO"})
        except:
            get_queue().put({"jobId": message["jobId"],
                                        "charCount": 0,
                                        "message": "FALHA"})

    return count_chars
