import os
import time
import numpy as np
from pandas import Series, DataFrame

#encoding:UTF-8
def yield_test(n):
    for i in range(n):
        call(i)
        print("i=",i)
    else:
        yield call(i)
        #做一些其它的事情
    print("do something.")
    print("end.")

def call(i):
    return i*2

#使用for循环
for i in yield_test(5):
    print(i,",")