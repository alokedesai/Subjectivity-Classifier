import math
import sys

class SvmInput:
  
  def __init__(self, in_file, feature_file, out_file, stop_file):
    self.in_file = open(in_file, "r").readlines()
    self.feature_file = open(feature_file, "w")
    self.out_file = open(out_file, "w")
    self.stop = self.read_stoplist(stop_file)

    self.idf = {}
    for text in self.in_file:
      line = text.split("\t")[1]

      words_seen = set()
      for word in line.split(" "):

        word = word.rstrip()
        if word not in words_seen:
          self.idf[word] = self.idf.get(word, 0) + 1
          words_seen.add(word)

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


  # really inefficient way to implement this, but we'll fix it in the future
  # when we have some time
  def get_tfidf(self, text):
    tf = self.get_word_counts(text)
    
    for word in tf.keys():
      tf[word] = tf[word] * self.idf[word]

    return tf

  def create_bow_file(self, feature_type, min_frequency):
    features = {}
    feature_count = 1

    for line in self.in_file:
      line = line.rstrip()
      label, text = line.split("\t")

      counts = feature_type(text)
      self.out_file.write(label)

      printme = {}
      for tok in counts.keys():
        if (tok not in self.stop):
          if (tok not in features):
            features[tok] = feature_count
            self.feature_file.write(str(feature_count) + "\t" + tok + "\n")

            feature_count+=1

          printme[features[tok]] = counts[tok]

      for fnum in sorted(printme):
        if printme[fnum] >= min_frequency:
          self.out_file.write(" " + str(fnum) + ":" + str(printme[fnum]))
      self.out_file.write("\n")


  def create_word_count_file(self, min_frequency):
    self.create_bow_file(self.get_word_counts, min_frequency)

  def create_tf_file(self, min_frequency):
    self.create_bow_file(self.get_tf, min_frequency)

  def create_tfidf_file(self, min_frequency):
    self.create_bow_file(self.get_word_counts, min_frequency)



# data_file = sys.argv[1]
# stoplist = sys.argv[2]
# out = sys.argv[3]

svm_factory = SvmInput("data/data.txt", "test_feature.txt", "model.svm", "stop.txt")
# svm_factory.create_tf_file()
svm_factory.create_word_count_file(1)
