import csv
import sys

skip_tags = [""]

#file_path = "./Test_DB.csv"

output_file = "./mind_map.dot"

dot_graph_start = """digraph {
    // Graph setup
    label = "Literature Review"
    labelloc = "top"
    fontsize = 30
    // Possible layouts:
    // circo, dot, dfp, neato, nop, nop1, nop2
    // osage, patchwork, sfdp, twopi
    layout = "circo"

    // Data
"""

dot_graph_end = "}"

# Functions
def write_graph(file_path, data):
    with open(file_path, "w") as f:
        f.write(data)

def gather_topics(data):
    topics = []

    for item in data:
        for tag in item["tags"]:
            if tag not in topics:
                topics += [tag]
    return topics


class Subgraph:
    def __init__(self, topic_name):
        self.topic_name = topic_name
        self.keys = []

    def add_key(self, key):
        self.keys += [key]

    def draw(self):
        graph = '\tsubgraph { topic_' + self.topic_name + f' [label="{self.topic_name}", shape="rectangle", fontsize=30]\n'

        for key in self.keys:
            graph += f"\t\tnode_{key} -> topic_{self.topic_name}\n"

        graph += "\t}"
        return graph

def generate_node(item):
    return "node_" + item["key"] + ' [label="{0}, {1},\\n{2}"]'.format(
        item["author"], item["year"], item["title_start"])

def generate_data_nodes(data):
    res = ""
    for item in data:
        res += f"\t{generate_node(item)}\n"
    return res + "\n"



# Main
if __name__ == "__main__":
    
    num_args = len(sys.argv)
    if num_args < 2 or num_args > 2:
        print('Usage: python generate_mind_map.py path_to_zotero_db.csv')
        exit()

    file_path = sys.argv[1]
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        raw_data = []
        for item in reader:
            raw_data += [item]

    # Create dict with key, author names, year, and manual tags
    data = [] 
    for item in raw_data:
        key = item['\ufeff"Key"'] # Some encoding issue? Fix this? pandas should decode the csv better...
        author = item["Author"].split(',')[0]
        year = item["Date"].split('-')[0]
        title_start = " ".join(item["Title"].split(' ')[:3]) 
        tags = [x.strip() for x in item["Manual Tags"].split(';') if x.strip() != "" and x.strip() not in skip_tags]
        if len(tags) > 0 and author != "":
            data += [{"key": key, "author": author, "year": year, 
                    "title_start": title_start, "tags": tags}]

    # Generate mind map
    topics = gather_topics(data)
    topics_subgraphs = {topic: Subgraph(topic) for topic in topics}

    # Assign items to topic subgraphs
    for item in data:
        for tag in item["tags"]:
            topics_subgraphs[tag].add_key(item["key"])

    
    graph = dot_graph_start

    graph += generate_data_nodes(data)

    for subgraph in topics_subgraphs.values():
        graph += subgraph.draw() + "\n"

    graph += dot_graph_end

    write_graph(output_file, graph)



    