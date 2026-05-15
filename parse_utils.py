import re
from enum import Enum

# Looks for something surrounded by quotation marks and puts it into group 1
string_pattern = re.compile(r'"(.*)"')

# Strips the string of its quotation marks
def parse_string(value: str) -> str:
    # If the value is surrounded by quotation marks, return what's inside
    string_match = string_pattern.search(value)
    if string_match:
        return string_match.group(1)

    # Otherwise, manually strip the string and return
    return value.strip()

# Turns a string ("True" or "False") into a bool
def parse_bool(value: str) -> bool:
    match value.strip().lower():
        case 'true':
            return True
        case 'false':
            return False
        case _:
            raise ValueError(f'Cannot parse {value} as bool')

# Turns a string into an enum member
def parse_enum(value: str, EnumCls: type[Enum]) -> Enum:
    for member in EnumCls:
        if value.strip().lower() == member.name.lower():
            return member

    raise ValueError(f'Cannot parse {value} as {EnumCls}')
