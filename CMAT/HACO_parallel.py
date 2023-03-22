# this program will run the optimization algorithm prallely in all the available CPU cores to minimize computation time.
import numpy as np
import matplotlib.pyplot as plt
import time

from joblib import Parallel, delayed
import multiprocessing as mp

num_cores = mp.cpu_count()
print(f'Number of cores in the system: {num_cores}')


def step_size(max_step, min_step, max_iteration, current_iteration):
    y = (min_step - max_step)/max_iteration * current_iteration + max_step
    return y

# locate the best solution and fitness value: x_best, y_best
def find_best(X, Y):
    idx_best = np.argmin(Y)
    x_best = X[idx_best]
    y_best = Y[idx_best]
    return x_best, y_best

# define the main function
def HACO(objective_function, lb, ub, available_operators, population=30, max_iteration=500, max_run_time=100, probability_random_chicks=0.0, max_step=0.99, min_step=0.01):
    start_time = time.process_time()    #track execution time

    history_best_obj_values = []  #keep history of the best fitness value for each iteration

    # step 1: initial solution
    no_variables = len(lb)
    # convert to numpy array
    lb, ub = np.array(lb), np.array(ub)

    X = np.zeros([population, no_variables])
    Y = np.zeros(population) # store fitness value

    for i in range(population):
        while True:
            X[i,:] = lb + np.random.uniform(0, 1, no_variables)*(ub - lb)
            X[i,:] = np.round(X[i,:], 0)
            if sum(X[i,:]) <= available_operators:
                break

    # parallel processing
    mp_results = Parallel(n_jobs=num_cores)(delayed(objective_function)(row) for row in X)
    Y = np.array( mp_results )

    x_best, y_best = find_best(X, Y)
    history_best_obj_values.append( y_best )
    #print the current result
    print(f'Iteration:0 Solution: {x_best} Objective: {y_best}')


    for k in range(max_iteration):
        current_step = step_size(max_step, min_step, max_iteration, k)

        # step 2: Guided by the Hen----------------------------------------------------------------
        X1 = np.zeros([population, no_variables])
        Y1 = np.zeros(population)  # store fitness value
        for i in range(population):
            while True:
                X1[i,:] = X[i,:] + current_step * np.random.uniform(-1, 1, no_variables) * ( x_best - X[i,:] )

                ## keep the search space within bounds
                # check lower bound
                mask = X1[i,:] < lb
                X1[i,:][mask] = lb[mask]
                # check upper bound
                mask = X1[i,:] > ub
                X1[i,:][mask] = ub[mask]

                X1[i,:] = np.round(X1[i,:], 0)
                if sum(X1[i,:]) <= available_operators:
                    break

        # # store objective function value for all the population
        # parallel processing
        mp_results = Parallel(n_jobs=num_cores)(delayed(objective_function)(row) for row in X1)
        Y1 = np.array( mp_results )


        # step 3: perform greedy selection
        mask = Y1 < Y
        Y[mask] = Y1[mask]
        X[mask, :] = X1[mask, :]



        # step 4: Guided by other chicks--------------------------------------------------------------
        X2 = np.zeros([population, no_variables])
        Y2 = np.zeros(population)  # store fitness value

        for i in range(population):
            while True: # make sure assigned_operators = available_operators
                if np.random.random() >= probability_random_chicks: #guided by other chicks
                    # select a partner other than self and the best group member
                    while True:
                        idx =np.random.randint(0, population)
                        if ( idx != np.argmin(Y) ) and (idx != i):
                            break
                    X2[i,:] = X[i,:] + current_step * np.random.uniform(-1, 1, no_variables) * (X[i,:] - X[idx, :])

                else: # step 5: random chicks-----------------------
                    X2[i,:] = lb + np.random.uniform(0, 1, no_variables)*(ub - lb)

                ## keep the search space within bounds
                # check lower bound
                mask = X2[i,:] < lb
                X2[i,:][mask] = lb[mask]
                # check upper bound
                mask = X2[i,:] > ub
                X2[i,:][mask] = ub[mask]

                X2[i,:] = np.round(X2[i,:], 0)
                if sum(X2[i,:]) <= available_operators:
                    break

        # # store objective function value for all the population
        # parallel processing
        mp_results = Parallel(n_jobs=num_cores)(delayed(objective_function)(row) for row in X2)
        Y2 = np.array( mp_results )

        # step 6: perform greedy selection
        mask = Y2 < Y
        Y[mask] = Y2[mask]
        X[mask, :] = X2[mask, :]


        # current best solution
        x_best, y_best = find_best(X, Y)
        # current best fitness value
        history_best_obj_values.append( y_best )


        #print the current result
        print(f'Iteration:{k+1} Solution: {x_best} Objective: {y_best}')

        ## break the loop if any of the termination conditions is true
        current_time = time.process_time()
        if (current_time - start_time) >= max_run_time * 60:  # max_run_time in minutes
            break



    # # print the best result
    # print('\n------------------------------------------------------------')
    # print(f'Elapsed time: {current_time - start_time} seconds')
    # print(f'Best objective value : {y_best}')
    # print(f'Best solution        : {x_best}')

    # # create plot
    # plt.figure(dpi = 300, figsize =(6, 4), constrained_layout=True )
    # plt.plot( range(len(history_best_obj_values)), history_best_obj_values, color='r')
    # plt.xlabel('Iterations')
    # plt.ylabel('Objective function value')
    # plt.show()

    return y_best, x_best



