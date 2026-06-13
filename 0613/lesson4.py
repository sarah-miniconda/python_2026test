import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font = FontProperties(fname="/System/Library/Fonts/STHeiti Medium.ttc")

# 讀取 CSV
df = pd.read_csv("考試分數_3年6班.csv")

# 篩選趙冠宇的資料
zhao = df[df["學生姓名"] == "趙冠宇"]

# 取出各科成績
scores = zhao.iloc[0][["語文", "數學", "英語", "物理", "化學"]]

# 繪製長條圖
fig = plt.figure(figsize=(6, 4))
ax = fig.add_subplot(1, 1, 1)

ax.bar(scores.index, scores.values)

ax.set_title("趙冠宇成績", fontproperties=font)
ax.set_xlabel("科目", fontproperties=font)
ax.set_ylabel("分數", fontproperties=font)
ax.set_ylim(0, 100)
ax.set_xticks(range(len(scores.index)))
ax.set_xticklabels(scores.index, fontproperties=font)

plt.show()