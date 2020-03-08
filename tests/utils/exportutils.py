def gen_export_data(num_rows=3):
    data = []
    for i in range(num_rows):
        row = [
            f'EV-{i}',
            'word',
            f'AT-{i}',
            3.14,
            3.14,
            '2000-01-01',
            '50',
            'male',
            'normal',
            open('tests/utils/example.wav', 'rb').read()
        ]
        data.append(row)
    return data
