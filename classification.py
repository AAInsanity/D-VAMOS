# Thomas Deng
# CS251 Spring 18
# classification.py

import sys
import data
import classifiers
import csv
from timeit import default_timer as timer


#params:
#train: the filename of the training data set
#test: the filename of the test data set
#outputfile: the filename of the output of the file
#traincat: the filename of training categories (optional)
#testcat: the filename of test categories (optional)
#mode: 0 is Naive Bayes, 1 is KNN
def classify(train, test, outputfile, traincat = None, testcat = None, mode=0, K=None):
    dtrain = data.Data(train)
    dtest = data.Data(test)
    if traincat != None:
        traincatdata = data.Data(traincat)
        traincats = traincatdata.select_data( [traincatdata.get_headers()[0]] )
        A = dtrain.select_data( dtrain.get_headers() )
    else: #if traincat is not provided as an external file
        traincats = dtrain.select_data( [dtrain.get_headers()[-1]] )
        A = dtrain.select_data( dtrain.get_headers()[:-1] )
    if testcat != None:
        testcatdata = data.Data(testcat)
        testcats = testcatdata.select_data( [testcatdata.get_headers()[0]] )
        B = dtest.select_data( dtest.get_headers() )
    else: #if testcat is not provided as an external file
        testcats = dtest.select_data( [dtest.get_headers()[-1]] )
        B = dtest.select_data( dtest.get_headers()[:-1] )
    
    if mode == 0:
        cf = classifiers.NaiveBayes()
        print ("traincats: ", traincats)
        cf.build(A, traincats)
    else:
        cf = classifiers.KNN()
        cf.build(A, traincats, K)
    
    #classify the training data set
    ctraincats, ctrainlabels = cf.classify( A )
    cmat_train = cf.confusion_matrix(traincats, ctraincats)     
    print ("For training data set:")    
    print (cf.confusion_matrix_str(cmat_train))
    #classify the test data set
    ctestcats, ctestlabels = cf.classify( B )   
    cmat_test = cf.confusion_matrix(testcats, ctestcats)     
    print ("For test data set:")    
    print (cf.confusion_matrix_str(cmat_test))
    
    num_points = B.shape[0]
    num_features = B.shape[1]
    
    content = []
    headers = dtest.get_headers()
    types = dtest.get_types()
    temp1 = []
    temp2 = []
    for i in range(num_features):
        temp1.append(headers[i])
        temp2.append(types[i])
    temp1.append("Result Category")
    temp2.append("numeric")
    content.append(temp1)
    content.append(temp2)
        
    for i in range(num_points):
        temp = []
        for j in range(num_features):
            temp.append(B[i,j])
        temp.append(ctestcats[i].item(0))
        content.append(temp)
        
    fp = open(outputfile, 'w+')
    csv_writer = csv.writer(fp, lineterminator='\n') 
    csv_writer.writerows(content)
    fp.close()


#classify data sets
#is modeled after classify(), does (basically) the same thing but with different params
#here, train, test, traincat, testcat are all matrices  
def classify2(train, test, traincat = None, testcat = None, mode = 0, K = None):
    #if traincat is separately provided
    if traincat is not None:
        traincats = traincat
        A = train
    #otherwise, assume the cats is the last column of train
    else:
        traincats = train[:, -1]
        A = train[:, :-1]
    
    #if testcat is separately provided
    if testcat is not None:
        testcats = testcat
        B = test
    #otherwise, assume the cats is the last column of test
    else:
        testcats = test[:, -1]
        B = test[:, :-1]    
    if mode == 0:
        cf = classifiers.NaiveBayes()
        cf.build(A, traincats)
    else:
        cf = classifiers.KNN()
        cf.build(A, traincats, K)
    
    #classify the training data set
    ctraincats, ctrainlabels = cf.classify( A )
    cmat_train = cf.confusion_matrix(traincats, ctraincats)     
    print ("For training data set:")    
    print (cf.confusion_matrix_str(cmat_train))
    #classify the test data set
    ctestcats, ctestlabels = cf.classify( B )
    cmat_test = cf.confusion_matrix(testcats, ctestcats)     
    print ("For test data set:")    
    print (cf.confusion_matrix_str(cmat_test))
    # print ("ctestcats tolist: ", ctestcats.T.tolist()[0])
    return ctestcats.T.tolist()[0]
    
    
    
#test
if __name__ == "__main__":
	t1 = timer()
	classify("UCI-X-train.csv","UCI-X-test.csv", "result.csv", "UCI-Y-train.csv", "UCI-Y-test.csv", mode = 1, K = 10)
	# classify("iris_proj8_train.csv","iris_proj8_test.csv", "result.csv", mode = 0)
	t2 = timer()
	print ("time taken to classify: ", t2-t1)    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
            