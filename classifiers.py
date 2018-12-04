# Thomas Deng
# CS 251 Project 8
#
# Modelled after classifiers_template by prof. Maxwell

import sys
import data
import analysis as an
import numpy as np
import math
import scipy.spatial.distance as dt

class Classifier:

    def __init__(self, type):
        '''The parent Classifier class stores only a single field: the type of
        the classifier.  A string makes the most sense.

        '''
        self._type = type

    def type(self, newtype = None):
        '''Set or get the type with this function'''
        if newtype != None:
            self._type = newtype
        return self._type

    def confusion_matrix( self, truecats, classcats ):
        '''Takes in two Nx1 matrices of zero-index numeric categories and
        computes the confusion matrix. The rows represent true
        categories, and the columns represent the classifier output.

        '''
        num_points = np.shape(truecats)[0]
        unique_true, mapping_true = np.unique( np.array(truecats.T), return_inverse = True)
        unique_class, mapping_class = np.unique( np.array(classcats.T), return_inverse = True)
        num_categories = max(len(unique_true),len(unique_class))
        c_mat = np.zeros((num_categories, num_categories))
        # print ("unique true: ", unique_true)
        for i in range(num_points):
            true = mapping_true.item(i)
            classified = mapping_class.item(i)
            c_mat[true,classified] += 1
        
        return c_mat

    def confusion_matrix_str( self, cmtx ):
        '''Takes in a confusion matrix and returns a string suitable for printing.'''
        s = "      Confusion Matrix\n"
        s += '         Predicted\n'
        num_categories = cmtx.shape[0]
        mid = int(num_categories/2)
        for i in range(num_categories):
            if i != mid:
            	s += "      "
            else:
            	s += "Actual"
            for j in range(num_categories):
                s += " " + str(cmtx[i,j]) + " "
            s += "\n"

        return s

    def __str__(self):
        '''Converts a classifier object to a string.  Prints out the type.'''
        return str(self._type)



class NaiveBayes(Classifier):
    '''NaiveBayes implements a simple NaiveBayes classifier using a
    Gaussian distribution as the pdf.

    '''

    def __init__(self, data=None, headers=[], categories=None):
        '''Takes in a Matrix of data with N points, a set of F headers, and a
        matrix of categories, one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'Naive Bayes Classifier')
        
        # store the headers used for classification
        self.headers = headers
        # number of classes and number of features
        self.num_categories = 0
        self.num_features = len(headers)
        # original class labels
        self.class_labels = None
        # unique data for the Naive Bayes: means, variances, scales, priors
        self.means = None
        self.variances = None
        self.scales = None
        self.priors = None
        
        # if given data,
        if data != None:
            # call the build function'
            self.build(data.select_data(headers), categories)

    def build( self, A, categories ):
        '''Builds the classifier give the data points in A and the categories'''
        
#         print ("categories: ", categories)
#         print ("categories.T: ", categories.T)
        # figure out how many categories there are and get the mapping (np.unique)
        self.class_labels, self.mapping, self.counts = np.unique( np.array(categories.T), return_inverse=True, return_counts=True)
        self.num_categories = np.shape(self.class_labels)[0]
        self.num_features = np.shape(A)[1] #number of features (dimensions)
        num_points = np.shape(A)[0] #number of points used to build
        
        
        # create the matrices for the means, vars, and scales
        # the output matrices will be categories x features
        self.means = np.empty([self.num_categories, self.num_features])
        self.vars = np.empty([self.num_categories, self.num_features])
        self.scales = np.empty([self.num_categories, self.num_features])
        self.priors = np.empty([self.num_categories, ])
        temp = dict(zip(self.class_labels, self.counts))
        # compute the means/vars/scales/priors for each class
        # the prior for class i will be the number of examples in class i divided by the total number of examples
#         print ("temp: ", temp)
#         print ("class labels: ", self.class_labels)
        
        for i in range(self.num_categories): #loop vertically
            self.priors[i] = temp[self.class_labels[i]]/len(categories)
            for j in range(self.num_features): #loop horizontally
                self.means[i,j] = np.mean(A[(self.mapping==i),j])
                self.vars[i,j] = np.var(A[(self.mapping==i),j], ddof = 1)
                # print ("A[(self.mapping==i),j] is: ", A[(self.mapping==i),j])
                self.scales[i,j] = 1/np.sqrt(2*math.pi*np.var(A[(self.mapping==i),j]))
        # store any other necessary information: # of classes, # of features, original labels
        return

    def classify( self, A, return_likelihoods=False ):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_likelihoods
        is True, it also returns the probability value for each class, which
        is product of the probability of the data given the class P(Data | Class)
        and the prior P(Class).

        '''

        # error check to see if A has the same number of columns as the class means
        if np.shape(A)[1] != self.num_features:
            print ("Dimensions don't match!")
            return 
                
        # make a matrix that is N x C to store the probability of each class for each data point
        P = np.zeros((np.shape(A)[0], self.num_categories)) # a matrix of zeros that is N (rows of A) x C (number of classes)

        # Calcuate P(D | C) by looping over the classes
        #  with numpy-fu you can do this in one line inside a for
        #  loop, calculating a column of P in each loop.
        #
        #  To compute the likelihood, use the formula for the Gaussian
        #  pdf for each feature, then multiply the likelihood for all
        #  the features together The result should be an N x 1 column
        #  matrix that gets assigned to a column of P
        for i in range(self.num_categories):
            P[:, i] = self.priors[i] * np.prod(np.multiply(self.scales[i,:],np.exp(-np.square(A-self.means[i,:])/(2*self.vars[i,:]))), axis=1).T
            
        # calculate the most likely class for each data point
        cats = np.matrix(np.argmax(P, axis = 1)).T # take the argmax of P along axis 1

        # use the class ID as a lookup to generate the original labels
        labels = self.class_labels[cats]

        if return_likelihoods:
            return cats, labels, P

        return cats, labels       

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nNaive Bayes Classifier\n"
        for i in range(self.num_categories):
            s += 'Class %d --------------------\n' % (i)
            s += 'Mean  : ' + str(self.means[i,:]) + "\n"
            s += 'Var   : ' + str(self.vars[i,:]) + "\n"
            s += 'Scales: ' + str(self.scales[i,:]) + "\n"
            s += 'Prior: ' + str(self.priors[i]) + "\n"

        s += "\n"
        return s
        
    def write(self, filename):
        '''Writes the Bayes classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the Bayes classifier from the file'''
        # extension
        return

    
class KNN(Classifier):

    def __init__(self, data=None, headers=[], categories=None, K=None):
        '''Take in a Matrix of data with N points, a set of F headers, and a
        matrix of categories, with one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'KNN Classifier')
        
        # store the headers used for classification
        self.headers = headers
        # number of classes and number of features
        self.num_categories = 0
        self.num_features = 0
        # original class labels
        self.class_labels = None
        # unique data for the KNN classifier: list of exemplars (matrices)
        self.exemplars = []
        # if given data,
        if data != None:
            # call the build function'
            self.build(data.select_data(headers), categories, K)
            
    def build( self, A, categories, K = None ):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        self.class_labels, self.mapping, self.counts = np.unique( np.array(categories.T), return_inverse=True, return_counts=True)
        self.num_categories = len(self.class_labels)
        self.num_features = A.shape[1]
        # for each category i, build the set of exemplars
        for i in range(self.num_categories):
            # if K is None
            if K == None:
                # append to exemplars a matrix with all of the rows of A where the category/mapping is i
                self.exemplars.append(A[(self.mapping==i),:])
            else:
                # run K-means on the rows of A where the category/mapping is i
                # append the codebook to the exemplars
                codebook = an.kmeans(A[(self.mapping==i),:], self.headers, K, whiten = False)[0]
                self.exemplars.append(codebook)

        # store any other necessary information: # of classes, # of features, original labels
        
        return

    def classify(self, A, return_distances=False, K=12):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_distances is
        True, it also returns the NxC distance matrix. The distance is 
        calculated using the nearest K neighbors.'''

        # error check to see if A has the same number of columns as the class means
        if np.shape(A)[1] != self.num_features:
            print ("Dimensions don't match!")
            return 

        # make a matrix that is N x C to store the distance to each class for each data point
        D = np.zeros((np.shape(A)[0], self.num_categories)) # a matrix of zeros that is N (rows of A) x C (number of classes)
        
        # for each class i
        for i in range(self.num_categories):
            # make a temporary matrix that is N x M where M is the number of examplars (rows in exemplars[i])
            temp = np.zeros((np.shape(A)[0], np.shape(self.exemplars[i])[0]))
            # calculate the distance from each point in A to each point in exemplar matrix i (for loop)
            for j in range(np.shape(A)[0]):
                for k in range(np.shape(self.exemplars[i])[0]):
                    temp[j,k] = dt.euclidean(A[j,:], self.exemplars[i][k,:])
            # sort the distances by row
            temp.sort(axis=1)
            # sum the first K columns
            D[:,i] = np.sum(temp[:,:K], axis = 1)

        # calculate the most likely class for each data point
        cats = np.matrix(np.argmin(D, axis=1)).T # take the argmax of D along axis 1

        # use the class ID as a lookup to generate the original labels
        labels = self.class_labels[cats]

        if return_distances:
            return cats, labels, D

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nKNN Classifier\n"
        for i in range(self.num_categories):
            s += 'Class %d --------------------\n' % (i)
            s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
            s += 'Mean of Exemplars  :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

        s += "\n"
        return s


    def write(self, filename):
        '''Writes the KNN classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the KNN classifier from the file'''
        # extension
        return
    

# test function
def main(argv):
    # test function here
    if len(argv) < 5:
        print( 'Usage: python3 %s <training data file> <training categories file> <test data file> <test categories file>' % (argv[0]) )
        exit(-1)

    train_file = argv[1]
    traincat_file = argv[2]
    test_file = argv[3]
    testcat_file = argv[4]

    dtrain = data.Data(train_file)

    traincats = data.Data(traincat_file)
    traincatdata = traincats.get_data(traincats.get_headers())

    dtest = data.Data(test_file)

    testcats = data.Data(testcat_file)
    testcatdata = testcats.get_data(testcats.get_headers())

    nbc = NaiveBayes(dtrain, dtrain.get_headers(), traincatdata )

    print( 'Naive Bayes Training Set Results' )
    A = dtrain.get_data(dtrain.get_headers())
    
    newcats, newlabels = nbc.classify( A )

    confmtx = nbc.confusion_matrix( traincatdata, newcats )
    print( nbc.confusion_matrix_str( confmtx ) )


    print( 'Naive Bayes Test Set Results' )
    A = dtest.get_data(dtest.get_headers())
    
    newcats, newlabels = nbc.classify( A )

    confmtx = nbc.confusion_matrix( testcatdata, newcats )
    print( nbc.confusion_matrix_str( confmtx ) )

    print( '-----------------' )
    print( 'Building KNN Classifier' )
    knnc = KNN( dtrain, dtrain.get_headers(), traincatdata, 10 )

    print( 'KNN Training Set Results' )
    A = dtrain.get_data(dtrain.get_headers())

    newcats, newlabels = knnc.classify( A )

    confmtx = knnc.confusion_matrix( traincatdata, newcats )
    print( knnc.confusion_matrix_str(confmtx) )

    print( 'KNN Test Set Results' )
    A = dtest.get_data(dtest.get_headers())

    newcats, newlabels = knnc.classify(A)

    # print the confusion matrix
    confmtx = knnc.confusion_matrix( testcatdata, newcats )
    print( knnc.confusion_matrix_str(confmtx) )

    return

if __name__ == "__main__":
    main(sys.argv)
