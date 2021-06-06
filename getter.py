import json
import os
import datetime as dt
from collections import Counter
import matplotlib.image as image

testfile = "data/selfiesat-techtalk/2021-04-21.json"
extract_data = ['text']
emojinames = [ '' ]

def get_json_dict(jsonpath):
    f = open(jsonpath)
    if not f:
        return print("Failed to open file", jsonpath)
    return json.load(f)

def get_text_from_dicts(jsondicts, keys):
    text = ""
    for jd in jsondicts:
        for key in list(jd.keys()):
            if key in keys:
                text += jd[key]
    return text

def get_emojis_from_dicts(jsondicts):
    reactdict = dict()
    for jd in jsondicts:

        # Get reactions from posts
        try:
            for reaction in jd['reactions']:
                name = reaction['name']
                count = reaction['count']
                if not name in reactdict:
                    reactdict[name] = 0
                reactdict[name] += count
        except:
            pass

        # Get emojis from text (must use rich text for this)
        try:
            for elem in jd['blocks'][0]['elements'][0]['elements']:
                try:
                    if elem['type'] == 'emoji':
                        name = elem['name']
                        if not name in reactdict:
                            reactdict[name] = 0
                        reactdict[name] += 1
                except:
                    pass
        except:
            pass
    return reactdict

#def strings_to_dictionary(strings):
#    strings = strings.split()
#    d = dict()
#    for i in range(len(strings)):
#        word = strings[i]
#        if strings[i] in d:
#            d[word] += 1
#        else:
#            d[word] = 1
##    d = dictionary_filter_boring(d)
#    return dict(sorted(d.items(), key=lambda item: item[1], reverse=True))

#def dictionary_filter_boring(d):
#    for key in d:
#        if d[key] <= 1:
#            d[key] = 0
#        elif key in borings:
#            d[key] = 0
#    return { x : y for x, y in d.items() if y != 0 }

def get_wcstr_from_file(filename):
    print("Process file", filename)
    ds = get_json_dict(filename)
    return get_text_from_dicts(ds, extract_data)
    
def get_emojis_from_file(filename):
    print("Process file", filename)
    ds = get_json_dict(filename)
    return get_emojis_from_dicts(ds)

def get_wcstr_from_folder(foldername):
    wcstr = ""

    files = get_files_below(foldername, '.json')
    for file in files:
        wcstr += get_wcstr_from_file(file)
    
    return wcstr

def get_emojis_from_folder(foldername):
    emojidict = Counter(dict())

    files = get_files_below(foldername, '.json')
    for file in files:
        emojis = Counter(get_emojis_from_file(file))
        emojidict = emojidict + emojis
    return emojidict

def get_emojis_date_from_folder(foldername):
    emoji_dates = []

    files = get_files_below(foldername, '.json')
    for file in files:
        emojis = get_emojis_from_file(file)
        date = file[-6:-16:-1][::-1]
        date = dt.datetime.strptime(date, "%Y-%m-%d")
        emoji_dates.append((emojis, date))
    return emoji_dates

def get_boring_words():
    words = []
    with open("boring.txt", "r") as f:
        for line in f:
            words.append(line[:-1])
    return words

def get_files_below(path, ext):
    files = []
    for r, d, f in os.walk(os.getcwd()):
        for file in f:
            if ext in file:
                files.append(os.path.join(r, file))
    return files

def get_images(emojinames):
    imgs = []
    for name, i in zip(emojinames, range(len(emojinames))):
        imgs.append(image.imread("emojis/" + name + ".jpg"))
    return imgs