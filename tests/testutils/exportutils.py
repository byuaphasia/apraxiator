from datetime import datetime


def gen_export_data(num_rows=3):
    data = []
    for i in range(num_rows):
        row = [
            f'EV-{i}',
            'word',
            f'AT-{i}',
            3.14,
            3.14,
            True,
            3,
            datetime.now(),
            '50',
            'male',
            'normal'
        ]
        data.append(row)
    return data
