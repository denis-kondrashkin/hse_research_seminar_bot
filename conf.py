AUTHOR_INTENT = 'AUTHOR_INTENT'
ARTICLE_INTENT = 'ARTICLE_INTENT'
SORT_INTENT = 'SORT_INTENT'
MORE_INTENT = 'MORE_INTENT'
START_INTENT = 'START_INTENT'
ABSTRACT_INTENT = 'ABSTRACT_INTENT'
DOWNLOAD_INTENT = 'DOWNLOAD_INTENT'
YEAR_INTENT = 'YEAR_INTENT'

sortings = {
    0: ('relevance', 'descending'),
    1: ('lastUpdatedDate', 'ascending'),
    2: ('lastUpdatedDate', 'descending'),
    3: ('submittedDate', 'ascending'),
    4: ('submittedDate', 'descending'),
}

exit_command = 'q'
cancel_command = 'c'

pipeline_file = "nlu_config_wv.yml"
articles_dir = 'articles'