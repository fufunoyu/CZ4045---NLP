import pytextrank.pytextrank as ptr
from dbmgr.models import AmazonReview
import json
from time import time

stage0 = "assignment_solution/stages/stage0.json"
stage1 = "assignment_solution/stages/stage1.json"
stage2 = "assignment_solution/stages/stage2.json"
stage_phrases = "assignment_solution/stages/key_phrases.txt"



# Top 3 more popular products: 
p1 = 'B005SUHPO6'
p2 = 'B0042FV2SI'    
p3 ='B008OHNZI0'

pop_products = [p1,p2,p3]

def write_to_json():
    #Concat and write all reviews to file
    data = AmazonReview.objects.all()[88000:90001]
    open(stage0, 'w').close()
    with open(stage0, "a") as outfile:
        for i, d in enumerate(data):
            cleaned_text = d.reviewText.replace("\"", "")
            cleaned_text = cleaned_text.replace("\'", "")
            cleaned_text = cleaned_text.replace("\\", "")
            new_review = {
                "id": i,
                "text": cleaned_text
            }
            json.dump(new_review, outfile)
            outfile.write("\n")
            if i%1000 == 0:
                print("\rfinished %d iterations" %i, end="")
        print("\n")

        # outfile.write("{\"id\": \"000\", \"text\": \"")
        # i = 0
        # for d in data:
        #     s1 = d.reviewText.replace("\"", "")
        #     s2 = s1.replace("\\", "")
        #     s3 = s2.replace("'", "")
        #     outfile.write(s3 + " ") #do we need fullstop?
        # outfile.write("\"}")

def generate_noun_phrases():
    open(stage1, "w").close()
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

    open(stage2, "w").close()
    with open(stage2, 'w') as f:
        for rl in ptr.normalize_key_phrases(stage1, ranks):
            f.write("%s\n" % ptr.pretty_print(rl._asdict()))
            # print(ptr.pretty_print(rl))

def extract_key_phrases():
    phrases = ", ".join(set([p for p in ptr.limit_keyphrases(stage2, phrase_limit=20)]))
    with open(stage_phrases, "w") as outfile:
        outfile.write(phrases)

def all_reviews(draw=False):
    start_time = time()
    write_to_json()
    end_time = time()
    print("Took %d seconds to write from db" %(int(end_time-start_time)))
    start_time = time()
    generate_noun_phrases()
    end_time = time()
    print("Took %d seconds to generate noun phrases" %(int(end_time-start_time)))
    start_time = time()
    collect_and_normalize(draw)
    end_time = time()
    print("Took %d seconds to collect and normalize noun phrases" %(int(end_time-start_time)))
    start_time = time()
    extract_key_phrases()
    end_time = time()
    print("Took %d seconds to extract key noun phrases" %(int(end_time-start_time)))