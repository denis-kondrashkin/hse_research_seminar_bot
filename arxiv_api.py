import datetime
import logging
import os
import re
import urllib.request

import feedparser
import progressbar

from conf import *

logger = logging.getLogger('bot')

ARXIV_API_BASE_QUERY = 'http://export.arxiv.org/api/query?'


def format_api_query(context):
    query_params = ''

    api_keywords = []
    for keywords in context.keywords:
        keywords = '%22' + re.sub('\s+', '+', keywords) + '%22'
        api_keywords.append(keywords)
    if api_keywords:
        query_params += '%28all:' + '+OR+'.join(api_keywords) + '%29'

    author_phrases = []
    for author in context.authors:
        author = '%22' + re.sub('\s+', '+', author) + '%22'
        author_phrases.append(author)
    if author_phrases:
        if query_params:
            query_params += '+AND+'
        query_params += '%28au:' + '+AND+'.join(author_phrases) + '%29'

    years = []
    for year in context.years:
        years.append('submittedDate:[' + str(year) + '+TO+' + str(year) + '12312359' + ']')
    if years:
        if query_params:
            query_params += '+AND+'
        query_params += '%28' + '+OR+'.join(years) + '%29'

    api_query = ARXIV_API_BASE_QUERY + '&search_query=' + query_params
    api_query += '&start={}&sortBy={}&sortOrder={}&max_results={}'.format(
        context.start, context.sort_by, context.sort_order, context.max_results)
    return api_query

def call_api(context):
    api_query = format_api_query(context)
    logger.info(api_query)
    return feedparser.parse(api_query)

def format_title(entry):
    title = entry['title']
    authors = ', '.join([a['name'] for a in entry['authors']])
    year = datetime.datetime.strptime(entry['published'], '%Y-%m-%dT%H:%M:%SZ').year
    return "{}. {}. {}.".format(title, authors, year)

def show_sample(context):
    response = call_api(context)
    start = int(response['feed']['opensearch_startindex'])
    totalresults = int(response['feed']['opensearch_totalresults'])
    logger.info("start: {}, totalresults: {}".format(start, totalresults))
    if not totalresults:
        print("Unsullied: I failed to find anything, Master, and I'm ready for execution.")
    elif start == totalresults:
        print("Unsullied: No more scrolls left, Master.")
    else:
        if totalresults == 1:
            print('Unsullied: There is only one script in our library, Master:'.format(totalresults))
        else:
            print('Unsullied: There are {} scrolls in our library, Master. I brought a few:'.format(totalresults))
        for i, e in enumerate(response['entries']):
            print()
            print("[{}.] {}".format(start + i, format_title(e)))
    print()

def print_abstract(context):
    response = call_api(context)
    e = response['entries'][0]
    print('Unsullied:')
    print(format_title(e))
    print('\t\t\tAbstract.')
    print(e['summary'])
    print()

def download_paper(context):
    print("Unsullied: It will take few seconds, Master.")

    response = call_api(context)
    e = response['entries'][0]
    href = [link for link in e['links'] if link['type'] == 'application/pdf'][0]['href']
    logger.info("loading paper from {}".format(href))

    if not os.path.exists(articles_dir):
        os.mkdir(articles_dir)
    elif not os.path.isdir(articles_dir):
        print('Unsullied: I cant store required paper: file articles exists instead of directory articles')
        return
    filename = format_title(e)
    filename = re.sub('[:;\n\r<>\[\]{}/\\\+=@#%~`*]', ' ', filename)
    filename = filename[:80]
    if filename[-1] != '.':
        filename += '.'
    filename = '{}\{}pdf'.format(articles_dir, filename)

    bar = []

    def show_progress(block_num, block_size, total_size):
        if not bar:
            bar.append(progressbar.ProgressBar(maxval=total_size))
        downloaded = block_num * block_size
        if downloaded < total_size:
            bar[0].update(downloaded)
        else:
            bar[0].finish()

    urllib.request.urlretrieve(href, filename, show_progress)

    os.system("""start "" /max "{}" """.format(filename))
