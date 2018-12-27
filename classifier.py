import warnings
import logging
from sklearn.exceptions import DataConversionWarning, ConvergenceWarning

warnings.filterwarnings(action='ignore', category=DataConversionWarning)
warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
warnings.filterwarnings(action='ignore', category=DeprecationWarning)
warnings.filterwarnings(action='ignore', category=UserWarning)
warnings.filterwarnings(action='ignore', category=FutureWarning)

from conf import *
from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu.model import Interpreter
from rasa_nlu import config

import tensorflow

logging.getLogger('tensorflow').setLevel(logging.ERROR)

training_data = load_data('data/')
trainer = Trainer(config.load(pipeline_file))
trainer.train(training_data)
model_directory = trainer.persist('./models/')

classifier = Interpreter.load(model_directory)


def classify_intent(query):
    result = classifier.parse(query)
    intent = result['intent']['name']
    score = round(result['intent']['confidence'], 3),
    detected_entities = result['entities']
    return intent, score, detected_entities
