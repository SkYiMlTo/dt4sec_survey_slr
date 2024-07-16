import logging
import threading
import time


def thread_function():
    print(name)
    time.sleep(2)
    print("b")


def main_scrap_databases(request):
    print("Fetching IEEE XPLORE... ", end='')
    ieee = IeeeXplore()
    ieee.request_all_infos_ieeexplore()
    print("done.")

    print("Fetching Computer... ", end='')
    computer = Computer()
    computer.request_all_infos_computer()
    print("done.")

    print("Fetching Scopus... ", end='')
    sc = Scopus()
    sc.request_all_infos_scopus()
    print("done.")

    print("Fetching Semantic Scholar... ", end='')
    ss = SemanticScholar()
    ss.request_all_infos_semantic_scholar()
    print("done.")
    x = threading.Thread(target=thread_function, args=(), daemon=False)
    y = threading.Thread(target=thread_function, args=(), daemon=False)
    x.start()
    y.start()
    print("all done")
