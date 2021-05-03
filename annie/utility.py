from tabulate import tabulate


def tabprint(cls) -> None:
    try:
        data = []
        columns = []
        for rows in cls:
            row = []
            columns = rows.__dict__.keys()
            for k, v in rows.__dict__.items():
                if isinstance(v, (str, int)):
                    row.append(v)
            data.append(row)
        print(tabulate(data, headers=columns))

    except TypeError:
        columns = []
        row = []
        for k, v in cls.__dict__.items():
            if isinstance(v, (str, int)):
                columns.append(k)
                row.append(v)
        print(tabulate([row], headers=columns))

