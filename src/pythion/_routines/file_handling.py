from datetime import datetime
from dataclasses import dataclass
import os


@dataclass
class FileSettings:
    name: str
    path: str = '.'
    extension: str = 'csv'
    timestamp: bool = True


def generate_filename(settings: FileSettings) -> str:
    if settings.timestamp:
        now = datetime.now()
        filename = f'{now:%y%m%d}T{now:%H%M}_' + settings.name

    uniqueifier = ''
    complete_path = settings.path + '/' + filename + uniqueifier + '.' + settings.extension

    # If directory exists, make sure file name is unique. Else, create directory(-ies)
    if os.path.exists(settings.path):
        counter = 1
        while os.path.exists(complete_path):
            uniqueifier = f'({counter})'
            counter = counter + 1
            complete_path = settings.path + '/' + filename + uniqueifier + '.' + settings.extension
    else:
        os.makedirs(settings.path)
    print(complete_path)
    return complete_path
