from dbmgr.models import AmazonReview
from nltk import word_tokenize, RegexpParser, pos_tag

def view_data():
    grammar = r"""
        NP: {<DT>?<JJ>*<NN|NNS>}
            {<NNP|NNPS>+}
    """
    
    cp = RegexpParser(grammar)

    data = AmazonReview.objects.all()[118].reviewText
    print(data)
    text = word_tokenize(data)
    sentence = pos_tag(text)
    
    result = cp.parse(sentence)
    print(result)
    result.draw()

    