from argparse import Namespace
from pathlib import Path

from patterns.singleton import Singleton


class Args(metaclass=Singleton):
    source = ''
    stop_after_parsing = False
    stop_before_type_inferring = False
    stop_after_type_inferring = False
    skip_header_generation = False

    def __init__(self, args: Namespace = None):
        # Обновление полей текущего объекта полями из args.
        if args is not None:
            self.__dict__.update(args.__dict__)

    def get_header_path(self):
        return str(Path(Args().source).with_suffix('.tmlh'))

    def get_module_name(self):
        return str(Path(Args().source).stem)
