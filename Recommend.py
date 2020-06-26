import csv
import os
from collections import defaultdict
from time import time

import pandas as pd
from surprise import Dataset, Reader, SVDpp, SlopeOne, NormalPredictor, KNNBaseline, KNNBasic, KNNWithMeans, \
    KNNWithZScore, BaselineOnly, CoClustering
from surprise import SVD
from surprise import dump
# Dump 파일명
from surprise.model_selection import cross_validate

traindump_file_name = "MyTrainPredictDump"
csv_name = "face_interaction.csv"
file_name = os.path.expanduser(traindump_file_name)


class Recommend():
    def __init__(self):
        self.df = None
        self.train()
        # self.predictions, self.algo = dump.load(file_name)

    def checkBestAlgorithm(self):
        self.df = pd.read_csv(csv_name)
        reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(self.df[['user_id', 'item_id', 'rating']], reader)
        benchmark = []
        rmseTuple = []
        # 모든 알고리즘을 literate화 시켜서 반복문을 실행시킨다.
        for algorithm in [SVD(), SVDpp(), SlopeOne(), NormalPredictor(), KNNBaseline(), KNNBasic(),
                          KNNWithMeans(),
                          KNNWithZScore(), BaselineOnly(), CoClustering()]:
            # 교차검증을 수행하는 단계.
            results = cross_validate(algorithm, data, measures=['RMSE'], cv=3, verbose=False)

            # 결과 저장과 알고리즘 이름 추가.
            tmp = pd.DataFrame.from_dict(results).mean(axis=0)
            rmseTuple.append((algorithm, tmp['test_rmse']))
            tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
            benchmark.append(tmp)
        print(pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse'))
        print("\n")
        rmseTuple.sort(key=lambda x: x[1])

        print("Best algorithm : ")
        print(str(rmseTuple[0]).split(' ')[0].split('.')[-1])
        return rmseTuple[0]

    def train(self):
        # 점수 1~ 10
        self.df = pd.read_csv(csv_name)
        reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(self.df[['user_id', 'item_id', 'rating']], reader)
        # TrainSet
        trainset = data.build_full_trainset()
        # algo = self.checkBestAlgorithm()[0]
        algo = SVD()
        algo.fit(trainset)
        # TestSet
        testset = trainset.build_anti_testset()
        predictions = algo.test(testset)

        self.predictions = predictions
        self.algo = algo

        # Validate Algo
        cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
        # Save Dump
        dump.dump(file_name, predictions=predictions, algo=algo)

    def get_recommend_by_user_id(self, user_id, n=10):
        print("User ID :", user_id)
        ests = [(iid, est) for uid, iid, true_r, est, _ in self.predictions if uid == user_id]
        if ests is not None:
            ests.sort(key=lambda x: x[1], reverse=True)
            results = ests[:n]

            for (iid, est) in results:
                print("Item id : ", iid, "Estimate Value : ", est)

            item_id = [result[0] for result in results]
            return item_id
        else:
            return []

    def get_popularity_item_id(self, n=10):
        item_list = []
        popularDf = self.df.groupby('item_id').count()
        for i, row in popularDf.iterrows():
            item_list.append((row.name, row['user_id']))
        item_list.sort(key=lambda x: x[1], reverse=True)
        item_id = [result[0] for result in item_list[:n]]
        print("pop" + str(item_id))
        return item_id

    def get_top_n(self, n=10):
        # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in self.predictions:
            top_n[uid].append((iid, est))

        # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n

    def add_interaction(self, uid, iid, type="view"):
        value = 0
        if type == "view":
            value = 2
        elif type == "like":
            value = 4
        elif type == "cart":
            value = 7
        elif type == "order":
            value = 10
        elif type == "face":
            value = 10

        with open(csv_name, 'a') as fd:
            fd.write("\n{},{},{},{}".format(uid, iid, value, int(time())))

    def csv_to_dic(self):
        with open(csv_name) as f:
            tab_reader = csv.DictReader(f, delimiter=',')
            for row in tab_reader:
                user_id = row["user_id"]
                item_id = row["item_id"]
                value = row["rating"]
                print(row)


if __name__ == '__main__':
    recommend = Recommend()
    recommend.checkBestAlgorithm()
    # recommend.get_recommend_by_user_id(6, 10)

    # recommend.add_interaction(10,2400,"view")
    # recommend.get_recommend_by_user_id(10, 10)
    # recommend.get_recommend_by_user_id(10, 10)
    # recommend.get_recommend_by_user_id(10, 10)
    # recommend.get_recommend_by_user_id(10, 10)

    # top_n = get_top_n(predictions, n=10)
    # for uid, user_ratings in top_n.items():
    #     print(uid, [iid for (iid, _) in user_ratings])
