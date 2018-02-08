# -*- coding:utf-8 -*-
import datetime
from multiprocessing import Process

from feature_extraction import ChiSquare
from tools import get_accuracy
from tools import Write2File

import numpy as np

from sklearn.svm import SVC
from sklearn.externals import joblib


class SVMClassifier:
    def __init__(self, train_data, train_labels, best_words, C, type):
        train_data = np.array(train_data)
        train_labels = np.array(train_labels)

        self.best_words = best_words
        self.type = type
        self.clf = joblib.load(self.type + '.pkl')
        # self.__train(train_data, train_labels)

    def words2vector(self, all_data):
        vectors = []
        for data in all_data:
            vector = []
            for feature in self.best_words:
                vector.append(data.count(feature))
            vectors.append(vector)

        vectors = np.array(vectors)
        return vectors

    def classify(self, data):
        vector = self.words2vector([data])

        prediction = self.clf.predict(vector)

        return prediction[0]



class Test:
    def __init__(self, type_, train_num, test_num, feature_num, max_iter, C, k, corpus):
        self.type = type_
        self.train_num = train_num
        self.test_num = test_num
        self.feature_num = feature_num
        self.max_iter = max_iter
        self.C = C
        self.k = k
        self.parameters = [train_num, test_num, feature_num]

        # get the f_corpus
        self.train_data, self.train_labels = corpus.get_train_corpus(train_num)
        self.test_data, self.test_labels = corpus.get_test_corpus(test_num)

        # feature extraction
        fe = ChiSquare(self.train_data, self.train_labels)
        self.best_words = fe.best_words(feature_num)

    def test_svm(self, test_data):
        # print("SVMClassifier")
        # clf = joblib.load('SVM_Dump.pkl')
        svm = SVMClassifier(self.train_data, self.train_labels, self.best_words, self.C, self.type)
        classify_labels = []

        # print(test_data)
        for data in test_data:
            if type(data) == type({"1":1}):
                a = svm.classify(data['text'].encode('utf-8'))
                print "DATA: {}".format(a)
                classify_labels.append(a)
            else:
                classify_labels.append(svm.classify(data))

        print(classify_labels)

        '''
        counter = 0
        for r in range(len(classify_labels)):
            counter += 1 if classify_labels[r]==self.test_labels[r] else 0
        print(float(counter / len(classify_labels)))
        '''
        return classify_labels


def comments_classify(data):
    from corpus import TencentCorpus

    type_ = "tencent"
    train_num = 0.75
    test_num = 0.25
    feature_num = 3000
    max_iter = 200
    C = 150
    k = 13
    k = [1, 3, 5, 7, 9, 11, 13]
    corpus = TencentCorpus()

    test = Test(type_, train_num, test_num, feature_num, max_iter, C, k, corpus)

    # print(test.test_svm(data))
    return test.test_svm(data)


def comments_classify_c(data):
    from corpus import TencentCompleteCorpus

    type_ = "complete_tencent"
    train_num = 0.75
    test_num = 0.25
    feature_num = 3000
    max_iter = 200
    C = 150
    k = 13
    k = [1, 3, 5, 7, 9, 11, 13]
    corpus = TencentCompleteCorpus()

    test = Test(type_, train_num, test_num, feature_num, max_iter, C, k, corpus)

    # print(test.test_svm(data))
    return test.test_svm(data)


if __name__ == '__main__':
    pass
    data = [u'知法犯法罪加一等，故意殴打他人应该按刑事案件处理'.encode('utf-8'),u'中国加油'.encode('utf-8')]
    comments_classify(data)
    #comments_classify_c(data)