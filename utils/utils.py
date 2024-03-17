from datetime import datetime


def string_to_bool(string_data: str):
    clean_string = string_data.strip().capitalize()
    if clean_string == "True":
        return True
    return False


def trello_date_to_python_date(trello_date):
    if trello_date:
        python_date_time = datetime.strptime(trello_date.split("T")[0], '%Y-%m-%d')
        return python_date_time.date()
    return None


def get_required_batches(data: list, batch_size):
    mod = len(data) % batch_size
    quotient = int(len(data) / batch_size)
    if quotient:
        if mod:
            return int(len(data) / batch_size) + 1
        return int(len(data) / batch_size)
    return 1


def date_to_string(python_date, string_format="%d.%m.%Y"):
    return python_date.strftime(string_format)


def string_to_date(date_string, string_format="%d.%m.%Y"):
    try:
        return datetime.strptime(date_string, string_format)
    except Exception as err:
        return None
