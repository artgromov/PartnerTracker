from my_creds import google as creds
import gspread
import pickle
import progressbar
from partner_tracker.updaters import update
from partner_tracker.searchers import search

fields = ['rating',
          'state',
          'name',
          'notes',
          'description',
          'country',
          'city',
          'org',
          'club',
          'trainer',
          'class_st',
          'class_la',
          'birth',
          'height',
          'weight',
          'links',
          'images',
          'videos',
          'phone',
          'email',
          'goal',
          'expectations',
          'competition_last_date',
          'change_org',
          'change_club',
          'change_trainer',
          'schedule_practice',
          'schedule_coached_practice',
          'schedule_competition',
          'schedule_training_time',
          ]


def check_header():
    cols_exist = len(wks.row_values(1))
    cols_needed = len(fields)
    if cols_needed > cols_exist:
        wks.add_cols(cols_needed - cols_exist)

    cell_list = wks.range(alnum_range(1, 1, 1, len(fields)))
    if cell_list[0].value != fields[0]:
        for num, cell in enumerate(cell_list):
            cell.value = fields[num]

        wks.update_cells(cell_list)


states_conv = ['new',
               'new',
               'contact attempt',
               'contact success',
               'testing',
               'additional testing',
               'ignored',
               'no answer'
               ]


def import_from_old_format(data, old_list):
    for old_data in old_list:
        if data['links'][0] == old_data.links[0]:
            data['notes'] = old_data.notes
            data['state'] = states_conv[old_data.state.id]
            break

    return data


def convert_lists(data):
    new_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            new_data[key] = '\n'.join(value)
        else:
            new_data[key] = value
    return new_data


def upload_partner(data):
    row = get_next_row()
    cell_list = wks.range(alnum_range(row, 1, row, len(fields)))
    for num, cell in enumerate(cell_list):
        key = fields[num]
        try:
            value = data[key]
        except KeyError:
            value = '-'

        cell.value = value

    wks.update_cells(cell_list)


def get_next_col():
    cols_total = wks.row_values(1)
    cols_filled = [i for i in cols_total if i != '']
    if cols_total == cols_filled:
        wks.add_cols(10)
    return len(cols_filled) + 1


def get_next_row():
    rows_total = wks.col_values(1)
    rows_filled = [i for i in rows_total if i != '']
    if rows_total == rows_filled:
        wks.add_rows(10)
    return len(rows_filled) + 1


def alnum(row, col):
    if row <= 0 or col <= 0:
        raise IndexError

    zero_chr = 65
    chars = []

    def walk(number):
        number -= 1
        div = int(number/26)
        mod = number % 26
        chars.append(chr(zero_chr + mod))

        if div != 0:
            walk(div)

    walk(col)

    col = ''.join(reversed(chars))

    return '%s%s' % (col, row)


def alnum_range(row1, col1, row2, col2):
    return '%s:%s' % (alnum(row1, col1), alnum(row2, col2))


if __name__ == '__main__':
    print('Authorizing access to google spreadsheet.')
    gc = gspread.authorize(creds)
    wks = gc.open('Partners').sheet1

    print('Checking header.')
    check_header()

    try:
        print('Loading file "gsheets.p" with already searched links.')
        with open('gsheets.p', 'rb') as file:
            links = pickle.load(file)
    except FileNotFoundError:
        print('File "gsheets.p" not found.')
        links = []

#    print('Loading file with old formatted data')
#    with open('data.p', 'rb') as file:
#        old_list = pickle.load(file).partners

    print('Searching and uploading new items.')
    new_links = search()
    new_links_len = len(new_links)
    with progressbar.ProgressBar(max_value=new_links_len) as bar:
        for num, link in enumerate(new_links):
            if link not in links:
                links.append(link)
                data = update(link)
                data['state'] = 'new'
                #data = import_from_old_format(data, old_list)
                data = convert_lists(data)
                upload_partner(data)
            bar.update(num)

    print('Saving searched links to file.')
    with open('gsheets.p', 'wb') as file:
        pickle.dump(links, file)
