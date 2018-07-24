'''
Multiprocessing test based on the very useful examples found here:
https://sebastianraschka.com/Articles/2014_multiprocessing.html
'''

import multiprocessing as mp
import time

# Define an output queue
output = mp.Queue()
   
def odds():
    val = 1
    while True:
        print(val)
        val += 2
        time.sleep(2)
  
def evens():
    time.sleep(1)
    val = 2
    while True:
        print(val)
        val += 2
        time.sleep(2)

# Setup a list of processes that we want to run
processes = []
processes.append( mp.Process(target=odds) )
processes.append( mp.Process(target=evens) )

# Run processes
for p in processes:
    p.start()

'''
Exit the completed processes
for p in processes:
    p.join()

Get process results from the output queue
results = [output.get() for p in processes]

print(results)
'''
