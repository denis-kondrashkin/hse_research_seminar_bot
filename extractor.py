import re
import spacy
from conf import *

nlp = spacy.load('en_core_web_sm')


def dummy_extract_ents(query, detected_entities):
    return tuple()


def extract_author_ents(query, detected_entities):
    if not detected_entities or not set(e['entity'] for e in detected_entities).issubset({'PERSON', 'ORG'}):
        return tuple()
    else:
        authors = [e['value'].replace("'s", "") for e in detected_entities]
        return tuple(authors)


def extract_article_ents(query, detected_entities):
    keywords = []
    for noun_chunk in nlp(query).noun_chunks:
        if not any(token.dep_ in ('pobj', 'conj') for token in noun_chunk):
            continue
        if any(token.dep_ in ('pobj', 'dobj')
               and token.lemma_ in ('something', 'anything', 'everything',
                                    'script', 'scroll', 'article', 'document', 'text', 'paper', 'publication')
               for token in noun_chunk):
            continue
        chunk = []
        for token in noun_chunk:
            if token.dep_ != 'poss' and token.dep_ != 'det' and token.pos_ != 'PRON':
                chunk.append(token.text)
        if chunk:
            keywords.append(' '.join(chunk))
    return tuple(keywords)


def extract_single_number(query, detected_entities):
    if len(detected_entities) != 1 or detected_entities[0]['entity'] != 'CARDINAL':
        string = query
    else:
        string = detected_entities[0]['value']
    match = re.search("[0-9]+", string)
    return tuple([int(match.group())]) if match else tuple()


def extract_start_ents(query, detected_entities):
    return extract_single_number(query, detected_entities)


def extract_abstract_ents(query, detected_entities):
    return extract_single_number(query, detected_entities)


def extract_download_ents(query, detected_entities):
    return extract_single_number(query, detected_entities)


def extract_year_ents(query, detected_entities):
    return tuple(int(year) for year in re.findall("[0-9]{4}", query))


intent_to_extractor = {
    AUTHOR_INTENT: extract_author_ents,
    ARTICLE_INTENT: extract_article_ents,
    SORT_INTENT: dummy_extract_ents,
    MORE_INTENT: dummy_extract_ents,
    START_INTENT: extract_start_ents,
    ABSTRACT_INTENT: extract_abstract_ents,
    DOWNLOAD_INTENT: extract_download_ents,
    YEAR_INTENT: extract_year_ents
}


def extract_ents(query, intent, detected_entities):
    return intent_to_extractor[intent](query, detected_entities)
