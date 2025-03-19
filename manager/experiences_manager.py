import itertools

class Experience:
    id_iter = itertools.count()

    def __init__(self, name: str, what: str, where: str, how: str, when: str, result: str, type:str):
        self.id = next(self.id_iter)
        self.name = name
        self.what = what
        self.where = where
        self.how = how
        self.when = when
        self.result = result
        self.type = type
        self.info = [what, how, result]
        self.improved_version = None
