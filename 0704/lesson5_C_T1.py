import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

import requests
import yfinance as yf
import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TaiwanStockAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("台灣股票相關性分析器")
        self.root.geometry("1000x720")

        self.stock_df = self.load_stock_list()
        self.stock_options = self.stock_df["display"].tolist()

        self.stock_a = tk.StringVar()
        self.stock_b = tk.StringVar()
        self.period = tk.StringVar(value="今年以來")

        self.build_ui()

    def load_stock_list(self):
        """
        優先從 FinMind 抓台股清單。
        如果網路失敗，就使用內建常用股票清單。
        """

        try:
            url = "https://api.finmindtrade.com/api/v4/data"
            params = {"dataset": "TaiwanStockInfo"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()["data"]
            df = pd.DataFrame(data)

            df = df[["stock_id", "stock_name", "type"]].dropna()
            df = df[df["stock_id"].str.match(r"^\d{4}$")]

            def yahoo_suffix(row):
                if row["type"] == "twse":
                    return f"{row['stock_id']}.TW"
                elif row["type"] == "tpex":
                    return f"{row['stock_id']}.TWO"
                else:
                    return f"{row['stock_id']}.TW"

            df["yahoo_code"] = df.apply(yahoo_suffix, axis=1)
            df["display"] = df["stock_name"] + " (" + df["stock_id"] + ")"

            return df.sort_values("stock_id").reset_index(drop=True)

        except Exception:
            common = {
                "台積電": "2330.TW",
                "聯電": "2303.TW",
                "聯發科": "2454.TW",
                "鴻海": "2317.TW",
                "廣達": "2382.TW",
                "華碩": "2357.TW",
                "中華電": "2412.TW",
                "富邦金": "2881.TW",
                "國泰金": "2882.TW",
                "中信金": "2891.TW",
                "元大台灣50": "0050.TW",
                "國泰永續高股息": "00878.TW",
            }

            rows = []
            for name, code in common.items():
                rows.append({
                    "stock_id": code.split(".")[0],
                    "stock_name": name,
                    "type": "twse",
                    "yahoo_code": code,
                    "display": f"{name} ({code.split('.')[0]})"
                })

            return pd.DataFrame(rows)

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill="x")

        ttk.Label(frame, text="股票 A").grid(row=0, column=0, sticky="w")
        self.combo_a = ttk.Combobox(
            frame,
            textvariable=self.stock_a,
            values=self.stock_options,
            width=30
        )
        self.combo_a.grid(row=0, column=1, padx=10)

        ttk.Label(frame, text="股票 B").grid(row=0, column=2, sticky="w")
        self.combo_b = ttk.Combobox(
            frame,
            textvariable=self.stock_b,
            values=self.stock_options,
            width=30
        )
        self.combo_b.grid(row=0, column=3, padx=10)

        ttk.Label(frame, text="期間").grid(row=1, column=0, sticky="w", pady=10)

        period_box = ttk.Combobox(
            frame,
            textvariable=self.period,
            values=["三個月", "六個月", "今年以來", "一年"],
            width=15,
            state="readonly"
        )
        period_box.grid(row=1, column=1, sticky="w", padx=10)

        analyze_btn = ttk.Button(frame, text="開始分析", command=self.analyze)
        analyze_btn.grid(row=1, column=3, sticky="e")

        self.result_text = tk.Text(self.root, height=9, font=("Arial", 13))
        self.result_text.pack(fill="x", padx=15, pady=10)

        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(fill="both", expand=True, padx=15, pady=10)

        if len(self.stock_options) >= 2:
            self.stock_a.set(self.stock_options[0])
            self.stock_b.set(self.stock_options[1])

    def get_stock_code(self, display_name):
        row = self.stock_df[self.stock_df["display"] == display_name]
        if row.empty:
            return None
        return row.iloc[0]["yahoo_code"]

    def get_start_date(self):
        today = date.today()

        if self.period.get() == "三個月":
            return today - timedelta(days=90)
        elif self.period.get() == "六個月":
            return today - timedelta(days=180)
        elif self.period.get() == "一年":
            return today - timedelta(days=365)
        else:
            return date(today.year, 1, 1)

    def analyze(self):
        name_a = self.stock_a.get()
        name_b = self.stock_b.get()

        code_a = self.get_stock_code(name_a)
        code_b = self.get_stock_code(name_b)

        if not code_a or not code_b:
            messagebox.showerror("錯誤", "請選擇兩檔股票")
            return

        if code_a == code_b:
            messagebox.showerror("錯誤", "請選擇不同股票")
            return

        start_date = self.get_start_date()

        try:
            data = yf.download(
                [code_a, code_b],
                start=start_date,
                interval="1d",
                auto_adjust=True,
                progress=False
            )

            close = data["Close"].dropna()

            close = close.rename(columns={
                code_a: name_a,
                code_b: name_b
            })

            returns = close.pct_change().dropna()

            corr = returns[name_a].corr(returns[name_b])
            cov = returns[name_a].cov(returns[name_b])

            avg_a = returns[name_a].mean()
            avg_b = returns[name_b].mean()

            vol_a = returns[name_a].std()
            vol_b = returns[name_b].std()

            self.show_result(
                name_a, name_b, corr, cov, avg_a, avg_b, vol_a, vol_b
            )

            self.draw_charts(close, returns, name_a, name_b)

        except Exception as e:
            messagebox.showerror("分析失敗", str(e))

    def show_result(self, name_a, name_b, corr, cov, avg_a, avg_b, vol_a, vol_b):
        self.result_text.delete("1.0", tk.END)

        if corr >= 0.8:
            level = "高度正相關"
        elif corr >= 0.4:
            level = "中度正相關"
        elif corr >= 0.2:
            level = "低度正相關"
        elif corr > -0.2:
            level = "幾乎沒有線性關係"
        elif corr > -0.4:
            level = "低度負相關"
        elif corr > -0.8:
            level = "中度負相關"
        else:
            level = "高度負相關"

        text = f"""
股票 A：{name_a}
股票 B：{name_b}

日報酬率相關係數：{corr:.4f}
判斷：{level}

日報酬率共變數：{cov:.8f}

{name_a} 平均日報酬率：{avg_a:.4%}
{name_b} 平均日報酬率：{avg_b:.4%}

{name_a} 日波動率：{vol_a:.4%}
{name_b} 日波動率：{vol_b:.4%}
"""
        self.result_text.insert(tk.END, text)

    def draw_charts(self, close, returns, name_a, name_b):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(10, 6), dpi=100)

        ax1 = fig.add_subplot(211)
        close.plot(ax=ax1)
        ax1.set_title("收盤價走勢")
        ax1.set_xlabel("日期")
        ax1.set_ylabel("收盤價")

        ax2 = fig.add_subplot(212)
        ax2.scatter(returns[name_a], returns[name_b], alpha=0.6)
        ax2.set_title("日報酬率散點圖")
        ax2.set_xlabel(name_a)
        ax2.set_ylabel(name_b)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaiwanStockAnalyzer(root)
    root.mainloop()