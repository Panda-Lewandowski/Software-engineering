import logging

logging.basicConfig(format='%(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.WARNING, filename='editor.log')


def singleton(cls):
    """
    PEP 0318
    """
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance
