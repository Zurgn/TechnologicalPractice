import pandas

df = pandas.read_csv('dataset.csv', index_col=0)

# Настройка для отображения всех строк без сокращений:
# pandas.set_option('display.max_rows', None)
# pandas.set_option('display.max_columns', None)


categorical_cols = [
    'Country', 
    'Region', 
    'Year', 
    'Water Source Type', 
    'Water Treatment Method'
]

counting_cols = [
    'Cholera Cases per 100,000 people',
    'Typhoid Cases per 100,000 people',
    'Infant Mortality Rate (per 1,000 live births)',
    'GDP per Capita (USD)',
    'Healthcare Access Index (0-100)',
    'Urbanization Rate (%)',
    'Sanitation Coverage (% of Population)',
    'Rainfall (mm per year)',
    'Temperature (°C)',
    'Population Density (people per km²)'
]

if __name__ == '__main__':
    with open('report.txt', 'w', encoding='utf-8') as file:
        print(f'Количество строк: {df.shape[0]}\nКоличество столбцов: {df.shape[1]}\n', file=file)
        print(f'Типы данных:\n{df.dtypes}\n', file=file)
        print(f'Число незаполненных ячеек:\n{df.isnull().sum()}\n', file=file)
        stats = df[counting_cols].agg(['mean', 'median', 'std']).T
        print(f"Стандартные характеристики:\n{stats}\n", file=file)
        print('Уникальные значения:', file=file)
        for col in categorical_cols:
            print(df[col].value_counts(), file=file)
            print('\n', file=file)

    print(f'Количество строк: {df.shape[0]}\nКоличество столбцов: {df.shape[1]}\n')
    print(f'Типы данных:\n{df.dtypes}\n')
    print(f'Число незаполненных ячеек:\n{df.isnull().sum()}\n')
    stats = df[counting_cols].agg(['mean', 'median', 'std']).T
    print(f"Стандартные характеристики:\n{stats}\n")
    print('Уникальные значения:')
    for col in categorical_cols:
        print(df[col].value_counts())
        print('\n')