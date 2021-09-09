import json
import os
import datetime as dt
from collections import Counter
import matplotlib.image as image


def get_json_dict(jsonpath):
    f = open(jsonpath)
    if not f:
        return print("Failed to open file", jsonpath)
    return json.load(f)

def get_emojis_from_dicts(jsondicts):
    reactdict = dict()
    for jd in jsondicts:
        reactions = jd.get('reactions')
        if reactions:
            for reaction in reactions:
                name = reaction['name']
                count = reaction['count']
                if not name in reactdict:
                    reactdict[name] = 0
                reactdict[name] += count
    return reactdict
    
def get_emojis_from_file(filename):
    #print("Process file", filename)
    ds = get_json_dict(filename)
    return get_emojis_from_dicts(ds)

def get_pathinfo_from_file(path):
    [ignore, root, subroot, channel, filename] = path.split('/')
    return [root, subroot, channel, filename]

def get_depth_from_path(path):
    return path.count('/')

def get_emojis_from_files(files):
    emojidict = Counter(dict())

    for file in files:
        emojis = Counter(get_emojis_from_file(file))
        emojidict = emojidict + emojis
    return emojidict

def get_folders_below(path):
    folders = []
    for r, d, f in os.walk(path):
        for dir in d:
            folders.append(dir)
    return folders

def get_files_below(path, ext):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if ext in file:
                files.append(os.path.join(r, file))
    return files

def get_images(emojinames):
    emojidir = 'emojis'
    emojifiles = os.listdir(emojidir)
    imgs = []
    for name in emojinames:
        for file in emojifiles:
            if name in file:
                imgs.append(image.imread(emojidir + '/' + file))
    return imgs

def get_datestr_from_datetime(datetime):
    # Converts a class into a string and removes non-dates
    return datetime.__str__().split(' ')[0]

def get_datetime_from_filename(filename, format):
    # Format dddd-mm-dd.json -> datetime
    date = filename.split('.')[0]
    return dt.datetime.strptime(date, format)