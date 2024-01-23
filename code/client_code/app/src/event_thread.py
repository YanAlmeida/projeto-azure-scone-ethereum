import time


def event_thread(queue, fire_method):
    t_break = False
    while True:
        while not queue.empty():
            next_event = queue.get()
            if next_event is None:
                t_break = True
                break
            fire_method(**next_event)
        if t_break:
            break
        time.sleep(0.1)
