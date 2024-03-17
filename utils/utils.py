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
    quotient = int(len(data)/batch_size)
    if quotient:
        return int(len(data)/batch_size) + mod
    return 1
