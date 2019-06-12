import numpy as np
import pandas as pd
from py2neo import Graph
#import similarity as sim
import fast_similarity as sim
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from time import time
#import seaborn as sns
#import matplotlib.pyplot as plt


__VERBOSE__ = True
___THREAD_COUNT___ = 5


class Cache:
    def __init__(self):
        self.graph = Graph()
        self.df = None
        self.store = None
        self.resources = None

    def get_papers(self):
        papers = self.graph.run("MATCH (n)-[p]->() WHERE p.predicate_id = 'P1001' RETURN n.resource_id as id").data()
        return [p["id"] for p in papers]

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
        self.resources = self.get_papers()
        self.resources = self.resources[310:313]
        dic = {}
        length = len(self.resources)
        st = time()
        for first in range(length):
            print(f'started {first} out of {length}')
            temp = {}
            if __VERBOSE__:
                print(f"first: {first}")
            for second in range(first, length):
                if __VERBOSE__:
                    print(f"second: {second}")
                temp[self.resources[second]] = sim.compute_similarity_between_two_entities(self.resources[first],
                                                                                           self.resources[second])
            dic[self.resources[first]] = temp
        ed = time()
        print(f'TIME: ========== {ed-st} SECONDS ==========')
        self.df = pd.DataFrame.from_dict(dic)
        self.df = Cache.complete_similarity_matrix(self.df)

    def update_cache(self, new_resource):
        temp = {}
        for second in range(len(self.resources)):
            if __VERBOSE__:
                print(f"computed against: {second}")
            temp[self.resources[second]] = sim.compute_similarity_between_two_entities(new_resource,
                                                                                       self.resources[second])
        self.resources.append(new_resource)
        self.df.loc[new_resource] = temp        # Add the new similarities to the matrix
        self.df[new_resource] = self.df.loc[new_resource].T     # Mirror the similarity in the matrix
        self.df.loc[new_resource, new_resource] = 100.0     # Add the similarity for the resource with itself

    def create_new_cache_parallel(self):
        pool = ThreadPool(___THREAD_COUNT___)
        resources = self.get_papers()
        resources = resources[310:325]
        length = len(resources)
        res = {}
        st = time()
        dics = pool.map(partial(Cache.threading_compute_similar, length, resources), range(length))
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
    store.update_cache("R1319")
    #store.create_new_cache_parallel()
    #store.save_cache()
    #store.load_cache()
    '''
    resources = store.get_papers()
    resources = resources[310:320]
    dic = {}
    length = len(resources)
    st = time()
    for first in range(length):
        temp = {}
        if __VERBOSE__:
            print(f"first: {first}")
        for second in range(first, length):
            if __VERBOSE__:
                print(f"second: {second}")
            temp[resources[second]] = sim.compute_similarity_between_two_entities(resources[first], resources[second])
        dic[resources[first]] = temp
    ed = time()
    print(f'TIME: ========== {ed-st} SECONDS ==========')
    df = pd.DataFrame.from_dict(dic)
    df = Cache.complete_similarity_matrix(df)
    print(df.head())
    sns.heatmap(df, annot=True)
    # plt.show()
    x = df.sort_values(by='R1310', ascending=False)
    x = x.loc[[index for index in x.index if index != 'R1310'], 'R1310']
    x[:3].to_dict()
    print(x[:3])'''
