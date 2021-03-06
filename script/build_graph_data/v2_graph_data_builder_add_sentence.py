import sys
from pathlib import Path
from nltk.tokenize import sent_tokenize
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection
import re
from definitions import OUTPUT_DIR
from script.fast_text.fasttext_classifier import FastTextClassifier
from sekg.graph.exporter.graph_data import GraphData
from util.import_extract_result_2_graph_data import ExtractResultImport
from util.path_util import PathUtil

classifier = FastTextClassifier()


def build_v2_graph_for_pro(pro_name):

    graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1")
    graph_data: GraphData = GraphData.load(graph_data_path)
    new_graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v2")
    res = ExtractResultImport(graph_data, new_graph_data_path, 2)

    data_dir = Path(OUTPUT_DIR) / "graph" / "jdk8" / "filter_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    filter_sentence_path = str(data_dir / "filter_sentence.txt")

    pat = re.compile('<[^>]+>', re.S)

    print("start to add sentences...")
    for id in graph_data.get_node_ids():
        node_info = graph_data.get_node_info_dict(id)
        short_description = node_info["properties"].get("short_description", "")
        if not short_description:
            continue

        short_description = pat.sub('', short_description)
        short_descs = sent_tokenize(short_description)

        for short_desc in short_descs:
            short_desc = " ".join(short_desc.split())
            str_rm_sign = classifier.preprocessor.remove_sign(short_desc)
            text = classifier.preprocessor.remove_stop_words(str_rm_sign)
            label = list(classifier.predict(text))[0]
            if label == "0":
                print(short_desc)
                with open(filter_sentence_path, "a", encoding='utf-8') as f:
                    f.write(short_desc)
                    f.write("\n")
                continue
            else:
                res.add_sentence_relation(short_desc, id, int(label))
    res.save_new_graph_data()


if __name__ == '__main__':
    pro_list = ["jdk8"]
    build_v2_graph_for_pro(pro_list[0])
