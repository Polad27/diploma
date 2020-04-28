import os
from multiprocessing.pool import ThreadPool as Pool


def run_process(process):
    os.system(f'py {os.getcwd()}\\scraping\\{process}')

if __name__ ==  '__main__':
    processes = [f for f in os.listdir('scraping') if f.endswith('.py')]
    print(os.listdir())
    for process in processes:
        print(process)
        run_process(process)
    # pool = Pool(processes=len(processes))
    # pool.map(run_process, processes)
    # pool.join()
    # pool.close()


