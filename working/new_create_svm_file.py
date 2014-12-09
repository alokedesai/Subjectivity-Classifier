import math
import sys
import subprocess

class FeatureMaker:
    def __init__(self, documents):
        # document_list is a list of tuples [(lable, [word, word])]
        self.document_list = documents

        self.feature_count = 0
        self.features = {}
        self.feature_mapping = {}
        self.selected_features = []  #?

        self.label_mapping = {}

    def idf(self):
        """Calculate idf for corpus."""
        for document in self.document_list:
            label, text = document
            words_in_text = set()  # used for keeping track of words already seen in the document
            for word in text:
                if word not in words_in_text:
                    self.idf[word] = self.idf.get(word,0) +1
                    words_in_text.add(word)

        # update idf dictionary to be idf
        for word in self.idf.keys():
            self.idf[word] = math.log10(len(self.document_list) / self.idf[word])

    def get_tf_idf(self,text):
        counts = self.get_word_counts(text)
        for word in counts:
            counts[word] *= self.idf[word]
        return counts

    def add_feature(self, feature_function):
        """
        adds new feature
        """
        document_id = 0
        for document in self.document_list:
            label, text = document
            self.label_mapping[document_id] = label
            feature_vector = feature_function(text)

            for key in feature_vector.keys():
                # get feature number
                if key not in self.feature_mapping:
                    self.feature_mapping[key] = self.feature_count
                    feature_number = self.feature_count
                    self.feature_count += 1
                else:
                    feature_number = self.feature_mapping[key]

                # add feature to dictionary
                document_features = self.features.get(document_id, {})
                document_features[feature_number] = feature_vector[key]
                self.features[document_id] = document_features
            document_id += 1

    def print_feature_mapping(self, feature_file_path):
        feature_file = open(feature_file_path, "w")
        for feature, feature_number in self.feature_mapping.items():
            out_string = "%d\t%s\n" % (feature_number, str(feature))
            feature_file.write(out_string)
        feature_file.close()

    def print_svm_file(self, svm_file_path):
        svm_file = open(svm_file_path, "w")
        for document_id in self.features.keys():
            label = self.label_mapping[document_id]
            output_string = str(label)
            for feature_number, feature_weight in self.features[document_id].items():
                output_string += " %d:%d" % (feature_number, feature_weight)
            svm_file.write(output_string)
            svm_file.write("\n")
        svm_file.close()


def get_word_counts(text):
    """get word counts in a single document"""
    counts = {}
    for word in text:
        counts[word] = counts.get(word,0) + 1
    return counts


def get_tf(text):
    """normalize counts by length of text"""
    counts = get_word_counts(text)
    for word in counts:
        counts[word] /= float(len(text))
    return counts


def main():
    #do all file I/O
    #read stoplist
    stop_list = open("stop.txt").readlines()
    stop_list = [e.strip() for e in stop_list]

    data = []
    data_file = open("data/data.txt", "r")
    for line in data_file:
        label, text = line.split("\t")
        split_text = text.strip().split(" ")
        split_text = [word for word in split_text if word not in stop_list]
        data.append((label, split_text))

    classifier = SvmClassifier(data)
    classifier.add_feature(get_word_counts)
    classifier.print_feature_mapping("feature_mapping.txt")
    classifier.print_svm_file("all_data.svm")


if __name__ == "__main__": main()