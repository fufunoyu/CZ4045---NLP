import pytextrank.pytextrank as ptr
from dbmgr.models import AmazonReview
import json

stage0 = "assignment_solution/stages/stage0.json"
stage1 = "assignment_solution/stages/stage1.json"
stage2 = "assignment_solution/stages/stage2.json"
stage_phrases = "assignment_solution/stages/key_phrases.txt"

def write_to_json(start, end):
    #Concat and write all reviews to file
    data = AmazonReview.objects.all()[start:end]
    open(stage0, 'w').close()
    with open(stage0, "a") as outfile:
        outfile.write("{\"id\": \"001\", \"text\": \"")
        for d in data:
            stripped = d.reviewText.replace("\"", "")
            outfile.write(stripped + " ") #do we need fullstop?
        outfile.write("\"}")

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

def extract_key_phrases():
    phrases = ", ".join(set([p for p in ptr.limit_keyphrases(stage2, phrase_limit=12)]))
    with open(stage_phrases, "w") as outfile:
        outfile.write(phrases)
    print("Key phrases:")
    print(phrases)

def test(start, end, draw=False):
    write_to_json(start, end)
    generate_noun_phrases()
    collect_and_normalize(draw)
    extract_key_phrases()