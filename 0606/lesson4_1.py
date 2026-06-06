import requests
import pandas as pd

def main():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # list[dict] -> DataFrame
        df = pd.DataFrame(data)

        print(df.head())
        
        # 存成 CSV
        df.to_csv("youbike_data.csv", index=False, encoding="utf-8-sig")
        print("已儲存為 youbike_data.csv")

    else:
        print("下載失敗")

if __name__ == '__main__':
    main()
