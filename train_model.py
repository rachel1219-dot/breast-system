import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# 加载数据集
data = load_breast_cancer()

# 提取前10个均值特征
X = data.data[:, :10]
y = data.target

# 划分训练集和测试集（8:2）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练随机森林模型
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 预测并计算准确率
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"模型准确率: {accuracy:.4f}")

# 确保model目录存在
os.makedirs('model', exist_ok=True)

# 保存模型到model/rf_model.pkl
model_path = os.path.join('model', 'rf_model.pkl')
joblib.dump(clf, model_path)
print(f"模型已保存到: {model_path}")

# 打印特征名称
print("\n使用的前10个特征:")
for i, feature in enumerate(data.feature_names[:10]):
    print(f"{i+1}. {feature}")
