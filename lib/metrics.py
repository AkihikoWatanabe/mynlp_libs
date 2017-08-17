# coding=utf-8

"""
分類器を評価する際の、Metricを計算し表示す
機能を提供するモジュール
"""

from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report
from collections import namedtuple

metrics = namedtuple(
        'metrics',
        ('acc', 'pre', 'rec', 'f1')
)


class MetricsForCrossValidation():
    """ CrossValidationを行う際のMetric全般に関する機能を提供するクラス
    """

    def __init__(self):
        """ 正解ラベル、予測ラベルを格納するリスト、およびラベルの一覧を初期化。

        Attributes:
            label_true (list): 正解ラベルを格納するリスト
            label_pred (list): 予測ラベルを格納するリスト
        """

        self.label_true = []
        self.label_pred = []

    @staticmethod
    def calc_metrics(label_true, label_pred, labels):
        """ 与えられたラベル情報から、各種メトリックを計算して返す。

        Args:
            label_true (list): 正解ラベルの系列
            label_pred (list): 予測ラベルの系列
            labels (list): ラベルの表層
        """

        acc = accuracy_score(
                    label_true,
                    label_pred
        )
        pre = precision_score(
                    label_true,
                    label_pred,
                    labels=labels,
                    average="micro"
        )
        rec = recall_score(
                    label_true,
                    label_pred,
                    labels=labels,
                    average="micro"
        )
        f1 = f1_score(
                    label_true,
                    label_pred,
                    labels=labels,
                    average="micro"
        )

        return metrics(acc, pre, rec, f1)

    def add_result(self, label_true, label_pred):
        """ Metricの計算を行うための予測結果を格納する。

        予測結果を格納するメソッド。
        基本的には各foldにおける正解・予測ラベルを随時追加していく使い方になる。
        内部的には、正解・予測ラベルをそのままメンバ変数に追加する。
        したがって、基本的にはMetricの計算にはマイクロ平均を用いることになる。

        Args:
            label_true (list): 正解ラベルの系列
            label_pred (list): 予測ラベルの系列
        """

        self.label_true += label_true
        self.label_pred += label_pred

    def show_result(self):
        """ 格納した予測結果から、Metricを計算し表示する。

        Accuracyと、Precision, Recall, F1-scoreを計算し表示する。
        ただし、AccuracyはMicroAverage, Precision, Recall, F1-scoreは
        classification_reportを用いて計算するため、Weighted Averageである。
        """

        acc = accuracy_score(
                self.label_true,
                self.label_pred
        )
        print("Accuracy (MicroAverage): {}".format(acc))
        print(classification_report(self.label_true, self.label_pred))
