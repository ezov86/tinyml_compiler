class Singleton:
    _instance = None

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
