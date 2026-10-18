"""快照逐行落盘；重复扫描只保留当前行，不累积全部正文。"""
from .codec import lines


class SpoolRows:
    def __init__(self, path, count, limits):
        self.path, self.count, self.limits = path, count, limits

    def __iter__(self):
        with self.path.open('rb') as stream:
            yield from lines(stream, self.limits)

    def __len__(self):
        return self.count


class FilteredRows:
    def __init__(self, rows, predicate):
        self.rows, self.predicate = rows, predicate
        self.count = None

    def __iter__(self):
        return (row for row in self.rows if self.predicate(row))

    def __len__(self):
        if self.count is None:
            self.count = sum(1 for _ in self)
        return self.count
