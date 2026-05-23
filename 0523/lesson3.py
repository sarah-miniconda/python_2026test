# 猜數子遊戲，chatgpt幫忙

import random

# 随机产生 1~100 的数字
answer = random.randint(1, 100)

print("=== 猜数字游戏 ===")
print("请输入 1~100 的数字")

count = 0

while True:

    guess = int(input("請輸入數字："))
    count += 1

    # 判断大小
    if guess > answer:
        print("太大了！")

    elif guess < answer:
        print("太小了！")

    else:
        print(f"恭喜猜對了！答案是 {answer}")
        print(f"恭喜你猜对了！一共猜測{count}次")
        break
