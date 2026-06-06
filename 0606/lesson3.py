import requests
# from requests import Response 
# 可用上述，後面就改為 >>> response:Response = requests.get(url)


# uv add requests


def main():
    url:str = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
# ubike 的api資料
# :str >> typhint 型別類型

    # print("這裏是main function的命名空間")

    response : requests.Response = requests.get(url)

# 200 代表成功, 404不成功
    if response.status_code == 200:
        data :list[dict] = response.json()
        print("下載成功")
        print(type(data))
        print(len(data))
        print(data[0])
    else:
        print("下載失敗")
        print(response.status_code)

if __name__ == '__main__':
    main()

