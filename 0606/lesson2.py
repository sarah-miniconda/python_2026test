#   主執行檔
if __name__ == "__main__":
    n = 10
    print (n)
    # n在這裡屬於文件變數


# 1
def main():
    print("這裏是main function的命名空間")
    print(n)

if __name__ == '__main__':
    n = 10
    main()
    # 執行後，先print字，再10。因爲跑到main的時候又回到最上面了，按順序print。

# 2
def main():
    print("這裏是main function的命名空間")
    print(n)

if __name__ == '__main__':
    n = 10
    main()
    # 執行後，先10, 再文字。

# 3
def main():
    n = 10 
    # n = 10 只能在main呼叫時使用
    print("這裏是main function的命名空間")
    print(n)

if __name__ == '__main__':
    main()
    print(n)
    # print 不出來。



