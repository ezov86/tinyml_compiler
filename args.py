from argparse import Namespace

from patterns.singleton import Singleton


class Args(metaclass=Singleton):
    source = ''
    stop_after_parsing = False
    stop_after_type_inferring = False

    def __init__(self, args: Namespace = None):
        # Обновление полей текущего объекта полями из args.
        if args is not None:
            self.__dict__.update(args.__dict__)
