# Thomas Deng
# CS251 Spring 18
# analysis.py

import numpy as np
import scipy.cluster.vq as vq
import data
import statistics
import scipy.stats as stats
import random
import math
import scipy.spatial.distance as dt

#Takes in a list of column headers and the Data object and returns a list of 2-element
#lists with the minimum and maximum values for each column. The function is required to work only on numeric data typess
def data_range(data, headers):
    #create new list
    range = []
    for header in headers:
        header = header.strip()
        index = data.header2col[header]
        if data.get_types()[index] != "numeric":
            continue #disregard non numerical headers
        col = data.get_col(index)
        max = np.amax(col)
        min = np.amin(col)
        range.append([min,max])
    return range
        
#Takes in a list of column headers and the Data object and returns a list of the mean 
#values for each column. Use the built-in numpy functions to execute this calculation       
def mean(data, headers):
    #create new list
    means = []
    for header in headers:
        header = header.strip()
        index = data.header2col[header]
        if data.get_types()[index] != "numeric":
            continue #disregard non numerical headers
        col = data.get_col(index)
        mean = np.mean(col)
        means.append(mean)
    return means

#Takes in a list of column headers and the Data object and returns a list of the standard 
#deviation for each specified column. Use the built-in numpy functions to execute this calculation
def stdev(data, headers):
    #create new list
    stds = []
    for header in headers:
        header = header.strip()
        index = data.header2col[header]
        if data.get_types()[index] != "numeric":
            continue #disregard non numerical headers
        col = data.get_col(index)
        std = np.std(col)
        stds.append(std)
    return stds
    
#Takes in a list of column headers and the Data object and returns a list of the variance 
#for each specified column. Use the built-in numpy functions to execute this calculation
def variance(data, headers):
    #create new list
    vars = []
    for header in headers:
        header = header.strip()
        index = data.header2col[header]
        if data.get_types()[index] != "numeric":
            continue #disregard non numerical headers
        col = data.get_col(index)
        var = np.var(col)
        vars.append(var)
    return vars
    
#Takes in a list of column headers and the Data object and returns a list of the medians 
#for each specified column. Use the built-in numpy functions to execute this calculation
def median(data, headers):
    #create new list
    meds = []
    for header in headers:
        header = header.strip()
        index = data.header2col[header]
        if data.get_types()[index] != "numeric":
            continue #disregard non numerical headers
        col = data.get_col(index)
        med = np.median(col, axis=0).item()
        meds.append(med)
    return meds         

#Takes in a list of column headers and the Data object and returns a list of the sums 
#for each specified column. Use the built-in numpy functions to execute this calculation
def sum(data, headers):
    #create new list
    sums = []
    for header in headers:
        header = header.strip()
        index = data.header2col[header]
        if data.get_types()[index] != "numeric":
            continue #disregard non numerical headers
        col = data.get_col(index)
        sum = np.sum(col)
        sums.append(sum)
    return sums     

#Takes in a list of column headers and the Data object and returns a matrix with each column
#normalized so its minimum value is mapped to zero and its maximum value is mapped to 1.
def normalize_columns_separately(data, headers):
    my_matrix = data.select_data(headers)
    for i in range(np.shape(my_matrix)[1]): #loop through the columns
        col = my_matrix[:,i]
        min = np.amin(col)
        col -= min #shift the min to 0
        max = np.amax(col)
        if max != 0:
            col *= 1/max #make the max to be 1
        else:
            pass #if max is 0 then don't change a thing
    return my_matrix

#Takes in a list of column headers and the Data object and returns a matrix with each entry
#normalized so that the minimum value (of all the data in this set of columns) 
#is mapped to zero and its maximum value is mapped to 1.
def normalize_columns_together(data, headers):
    my_matrix = data.select_data(headers)
    min = np.amin(my_matrix)
    my_matrix -= min #shift the min to 0
    max = np.amax(my_matrix)
    my_matrix *= 1/max
    return my_matrix
    
#performs single linear regression
#returns a tuple (slope, intercept, r_value, p_value, std_err, min_ind, max_ind, min_dep, max_dep)
def single_linear_regression(data_obj, ind_var, dep_var):
    arr = data_obj.select_data([ind_var,dep_var])
    slope, intercept, r_value, p_value, std_err = stats.linregress(arr)
    min_ind = np.amin(arr[:,0])
    max_ind = np.amax(arr[:,0])
    min_dep = np.amin(arr[:,1])
    max_dep = np.amax(arr[:,1])
    return (slope, intercept, r_value, p_value, std_err, min_ind, max_ind, min_dep, max_dep)


#performs linear regression
#returns (b, sse, r2, t, p)
#b is in the form (m0, m1, .. mk, b)
def linear_regression(d, ind, dep):
    # assign to y the column of data for the dependent variable
    y = d.select_data([dep])
    # print ("y is: ", y)
    
    # assign to A the columns of data for the independent variables
    A = d.select_data(ind)
    # print ("A is: ", A)
    
    #    It's best if both y and A are numpy matrices

    # add a column of 1's to A to represent the constant term in the 
    #    regression equation.  Remember, this is just y = mx + b (even 
    #    if m and x are vectors).
    A = np.insert(A, np.shape(A)[1], 1, axis=1)
    # print ("A is: ", A)

    # assign to AAinv the result of calling numpy.linalg.inv( np.dot(A.T, A))
    AAinv = np.linalg.inv( np.dot(A.T, A))
    #    The matrix A.T * A is the covariance matrix of the independent
    #    data, and we will use it for computing the standard error of the 
    #    linear regression fit below.

    # assign to x the result of calling numpy.linalg.lstsq( A, y )
    x = np.linalg.lstsq( A, y )
    #    This solves the equation y = Ab, where A is a matrix of the 
    #    independent data, b is the set of unknowns as a column vector, 
    #    and y is the dependent column of data.  The return value x 
    #    contains the solution for b.

    # assign to b the first element of x.
    b = x[0]
    #    This is the solution that provides the best fit regression
    
    # assign to N the number of data points (rows in y)
    N = np.shape(y)[0]
    # assign to C the number of coefficients (rows in b)
    C = np.shape(b)[0]
    # assign to df_e the value N-C, 
    df_e = N-C
    #    This is the number of degrees of freedom of the error
    # assign to df_r the value C-1
    df_r = C-1
    #    This is the number of degrees of freedom of the model fit
    #    It means if you have C-1 of the values of b you can find the last one.

    # assign to error, the error of the model prediction.  Do this by 
    #    taking the difference between the value to be predicted and
    #    the prediction. These are the vertical differences between the
    #    regression line and the data.
    error = y - np.dot(A, b)

    # assign to sse, the sum squared error, which is the sum of the
    #    squares of the errors computed in the prior step, divided by the
    #    number of degrees of freedom of the error.  The result is a 1x1 matrix.
    sse = np.dot(error.T, error) / df_e

    # assign to stderr, the standard error, which is the square root
    #    of the diagonals of the sum-squared error multiplied by the
    #    inverse covariance matrix of the data. This will be a Cx1 vector.
    stderr = np.sqrt( np.diagonal( sse[0, 0] * AAinv ) )

    # assign to t, the t-statistic for each independent variable by dividing 
    #    each coefficient of the fit by the standard error.
    t = b.T / stderr

    # assign to p, the probability of the coefficient indicating a
    #    random relationship (slope = 0). To do this we use the 
    #    cumulative distribution function of the student-t distribution.  
    #    Multiply by 2 to get the 2-sided tail.
    p = 2*(1 - stats.t.cdf(abs(t), df_e))

    # assign to r2, the r^2 coefficient indicating the quality of the fit.
    r2  = 1 - error.var() / y.var()
    
    ranges = []
    for i in range(len(ind)): #for each columns of independent variable
        min_ind = np.amin(A[:,i])
        max_ind = np.amax(A[:,i])
        ranges.append((min_ind,max_ind))
    min_dep = np.amin(y)
    max_dep = np.amax(y)
    ranges.append((min_dep,max_dep))

    # Return the values of the fit (b), the sum-squared error, the
    #     R^2 fit quality, the t-statistic, and the probability of a
    #     random relationship, as well as min and max for each variable (ind columns and the dep column).
    
    return (b, sse, r2, t, p, ranges)
    
    
#preforms principle component analysis
def pca(d, headers, normalize=True):
    # assign to A the desired data. Use either normalize_columns_separately 
    #   or select_data, depending on the value of the normalize argument.
    if normalize:
        A = normalize_columns_separately(d,headers)
    else:
        A = d.select_data(headers)

    # assign to m the mean values of the columns of A
    m = []
    for i in range(len(headers)):
        col = A[:,i]
        mean = np.mean(col)
        m.append(mean)
    m = np.matrix(m)
        
    # assign to D the difference matrix A - m
    D = A - m
    
    # assign to U, S, V the result of running np.svd on D, with full_matrices=False
    U, S, V = np.linalg.svd(D, full_matrices=False)

    # the eigenvalues of cov(A) are the squares of the singular values (S matrix)
    #   divided by the degrees of freedom (N-1). The values are sorted.
    N = np.shape(A)[0]
    evals = np.square(S)
    evals *= 1/(N-1)

    # project the data onto the eigenvectors. Treat V as a transformation 
    #   matrix and right-multiply it by D transpose. The eigenvectors of A 
    #   are the rows of V. The eigenvectors match the order of the eigenvalues.
    pdata = (V * D.T).T

    # create and return a PCA data object with the headers, projected data, 
    # eigenvectors, eigenvalues, and mean vector.
    pcad = data.PCAData( pdata, V, evals, m, headers)
    
    return pcad

#generate kmeans with Numpy's built-in k-means function
#Takes in a numpy matrix, a set of headers, and the number of clusters to create
#Computes and returns the codebook, codes, and representation error.
def kmeans_numpy( A, headers, K, whiten = True):    
    # assign to W the result of calling vq.whiten on A
    W = vq.whiten(A)
    # assign to codebook, bookerror the result of calling vq.kmeans with W and K
    codebook , bookerror = vq.kmeans(W,K)
    # assign to codes, error the result of calling vq.vq with W and the codebook
    codes, error = vq.vq(W, codebook)
    # return codebook, codes, and error 
    return (codebook, codes, error)
    
# Selects K random rows from the data matrix A and returns them as a matrix
def kmeans_init(A, K):
    # Hint: generate a list of indices then shuffle it and pick K
    # Hint: Probably want to check for error cases (e.g. # data points < K)
    size = np.shape(A)[0]#how many points there are
    dim = np.shape(A)[1]#how many dimensions there are
    if size < K: #if there are not enough data points
        return
    temp = list(range(size)) #a list of available indices
    random.shuffle(temp)
    new_matrix = np.empty((0,dim)) #create an empty matrix
    for i in range(K):
        ind = temp[i]
        row = A[ind,:]
        new_matrix = np.vstack((new_matrix, row))
    return new_matrix
        

# Given a data matrix A and a set of means in the codebook
# Returns a matrix of the id of the closest mean to each point
# Returns a matrix of the sum-squared distance between the closest mean and each point
def kmeans_classify(A, codebook, d_metric = 0):
    # Hint: you can compute the difference between all of the means and data point i using: codebook - A[i,:]
    # Hint: look at the numpy functions square and sqrt
    # Hint: look at the numpy functions argmin and min        
    # print ("Distance Metric used: ", d_metric)
    size = np.shape(A)[0]#how many points there are
    min_ids = []
    min_ds = []
    k = codebook.shape[0] #how many means
    for i in range(size):#for each point
        temp = [] #temp is the list of distances to each mean
        for j in range(k): #loop through each mean
        	if d_metric == 0:
        		distance = dt.euclidean(A[i,:], codebook[j,:])
        	elif d_metric == 1:
        		distance = dt.cityblock(A[i,:], codebook[j,:])
        	elif d_metric == 2:
        		distance = dt.correlation(A[i,:], codebook[j,:])
        	elif d_metric == 3:
        		distance = dt.hamming(A[i,:], codebook[j,:])	
        	elif d_metric == 4:
        		distance = dt.cosine(A[i,:], codebook[j,:])
        	temp.append(distance)
#         diff = codebook - A[i,:]
#         diff2 = np.square(diff)#distances squared
#         for j in range(k): #loop through each mean
#             sum = np.sum(diff2[j,:])
#             d = np.sqrt(sum) #calculate the sum_squared distance
#             temp.append(d)
        temp = np.array(temp)
        min_d = np.min(temp)
        min_id = np.argmin(temp)
        min_ids.append(min_id)
        min_ds.append(min_d)
    min_ids = np.matrix(min_ids)
    min_ds = np.matrix(min_ds)
    return (min_ids, min_ds)
    
# Given a data matrix A and a set of K initial means, compute the optimal
# cluster means for the data and an ID and an error for each data point
def kmeans_algorithm(A, means, d_metric = 0):
    # set up some useful constants
    MIN_CHANGE = 1e-7     # might want to make this an optional argument
    MAX_ITERATIONS = 100  # might want to make this an optional argument
    D = means.shape[1]    # number of dimensions
    K = means.shape[0]    # number of clusters
    N = A.shape[0]        # number of data points

    # iterate no more than MAX_ITERATIONS
    for i in range(MAX_ITERATIONS):
        # calculate the codes by calling kmeans_classify
        # codes[j,0] is the id of the closest mean to point j
        codes, errors = kmeans_classify(A, means, d_metric)
        # initialize newmeans to a zero matrix identical in size to means
        # Hint: look up the numpy function zeros_like
        newmeans = np.zeros_like(means)
        # Meaning: the new means given the cluster ids for each point

        # initialize a K x 1 matrix counts to zeros
        # Hint: use the numpy zeros function
        counts = np.zeros((K,1))
        # Meaning: counts will store how many points get assigned to each mean

        # for the number of data points
        for j in range(N):
            # add to the closest mean (row codes[j,0] of newmeans) the jth row of A
            idx = codes[0,j]
            newmeans[idx, :] += A[j,:]
            # add one to the corresponding count for the closest mean
            counts[idx,0]+=1

        # finish calculating the means, taking into account possible zero counts
        #for the number of clusters K
        for j in range(K):
            # if counts is not zero, divide the mean by its count
            count = counts[j,0]
            if count != 0:
                newmeans[j,:] *= 1/count
            # else pick a random data point to be the new cluster mean
            else:
                temp = list(range(N)) #a list of available indices
                random.shuffle(temp)
                sub = A[temp[0]]
                newmeans[j,:] = sub

        # test if the change is small enough and exit if it is
        diff = np.sum(np.square(means - newmeans))
        means = newmeans
        if diff < MIN_CHANGE:
            break

    # call kmeans_classify one more time with the final means
    codes, errors = kmeans_classify( A, means, d_metric )

    # return the means, codes, and errors
    return (means, codes, errors)
    
#Takes in a numpy data, a set of headers, and the number of clusters to create
#Computes and returns the codebook, codes and representation errors. 
def kmeans(A, headers, K, whiten=True, d_metric = 0 ):
    # if whiten is True
    if whiten:
        # assign to W the result of calling vq.whiten on the data
        W = vq.whiten(A)
    # else
    else:
        # assign to W the matrix A
        W = A

    # assign to codebook the result of calling kmeans_init with W and K
    codebook = kmeans_init(W, K)
    # assign to codebook, codes, errors, the result of calling kmeans_algorithm with W and codebook        
    codebook, codes, errors = kmeans_algorithm(W, codebook, d_metric)
    # return the codebook, codes, and representation error    
    return (codebook, codes, errors)    
        





