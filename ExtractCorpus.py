#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import fnmatch
import random
import linecache
import json
import re
import MeCab


LIMIT_BYTES = (100*1000*1000)
TAGGER = MeCab.Tagger('-Owakati')
REGEX_TWO_NEW_LINES = re.compile('\\n\\n')
random.seed(42)


def usage():
    print('python3 ExtractCorpus.py wiki_dir corpus_file_name')
    print


def list_files(dirname):
    matches = []
    for root, _, filenames in os.walk(dirname):
        for filename in fnmatch.filter(filenames, 'wiki*'):
            matches.append(os.path.join(root, filename))

    return sorted(matches)


def linecount(filename=''):
    count = 0
    thefile = open(filename, 'r')
    while 1:
        buffer = thefile.read(65536)
        if not buffer:
            break
        count += buffer.count('\n')
    return count


def access_wikipedia_articles(wiki_dir=''):
    wiki_files = list_files(wiki_dir)
    each_file_info = {}
    sum_lines = 0
    for wiki in wiki_files:
        print('phase1: count wiki_file=%s lines...' % wiki)
        lnum = linecount(filename=wiki)
        each_file_info[wiki] = (lnum, sum_lines)
        sum_lines += lnum

    return wiki_files, each_file_info, sum_lines


def make_indices(wiki_files=[], each_file_info={}, lines=0):
    indices = {}
    wiki_file = wiki_files[0]

    file_index = 0
    content_line_position = 0
    content_length = 0
    for idx in range(lines):
        indices[idx] = {'wiki_file': wiki_file,
                        'line': content_line_position + 1}
        if content_line_position == 0:
            wiki_file = wiki_files[file_index]
            print('phase2: numbering in %s' % wiki_file)
            content_length, _ = each_file_info[wiki_file]
        content_line_position += 1
        if content_line_position == content_length:
            content_line_position = 0
            file_index += 1

    return indices


def get_json(index=-1, filename='', lineno=0):
    li = linecache.getline(filename, lineno)
    js = json.loads(li)
    js['corpus_id'] = index
    text = js['text']
    return js, text


def wakachigaki(text=u''):
    text2 = text.strip()
    text3 = TAGGER.parse(text2).strip()
    return text3


def length_of_unicode_string(stri=''):
    return len(stri.encode('utf-8'))


def make_corpus_and_metainfo(indices={}, sequence=[]):
    corpus = []
    metainfo = []
    total_bytes = 0
    for idx, random_index in enumerate(sequence):
        if idx % 100 == 0:
            print('phase3: write %d...' % idx)
        target = indices[random_index]
        js, text = get_json(
            index=idx, filename=target['wiki_file'], lineno=int(target['line']))
        j_lines = re.split(REGEX_TWO_NEW_LINES, text)
        new_line_list = []
        for each_line in j_lines:
            new_text = wakachigaki(each_line)
            new_line_list.append(new_text)

        add_line = u' '.join(new_line_list)
        add_line_bytes = length_of_unicode_string(stri=add_line)
        total_bytes += add_line_bytes
        if total_bytes >= LIMIT_BYTES:
            total_bytes -= add_line_bytes
            break
        corpus.append(add_line)
        metainfo.append(js)

    print('total corpus length = %d Bytes, = %f KiBytes, = %f MiBytes'
          % (total_bytes, total_bytes / 1024.0, total_bytes / (1024.0*1024.0)))

    return '\n'.join(corpus), metainfo


def main(wiki_dir='./extracted2', corpus_file_name='ja.text8', metainfo_file='info.json'):
    wiki_files, info, lines = access_wikipedia_articles(wiki_dir=wiki_dir)
    indices = make_indices(wiki_files=wiki_files,
                           each_file_info=info, lines=lines)
    seq = [x for x in range(lines)]
    random.shuffle(seq)
    corpus, metainfo = make_corpus_and_metainfo(indices=indices, sequence=seq)
    with open(corpus_file_name, 'w') as fpx:
        fpx.write(corpus)
    fi = open(metainfo_file, "w")
    json.dump(metainfo, fi)
    fi.close()
    return True


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
        quit()

    dirname = sys.argv[1]
    corpus_name = sys.argv[2]
    tf = main(wiki_dir=dirname, corpus_file_name=corpus_name)
