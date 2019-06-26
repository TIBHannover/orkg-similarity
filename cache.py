import numpy as np
import pandas as pd
from similarity import fast_similarity as sim
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from time import time
from connection.neo4j import Neo4J
#import seaborn as sns
#import matplotlib.pyplot as plt


__VERBOSE__ = False
___THREAD_COUNT___ = 5
neo4j = Neo4J.getInstance()


class Cache:
    def __init__(self):
        self.df = None
        self.store = None

    @staticmethod
    def complete_similarity_matrix(df):
        new_df = df.fillna(0) + df.fillna(0).T
        np.fill_diagonal(new_df.values, 100)
        return new_df

    def get_top_similar(self, node, topk=3):
        x = self.df.sort_values(by=node, ascending=False)
        x = x.loc[[index for index in x.index if index != node], node]
        return x[:topk].to_dict()

    def create_new_cache(self):
        dic = {}
        length = len(neo4j.contributions)
        st = time()
        for first in range(length):
            # print(f'started {first} out of {length}')
            temp = {}
            if __VERBOSE__:
                print(f"first: {first}")
            for second in range(first, length):
                if __VERBOSE__:
                    print(f"second: {second}")
                temp[neo4j.contributions[second]] = sim.compute_similarity_between_two_entities(
                    neo4j.contributions[first],
                    neo4j.contributions[second])
            dic[neo4j.contributions[first]] = temp
        ed = time()
        print(f'TIME: ========== {ed-st} SECONDS ==========')
        self.df = pd.DataFrame.from_dict(dic)
        self.df = Cache.complete_similarity_matrix(self.df)

    def update_cache(self, new_resource):
        temp = {}
        for second in range(len(neo4j.contributions)):
            if __VERBOSE__:
                print(f"computed against: {second}")
            temp[neo4j.contributions[second]] = sim.compute_similarity_between_two_entities(new_resource,
                                                                                            neo4j.contributions[second])
            neo4j.contributions.append(new_resource)
        self.df.loc[new_resource] = temp        # Add the new similarities to the matrix
        self.df[new_resource] = self.df.loc[new_resource].T     # Mirror the similarity in the matrix
        self.df.loc[new_resource, new_resource] = 100.0     # Add the similarity for the resource with itself

    def create_new_cache_parallel(self):
        # TODO: Investigate why threading performing worse than serial execution
        pool = ThreadPool(___THREAD_COUNT___)
        # resources = resources[310:450]
        length = len(neo4j.contributions)
        res = {}
        st = time()
        dics = pool.map(partial(Cache.threading_compute_similar, length, neo4j.contributions), range(length))
        pool.terminate()
        ed = time()
        print(f'TIME: ========== {ed-st} SECONDS ==========')
        for dic in dics:
            res[dic[0]] = dic[1]
        self.df = pd.DataFrame.from_dict(res)
        self.df = Cache.complete_similarity_matrix(self.df)

    @staticmethod
    def threading_compute_similar(length, resources, first):
        temp = {}
        for second in range(first, length):
            temp[resources[second]] = sim.compute_similarity_between_two_entities(resources[first], resources[second])
        return resources[first], temp

    def save_cache(self):
        if self.df is not None:
            self.store = pd.HDFStore('similarity.h5')
            self.store['df'] = self.df
            self.store.close()
        else:
            raise RuntimeError("DataFrame is not initialized yet")

    def load_cache(self):
        self.store = pd.HDFStore('similarity.h5')
        if self.store is not None and self.store['df'] is not None:
            self.df = self.store['df']
            self.store.close()
        else:
            self.store.close()
            raise RuntimeError("Store is not initialized correctly")


if __name__ == '__main__':
    store = Cache()
    store.create_new_cache()
    #store.update_cache("R1319")
    #store.create_new_cache_parallel()
    #store.save_cache()
    #store.load_cache()

    # TODO: extract heat map function to util file
    '''
    
    sns.heatmap(df, annot=True)
    plt.show()
    
    x = df.sort_values(by='R1310', ascending=False)
    x = x.loc[[index for index in x.index if index != 'R1310'], 'R1310']
    x[:3].to_dict()
    print(x[:3])'''
