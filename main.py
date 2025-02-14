from lxml import etree
import os
import json


def build_word_info(xml_file):
    """
    Parses a single XML file and returns a dictionary mapping each word to a dictionary with:
      - "synonyms": a set of words from the same synset (other than itself)
      - "antonyms": a set of antonyms (if present)
      - "definition": a set of definitions (from the gloss with desc="orig")
    """
    part_of_speech = xml_file.split("/")[-1].split(".")[0]

    try:
        tree = etree.parse(xml_file)
    except Exception as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return {}

    root = tree.getroot()
    word_info = {}

    for synset in root.findall("synset"):
        # Extract terms from the <terms> element.
        terms = synset.xpath("./terms/term/text()")
        terms = [term.strip() for term in terms if term.strip()]

        # Extract the definition from the gloss with desc="orig".
        definition_list = synset.xpath("./gloss[@desc='orig']/orig/text()")
        definition = definition_list[0].strip() if definition_list else ""

        # Attempt to extract antonyms (if present).
        antonyms = synset.xpath(".//ant/text()")
        antonyms = [ant.strip() for ant in antonyms if ant.strip()]

        # For every term in the synset, add other terms as synonyms.
        for word in terms:
            if word not in word_info:
                word_info[word] = {
                    part_of_speech: {
                        "synonyms": set(),
                        "antonyms": set(),
                        "definition": set(),
                    }
                }
            for other in terms:
                if other != word:
                    word_info[word][part_of_speech]["synonyms"].add(other)
            for ant in antonyms:
                word_info[word][part_of_speech]["antonyms"].add(ant)
            if definition:
                word_info[word][part_of_speech]["definition"].add(definition)

    return word_info


def combine_dicionaries(dict1, dict2):
    """ Combines two dictionaries, updating the first dictionary with the second. """
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(value, dict):
                combine_dicionaries(dict1[key], value)
            else:
                dict1[key].update(value)
        else:
            dict1[key] = value
    return dict1


def convert_sets_to_lists(word_info):
    """ Converts all sets in the word_info dictionary to lists. """
    for word, info in word_info.items():
        for part_of_speech, data in info.items():
            for key, value in data.items():
                word_info[word][part_of_speech][key] = list(value)
    return word_info


def print_word(word_info, word):
    """
    Prints the synonyms, antonyms, and definitions for a given word.
    """
    if word not in word_info:
        print(f"Word '{word}' not found in the thesaurus.")
        return

    for part_of_speech, info in word_info[word].items():
        print(f"{word} ({part_of_speech}):")
        print(f"\tSynonyms: {info["synonyms"]}")
        print(f"\tAntonyms:  {info["antonyms"]}")
        print(f"\tDefinitions:  {info["definition"]}")


def make_word_info_json(xml_files, output_file):
    """ Builds a JSON file with the word information from the XML files. """
    word_info = {}
    for xml_file in xml_files:
        current_info = build_word_info(xml_file)
        combine_dicionaries(word_info, current_info)
    word_info = convert_sets_to_lists(word_info)
    json.dump(word_info, open(output_file, "w"), indent=4)


def main():
    word_info_json = "word_info.json"
    if not os.path.exists(word_info_json):
        xml_files = [
            "resources/thesaurus/adj.xml",
            "resources/thesaurus/adv.xml",
            "resources/thesaurus/noun.xml",
            "resources/thesaurus/verb.xml",
        ]
        make_word_info_json(xml_files, word_info_json)
    word_info = json.load(open(word_info_json))
    
    print_word(word_info, "happy")


if __name__ == "__main__":
    main()  
