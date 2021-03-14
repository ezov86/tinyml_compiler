from argparse import Namespace

from patterns.singleton import Singleton


class Args(Singleton):
    source = ''
    stop_after_parsing = False

    def initialize(self, args: Namespace):
        # Обновление полей текущего объекта полями из args.
        self.__dict__.update(args.__dict__)
