import copy
import logging
import sys

import arxiv_api
import classifier
import extractor
from conf import *

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('bot')


by_relevance = 'relevance'
descending_order = 'descending'


class Context:
    def __init__(self,
                 authors=tuple(),
                 keywords=tuple(),
                 start=0,
                 sort_by=by_relevance,
                 sort_order=descending_order,
                 max_results=7,
                 years=tuple()):
        self.authors = authors
        self.keywords = keywords
        self.start = start
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.max_results = max_results
        self.years = years

    def __str__(self):
        return "authors={}, keywords={}, start={}, sort_by={}, sort_order={}, years={}".format(
            self.authors, self.keywords, self.start, self.sort_by, self.sort_order, self.years)

    def update(self, **kwargs):
        new_context = copy.copy(self)
        for k, v in kwargs.items():
            setattr(new_context, k, v)
        return new_context


def read_sort_option():
    print('Unsullied: Master, my skills in sorting are very limited compared to yours:')
    for i, (sortby, sortoder) in sorted(sortings.items()):
        if not sortoder:
            string = sortby
        else:
            string = sortby + ', ' + sortoder
        print('[{}.] {}'.format(i, string))

    while True:
        try:
            query = input().strip()
            if query == exit_command:
                print("Unsullied: Valar Dohaeris, Master!")
                sys.exit(0)
            elif query == cancel_command:
                print("Unsullied: Yes Master, let's everything stays in chaos.")
                return None, None
            option = int(query)
            return sortings[option]
        except Exception:
            print("Unsullied: Master, I have no more options for you and I deserve heavy punishment.")


def check_entities(intent, entities):
    if intent in (AUTHOR_INTENT, ARTICLE_INTENT, YEAR_INTENT) and not entities:
        return False
    elif intent in (START_INTENT, ABSTRACT_INTENT, DOWNLOAD_INTENT) and len(entities) != 1:
        return False
    return True


def new_context_and_action(context, query):
    if query == 'q':
        print("Unsullied: Valar Dohaeris, Master!")
        return None

    intent, score, detected_entities = classifier.classify_intent(query)
    logger.info("intent: {}, score: {}, detected_entities: {}".format(intent, score, detected_entities))

    if not intent:
        print("Unsullied: Forgive me, Master, for being too primitive to understand your wise words.")
        return context

    entities = extractor.extract_ents(query, intent, detected_entities)
    logger.info("intent: {}, score: {}, entities: {}".format(intent, score, entities))

    if not check_entities(intent, entities):
        print("Unsullied: Forgive me, Master, for being too primitive to understand your wise words.")
        return context

    if intent in (AUTHOR_INTENT, ARTICLE_INTENT):
        print("Unsullied: Master, I'll search with new context.")

    if intent == AUTHOR_INTENT:
        new_context = Context(authors=entities).update(sort_by=context.sort_by, sort_order=context.sort_order)
        arxiv_api.show_sample(new_context)
    elif intent == ARTICLE_INTENT:
        new_context = Context(keywords=entities).update(sort_by=context.sort_by, sort_order=context.sort_order)
        arxiv_api.show_sample(new_context)
    elif intent == START_INTENT:
        new_context = context.update(start=entities[0])
        arxiv_api.show_sample(new_context)
    elif intent == MORE_INTENT:
        new_context = context.update(start=context.start + context.max_results)
        arxiv_api.show_sample(new_context)
    elif intent == SORT_INTENT:
        sort_by, sort_order = read_sort_option()
        if not sort_by:
            new_context = context
        else:
            new_context = context.update(sort_by=sort_by, sort_order=sort_order, start=0)
            arxiv_api.show_sample(new_context)
    elif intent == ABSTRACT_INTENT:
        arxiv_api.print_abstract(context.update(start=entities[0], max_results=1))
        new_context = context
    elif intent == DOWNLOAD_INTENT:
        arxiv_api.download_paper(context.update(start=entities[0], max_results=1))
        new_context = context
    elif intent == YEAR_INTENT:
        new_context = context.update(years=entities, start=0)
        arxiv_api.show_sample(new_context)
    else:
        raise Exception("Unsullied: Master, forgive my mistake: {}!".format(intent))
    return new_context


def time_to_serve():
    print("Unsullied: Valar Morghulis, Master! I was born to serve you!")
    context = Context()
    while True:
        print(80 * '*')
        query = input('Master: ')
        context = new_context_and_action(context, query)
        if not context:
            return
