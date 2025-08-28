import os
import gdown

baseURL = 'https://drive.google.com/uc?id='

# ID'S of the Oracle's Elixir CSV's in gdrive
ids = {
    2014: '12syQsRH2QnKrQZTQQ6G5zyVeTG2pAYvu',
    2015: '1qyckLuw0-hJM8XqFhlV9l1xAbr3H78T_',
    2016: '1muyfpaIqk8_0BFkgLCWXDGNgWSXoPBwG',
    2017: '11fx3nNjSYB0X8vKxLAbYOrS2Bu6avm9A',
    2018: '1GsNetJQOMx0QJ6_FN8M1kwGvU_GPPcPZ',
    2019: '11eKtScnZcpfZcD3w3UrD7nnpfLHvj9_t',
    2020: '1dlSIczXShnv1vIfGNvBjgk-thMKA5j7d',
    2021: '1fzwTTz77hcnYjOnO9ONeoPrkWCoOSecA',
    2022: '1EHmptHyzY8owv0BAcNKtkQpMwfkURwRy',
    2023: '1XXk2LO0CsNADBB1LRGOV5rUpyZdEZ8s2',
    2024: '1IjIEhLc9n8eLKeY-yh_YigKVWbhgGBsN',
    2025: '1v6LRphp2kYciU4SXp0PCjEMuev1bDejc',
}


def update_all_years():
    for year in ids.keys():
        update_year(year=year)


def update_year(year: int = 2025):
    base_path = f'../../Datasets/{year}.csv'
    if os.path.exists(base_path):
        os.remove(base_path)
    gdown.download(baseURL+ids[year], base_path)


