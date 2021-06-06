allowed_chars = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'æ', 'ø', 'å']
end_chars = [ '.', ',', '!', '?' ]

def filter_text(string, borings):
    string = string.strip()
    string = string.lower()
    string = filter_escapes(string)
    string = filter_boring(string, borings)
    return filter_non_ascci(string)

def filter_escapes(string):
    escaped_string = ""
    escape = 0
    for c in string:
        if c == '<':
            escape = 1
        elif c == '>':
            escape = 0
        else:
            if not escape:
                escaped_string += c
    return escaped_string

def filter_boring(string, borings):
    strings = string.split()
    for string, i in zip(strings, range(len(strings))):
        if string in borings:
            strings[i] = ""
    return " ".join(strings)

def filter_non_ascci(string):
    strings = string.split()
    for string, i in zip(strings, range(len(strings))):
        for char in string:
            if char in end_chars:
                strings[i] = string[:-1]
            if not char in allowed_chars:
                strings[i] = ""
    return " ".join(strings)

def print_dict_as_code_strings(d):
    for key in d:
        print("\'" + key + "\',")