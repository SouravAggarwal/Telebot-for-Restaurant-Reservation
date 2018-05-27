import os
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import config as c

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = c.AUTH_FILE

client = language.LanguageServiceClient()


def nlp_text(text):
    result = {}
    client = language.LanguageServiceClient()

    document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)

    sentiment = client.analyze_sentiment(document=document).document_sentiment
    result["sentiment"] = {"magnitude": sentiment.magnitude, "score": sentiment.score}

    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
    arr = []
    words = []
    for entity in entities:
        if __name__ == "__main__":
            print('=' * 20)
            print(u'{:<16}: {}'.format('name', entity.name))
            print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
            print(u'{:<16}: {}'.format('metadata', entity.metadata))
            print(u'{:<16}: {}'.format('salience', entity.salience))

        arr.append({"name": entity.name, "type": entity_type[entity.type], "salience": entity.salience})
        words.append(str(entity.name).lower())
    result["entity"] = arr
    result["wordslist"] = words

    return ((result))


if __name__ == "__main__":
    print(nlp_text(u"Hello, it's me"))
