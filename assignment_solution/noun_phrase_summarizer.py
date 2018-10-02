import pytextrank as ptr
from dbmgr.models import AmazonReview
import json
from sys import argv

stage0 = "assignment_solution/stages/stage0.json"
stage1 = "assignment_solution/stages/stage1.json"
stage2 = "assignment_solution/stages/stage2.json"
stage3 = "assignment_solution/stages/stage3.json"

def generate_json_data(sample):
    data = AmazonReview.objects.all()[sample:sample+1]
    open(stage0, "w").close()
    with open(stage0, "a") as outfile:
        for counter, d in enumerate(data):
            new_review = {"id":d.asin, "text": d.reviewText}
            json.dump(new_review, outfile)
            outfile.write("\n")
    print(d.reviewText)

def generate_noun_phrases():
    with open(stage1, "w") as f:
        for graf in ptr.parse_doc(ptr.json_iter(stage0)):
            f.write("%s\n" % ptr.pretty_print(graf._asdict()))
            # print(ptr.pretty_print(graf))

def collect_and_normalize(draw):
    graph, ranks = ptr.text_rank(stage1)
    ptr.render_ranks(graph, ranks)
    if draw:
        import networkx as nx
        import pylab as plt
        nx.draw(graph, with_labels=True) 
        plt.show()

    with open(stage2, 'w') as f:
        for rl in ptr.normalize_key_phrases(stage1, ranks):
            f.write("%s\n" % ptr.pretty_print(rl._asdict()))
            # print(ptr.pretty_print(rl))

def calculate_weights():
    kernel = ptr.rank_kernel(stage2)

    with open(stage3, 'w') as f:
        for s in ptr.top_sentences(kernel, stage1):
            f.write(ptr.pretty_print(s._asdict()))
            f.write("\n")
            # print(pytextrank.pretty_print(s._asdict()))

def extract_key_phrases():
    phrases = ", ".join(set([p for p in ptr.limit_keyphrases(stage2, phrase_limit=12)]))
    print("Key phrases:")
    print(phrases)

def test(start, end, draw=False):
    for i in range(start, end):
        print("reviewText " + str(i) + ": ")
        generate_json_data(i)
        generate_noun_phrases()
        collect_and_normalize(draw)
        # only for summary    
        # calculate_weights()
        extract_key_phrases()
        print("\n")
