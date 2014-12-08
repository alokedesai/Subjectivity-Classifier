import math
import sys
import subprocess

class SvmClassifier:
  
  def __init__(self, in_file, feature_file, out_file, stop_file):
    self.in_file = open(in_file, "r").readlines()
    self.feature_file = open(feature_file, "w")
    self.out_file = None
    self.out_file_name =  out_file
    self.stop = self.read_stoplist(stop_file)

    self.features = {}
    
    # info for Mutual Information
    self.num_objective = 0
    self.num_subjective = 0
    self.word_frequency = {}

    self.selected_features = []

    # calculate document frequency
    self.idf = {}
    for text in self.in_file:
      label, line = text.split("\t")

      if label == "1":
        self.num_objective += 1
      else:
        self.num_subjective += 1

      if label not in self.word_frequency:
        self.word_frequency[label] = {}

      words_seen = set()
      for word in line.split(" "):
        word = word.rstrip()

        if word not in words_seen and word not in self.stop:
          previous_count = self.word_frequency[label].get(word, 0)
          self.word_frequency[label][word] = previous_count + 1

          self.idf[word] = self.idf.get(word, 0) + 1
          words_seen.add(word)

    # update idf dictionary to be idf
    for word in self.idf.keys():
      self.idf[word] = math.log10(len(self.in_file) / self.idf[word])

  def read_stoplist(self, stop_file):
    stoplist = open(stop_file, "r").readlines()
    stop = set()

    for line in stoplist:
      line = line.rstrip()
      stop.add(line)

    return stop
	
  def get_word_counts(self, text):
  	count = {}
  	for word in text.split(" "):
  		old_count = count.get(word, 0)
  		count[word] = old_count + 1
  	return count

  def get_tf(self, text):
    count = {}
    words = text.split(" ")
    for word in words:
      word = word.rstrip()
      old_count = count.get(word, 0)
      count[word] = old_count + 1

    # normalize by length of text
    for word in count:
      count[word] = count[word] / float(len(words))

    return count


  def get_tfidf(self, text):
    tf = self.get_word_counts(text)
    
    for word in tf.keys():
      tf[word] = tf[word] * self.idf[word]

    return tf

  # populates feature dictionary
  def populate_features(self, feature_type):
    self.features = {}
    feature_count = 1
    for line in self.in_file:
      line = line.rstrip()
      label, text = line.split("\t")

      counts = feature_type(text)
      for word in counts.keys():
        if word not in self.stop:
          if word not in self.features:
            self.features[word] = feature_count
            self.feature_file.write(str(feature_count) + "\t" + word + "\n")
            feature_count += 1
  
  # creates svm files
  def print_svm(self, feature_type):
    self.out_file = open(self.out_file_name, "w")
    for line in self.in_file:
      line = line.rstrip()
      label, text = line.split("\t")

      counts = feature_type(text)
      self.out_file.write(label)

      printme = {}
      for word in counts.keys():
        if word not in self.stop:
          printme[self.features[word]] = counts[word]
            
      for fnum in sorted(printme):
        if not self.selected_features or fnum in self.selected_features:
          self.out_file.write(" " + str(fnum) + ":" + str(printme[fnum]))
      self.out_file.write("\n")
    self.out_file.close()

  def unigram_counts(self):
    self.populate_features(self.get_word_counts)

  def term_frequency(self):
    self.populate_features(self.get_tf)

  def tfidf(self):
    self.populate_features(self.get_word_counts)

  # returns the top n features using feature_selection
  def feature_selection(self, num_features = None):
    num_documents = float(self.num_objective + self.num_subjective)

    mutual_information = {}
    
    # compute mutual information
    for word in self.features:
      objective_count = self.word_frequency["1"].get(word, 0)
      objective_count = objective_count if objective_count != 0 else 1

      subjective_count = self.word_frequency["-1"].get(word, 0)
      subjective_count = subjective_count if subjective_count != 0 else 1

      docs_with_word = subjective_count + objective_count
      docs_without_word = num_documents - docs_with_word

      first = (objective_count / num_documents) * math.log(((num_documents * objective_count)/ float(docs_with_word*self.num_objective)),2)
      second = ((self.num_objective - objective_count) / num_documents) * math.log(((num_documents * (self.num_objective - objective_count)) / float(docs_without_word*self.num_objective)), 2)

      third = (subjective_count / num_documents) * math.log(((num_documents * subjective_count) / float(docs_with_word * self.num_subjective)), 2)
      fourth = ((self.num_subjective - subjective_count) / num_documents) * math.log(((num_documents * (self.num_subjective - subjective_count)) / float(docs_without_word * self.num_subjective)), 2)

      mutual_information[word] = first + second + third + fourth

    # convert mutual info to tuple list and sort
    mutual_info_tuple = [(k,v) for k,v in mutual_information.iteritems()]
    mutual_info_tuple = sorted(mutual_info_tuple, key= lambda x: x[1], reverse=True)
    
    if num_features:
      self.selected_features = [self.features[x[0]] for x in mutual_info_tuple[:num_features]]
    else:
      self.selected_features = [self.features[x[0]] for x in mutual_info_tuple]

svm_factory = SvmClassifier("data/data.txt", "test_feature.txt", "model.svm", "stop.txt")

# svm_factory.unigram_counts()
# svm_factory.feature_selection(200)
# svm_factory.print_svm(svm_factory.get_word_counts)

# run svm light and return a tuple of the accuracy and the f1
def run_svm_light(svm_file):
  divide(svm_file)
  subprocess.check_output(["../svm_learn", "train.svm", "test.model"])
  result = subprocess.check_output(["../svm_classify", "test.svm", "test.model"])
  return "\n".join(result.split("\n")[3:5])

def divide(svm_file):
  in_file = open(svm_file, "r").readlines()

  test = len(in_file)/10
  train = 9*test

  test_lines = in_file[:test]  
  train_lines = in_file[-train:]

  test_file = open("test.svm", "w")
  train_file = open("train.svm", "w")

  test_file.writelines(test_lines)
  train_file.writelines(train_lines)

for i in xrange(10, 28000, 100):
  svm_factory.unigram_counts()
  svm_factory.feature_selection(i)
  svm_factory.print_svm(svm_factory.get_word_counts)
  
  result = run_svm_light("model.svm")
  print str(i) + "\t" + result.split("\n")[0][22:28] + "\t" + result.split("\n")[1][30:37] + "\t" + result.split("\n")[1][38:44]
 