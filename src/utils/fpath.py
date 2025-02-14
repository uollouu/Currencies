from fnmatch import fnmatch
class FPath:
    def __init__(self, path: str):
        self.fpath = [i for i in path.split("/") if i.strip()]

    def match(self, path_pattern: str) -> bool:
        fpattern = FPath(path_pattern)
        if len(self) != len(fpattern):
            return False

        for i in range(len(self)):
            if not fnmatch(self[i], fpattern[i]):
                return False
        return True

    def __len__(self):
        return len(self.fpath)

    def __getitem__(self, item):
        return self.fpath[item]