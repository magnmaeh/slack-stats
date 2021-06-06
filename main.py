# Plotting tools
import matplotlib.pyplot as plt
import matplotlib.image as image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Time tools
import datetime as dt

from wordcloud import WordCloud
from collections import Counter

# Own functions
from getter import *
from filter import filter_text

borings = get_boring_words()

def __main__():
    #text = get_wcstr_from_folder("./data")
    #text = filter_text(text, borings)

    #emojis = get_emojis_from_folder("./data/selfiesat-techtalk")
    emojidates = get_emojis_date_from_folder("./data")
    emojidates_sorted = sort_tuple_list(emojidates)

    emojidates_sorted_combined = combine_equal_dates(emojidates_sorted)
    emojidates_sorted_combined_cumulative = calculate_cumulative(emojidates_sorted_combined)
    
    emojidates_sorted_combined_cumulative = remove_non_winners(emojidates_sorted_combined_cumulative, 2)
    winners = emojidates_sorted_combined_cumulative[-1][0]
    print(winners)
    
    plot_cumulative(emojidates_sorted_combined_cumulative, winners)

def sort_tuple_list(tuplst):
    fmat = "%Y-%m-%d"

    l = len(tuplst)
    for i in range(0, l):
        for j in range(0, l - i - 1):
            tup1 = tuplst[j]
            tup2 = tuplst[j + 1]
            if tup1[1] > tup2[1]:
                temp = tuplst[j]
                tuplst[j]= tuplst[j + 1]
                tuplst[j + 1]= temp
    return tuplst
                
def combine_equal_dates(emojidates):
    combined = []
    combined_dict = Counter(dict())

    cur_date = emojidates[0][1]
    for i in range(len(emojidates)):
        if cur_date != emojidates[i][1]:
            combined.append((combined_dict, cur_date))
            cur_date = emojidates[i][1]
            combined_dict = Counter(dict())
        else:
            combined_dict = combined_dict + Counter(emojidates[i][0])
    return combined

def calculate_cumulative(emojidates):
    cumulative = []
    cumulative_dict = Counter(dict())

    cur_date = emojidates[0][1]
    for emojidate in emojidates:
        cumulative_dict = cumulative_dict + emojidate[0]
        cur_date = emojidate[1]
        cumulative.append((cumulative_dict, cur_date))
    return cumulative

def remove_non_winners(emojidates, numwinners):
    winners = dict()
    last_date = emojidates[-1]
    emdict = last_date[0]
    emdict = dict(sorted(emdict.items(), key=lambda item: item[1], reverse=True))
    for key, i in zip(emdict, range(numwinners)):
        winners[key] = emdict[key]
        if i == numwinners:
            break

    new_emojidates = []
    for emdate in emojidates:
        emdict = emdate[0]
        emdict = {k:v for k,v in emdict.items() if k in winners}    
        new_emojidates.append((emdict, emdate[1]))
    
    return new_emojidates

def plot_cumulative(emojidates, emojiwinners):
    imgs = get_images(emojiwinners)
    fig, ax = plt.subplots()
    for emdate in emojidates:
        emdict = emdate[0]
        for em, img in zip(emdict, imgs):
            ax.plot(emdate[1], emdict[em])
            plot_images(emdate[1], emdict[em], img, ax, 3500)
    plt.grid(True)
    plt.show()

def plot_images(x, y, image, ax, size):
    area = image.shape[0] * image.shape[1]
    sz = area ** (1/2)
    im = OffsetImage(image, zoom=size/sz/ax.figure.dpi)
    im.image.axes = ax

    ab = AnnotationBbox(im, (x, y), frameon=False, pad=0.0)

    ax.add_artist(ab)


if __name__ == "__main__":
    __main__()