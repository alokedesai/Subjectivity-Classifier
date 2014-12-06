import sys

in_file = open(sys.argv[1], "r").readlines()

test = len(in_file)/10
train = 9*test

test_lines = in_file[:test]
train_lines = in_file[-train:]

test_file = open("test.svm", "w")
train_file = open("train.svm", "w")

test_file.writelines(test_lines)
train_file.writelines(train_lines)