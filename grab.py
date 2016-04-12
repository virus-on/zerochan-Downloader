# -*- coding: UTF-8 -*-

import grab
import urllib
import time
import os
import argparse
import warnings

warnings.filterwarnings("ignore")  # I used old instruction so there can be


def next_page(flink):
    global max_page, i, sub_link, g
    g.go(flink)
    time.sleep(0.4)
    if max_page != i: sub_link = g.xpath('//p[@class="pagination"]/a[@rel="next"]').get('href')


def get_img(img_link_list):
    for x in img_link_list:
        img_url = str(x.get('src'))
        img_url = img_url.replace('.240.', '.full.')
        img_url = img_url.replace('s3.', 'static.')
        img = urllib.urlopen(img_url).read()
        img_name = img_url.split('.')[len(img_url.split('.')) - 2] + '.' + img_url.split('.')[
            len(img_url.split('.')) - 1]
        if os.path.isfile(img_name): os.remove(img_name)
        f = open(img_name, "wb")
        f.write(img)
        f.close()
        time.sleep(0.4)


def check_img(img_link_list):
    for x in img_link_list:
        img_url = str(x.get('src'))
        img_url = img_url.replace('.240.', '.full.')
        img_url = img_url.replace('s3.', 'static.')
        img_name = img_url.split('.')[len(img_url.split('.')) - 2] + '.' + img_url.split('.')[
            len(img_url.split('.')) - 1]
        # if exists, go on to the next step
        if (os.path.isfile(img_name) == False):
            print('Image ' + img_name + ' was not found, receiving')
            img = urllib.urlopen(img_url).read()
            f = open(img_name, "wb")
            f.write(img)
            f.close()
            time.sleep(0.4)


def create_parser():
    parser = argparse.ArgumentParser(
            prog='grab.py',
            epilog='''(c) April 2016.''')

    parser.add_argument('link', help='URL WITHOUT parameters like http://www.zerochan.net/Kantai+Collection')
    parser.add_argument('-m', '--max', type=int, default=-1, help='Max page (All(default))')
    parser.add_argument('-t', '--time', default='-1',
                        help='Sort by popularity and by time(1 - Last week | 2 - Last 3 month(default) | 3 - All time)')
    parser.add_argument('-b', '--beginning', type=int, default=-1, help='Begin grab from N page')
    parser.add_argument('-c', '--check', type=int, default=-1,
                        help='Check weather all images was downloaded, should be used after main grab has ended')
    parser.add_argument('-d', '--mode', default='-1', help='Mode (1 - Last(default) | 2 - Popular | 3 - Random)')
    parser.add_argument('-s', '--size', default='-1',
                        help='Size of images (1 - All(default) | 2 - Bigger and better | 3 - Large only)')

    return parser


def switch_mode():
    global args
    if int(args.time) > 0:  # Sort by popularity or by mode?
        return {
            '1': 's=fav&t=1',  # Last week
            '3': 's=fav&t=0'  # All time
        }.get(args.time, 's=fav&t=2')

    return {
        '2': 's=fav',  # Popular last 3 month
        '3': 's=random'  # Random pics
    }.get(args.mode, 's=id')


def switch_size():
    return {
        '2': 'd=1',  # Bigger and better
        '3': 'd=2'  # BIG and HUGE only
    }.get(args.size, 'd=0')


# Initializing grab and parser
g = grab.Grab()
g.setup(connect_timeout=50, timeout=50)
parser = create_parser()
args = parser.parse_args()

# Receiving link
link = args.link
sub_link = '?' + switch_mode() + '&' + switch_size()

# Receiving page diapason and setting cycle var
max_page = args.max
if max_page < 0:  # If not specified, will receive automatically
    g.go(link + sub_link)
    max_page = int(g.xpath_text('//p[@class="pagination"]').split(' ')[3])
starting_point = args.beginning
i = 1

# Skipping pages
while i <= starting_point:
    try:
        next_page(link + sub_link)
        print ('skipping page number %i' % i)
        i += 1
    except:
        print('Error while skipping page %i, will try again in 10 seconds' % i)
        time.sleep(10)
        continue

# Check images
if args.check > 0:
    while i <= max_page:
        try:
            next_page(link + sub_link)
            check_img(g.xpath_list('//li/a/img'))
        except:
            print('Error on %i iteration, will try again in 10 seconds' % i)
            time.sleep(10)
            continue
        print('Check page number %i successful' % i)
        i += 1
    print('Done')
    exit()

# Getting images
while i <= max_page:
    try:
        next_page(link + sub_link)
        get_img(g.xpath_list('//li/a/img'))
    except:
        print('Error on %i iteration, will try again in 10 seconds' % i)
        time.sleep(10)
        continue
    print('Grab page number %i successful' % i)
    i += 1

print('Done')
exit()
