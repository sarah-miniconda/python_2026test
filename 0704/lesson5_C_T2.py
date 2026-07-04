# taiwan_stock_analyzer.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from itertools import combinations

import requests
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# 解決 matplotlib 中文亂碼
plt.rcParams["font.sans-serif"] = [
    "PingFang TC",
    "Microsoft JhengHei",
    "Arial Unicode MS",
    "Heiti TC",
    "SimHei",
]
plt.rcParams["axes.unicode_minus"] = False


class TaiwanStockAnalyzer4:
    def __init__(self, root):
        self.root = root
        self.root.title("台灣股票相關性分析器（4 檔對比）")
        self.root.geometry("1250x850")

        self.stock_df = self.load_stock_list()
        self.stock_options = self.stock_df["display"].tolist()

        self.stock_vars = [tk.StringVar() for _ in range(4)]
        self.period = tk.StringVar(value="今年以來")

        self.canvas = None

        self.build_ui()

    def load_stock_list(self):
        try:
            url = "https://api.finmindtrade.com/api/v4/data"
            params = {"dataset": "TaiwanStockInfo"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            df = pd.DataFrame(response.json()["data"])
            df = df[["stock_id", "stock_name", "type"]].dropna()
            df = df[df["stock_id"].str.match(r"^\d{4}$")]

            def to_yahoo_code(row):
                if row["type"] == "tpex":
                    return f"{row['stock_id']}.TWO"
                return f"{row['stock_id']}.TW"

            df["yahoo_code"] = df.apply(to_yahoo_code, axis=1)
            df["display"] = df["stock_name"] + " (" + df["stock_id"] + ")"

            return df.sort_values("stock_id").reset_index(drop=True)

        except Exception:
            common = {
                "元大台灣50": "0050.TW",
                "元大中型100": "0051.TW",
                "台積電": "2330.TW",
                "聯電": "2303.TW",
                "聯發科": "2454.TW",
                "鴻海": "2317.TW",
                "廣達": "2382.TW",
                "中華電": "2412.TW",
                "富邦金": "2881.TW",
                "國泰金": "2882.TW",
                "中信金": "2891.TW",
                "國泰永續高股息": "00878.TW",
            }

            rows = []
            for name, code in common.items():
                stock_id = code.split(".")[0]
                rows.append({
                    "stock_id": stock_id,
                    "stock_name": name,
                    "type": "twse",
                    "yahoo_code": code,
                    "display": f"{name} ({stock_id})",
                })

            return pd.DataFrame(rows)

    def build_ui(self):
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")

        for i in range(4):
            ttk.Label(top, text=f"股票 {i + 1}").grid(row=0, column=i, sticky="w")

            box = ttk.Combobox(
                top,
                textvariable=self.stock_vars[i],
                values=self.stock_options,
                width=24,
            )
            box.grid(row=1, column=i, padx=5, pady=5)

        ttk.Label(top, text="期間").grid(row=0, column=4, sticky="w")

        period_box = ttk.Combobox(
            top,
            textvariable=self.period,
            values=["三個月", "六個月", "今年以來", "一年"],
            width=15,
            state="readonly",
        )
        period_box.grid(row=1, column=4, padx=5)

        ttk.Button(top, text="開始分析", command=self.analyze).grid(
            row=1, column=5, padx=10
        )

        ttk.Button(top, text="清除圖表", command=self.clear_chart).grid(
            row=1, column=6, padx=5
        )

        self.result_text = tk.Text(self.root, height=9, font=("Arial", 12))
        self.result_text.pack(fill="x", padx=12, pady=8)

        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(fill="both", expand=True, padx=12, pady=8)

        defaults = ["台積電 (2330)", "聯發科 (2454)", "鴻海 (2317)", "中華電 (2412)"]

        for var, default in zip(self.stock_vars, defaults):
            if default in self.stock_options:
                var.set(default)

    def get_stock_code(self, display_name):
        row = self.stock_df[self.stock_df["display"] == display_name]
        if row.empty:
            return None
        return row.iloc[0]["yahoo_code"]

    def get_start_date(self):
        today = date.today()

        if self.period.get() == "三個月":
            return today - timedelta(days=90)
        if self.period.get() == "六個月":
            return today - timedelta(days=180)
        if self.period.get() == "一年":
            return today - timedelta(days=365)

        return date(today.year, 1, 1)

    def analyze(self):
        names = [var.get() for var in self.stock_vars]
        codes = [self.get_stock_code(name) for name in names]

        if any(code is None for code in codes):
            messagebox.showerror("錯誤", "請選擇 4 檔股票")
            return

        if len(set(codes)) < 4:
            messagebox.showerror("錯誤", "請選擇 4 檔不同股票")
            return

        try:
            data = yf.download(
                codes,
                start=self.get_start_date(),
                interval="1d",
                auto_adjust=True,
                progress=False,
            )

            close = data["Close"].dropna(how="all")
            rename_map = dict(zip(codes, names))
            close = close.rename(columns=rename_map)
            close = close.dropna()

            returns = close.pct_change().dropna()

            corr = returns.corr()
            cov = returns.cov()

            self.show_result(names, returns, corr, cov)
            self.draw_charts(close, returns, corr, names)

        except Exception as e:
            messagebox.showerror("分析失敗", str(e))

    def show_result(self, names, returns, corr, cov):
        self.result_text.delete("1.0", tk.END)

        lines = []
        lines.append("統計指標（以日報酬率計算）\n")

        for name in names:
            avg_daily = returns[name].mean()
            vol_daily = returns[name].std()
            annual_return = avg_daily * 252
            annual_vol = vol_daily * (252 ** 0.5)

            lines.append(
                f"{name}\n"
                f"  平均日報酬率：{avg_daily:.4%}\n"
                f"  日波動率：{vol_daily:.4%}\n"
                f"  年化報酬率估計：{annual_return:.2%}\n"
                f"  年化波動率估計：{annual_vol:.2%}\n"
            )

        lines.append("\n兩兩相關係數：")
        for a, b in combinations(names, 2):
            lines.append(f"  {a} vs {b}：{corr.loc[a, b]:.4f}")

        lines.append("\n兩兩共變數：")
        for a, b in combinations(names, 2):
            lines.append(f"  {a} vs {b}：{cov.loc[a, b]:.8f}")

        self.result_text.insert(tk.END, "\n".join(lines))

    def draw_charts(self, close, returns, corr, names):
        self.clear_chart()

        fig = Figure(figsize=(12, 8), dpi=100)

        # 1. 收盤價走勢：轉成起始日 = 100，方便不同股價比較
        ax1 = fig.add_subplot(2, 2, 1)
        normalized_close = close / close.iloc[0] * 100
        normalized_close.plot(ax=ax1)
        ax1.set_title("收盤價走勢比較（起始日 = 100）")
        ax1.set_xlabel("日期")
        ax1.set_ylabel("累積表現")
        ax1.grid(True, alpha=0.3)

        # 2. 相關係數熱力圖
        ax2 = fig.add_subplot(2, 2, 2)
        im = ax2.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")

        ax2.set_title("日報酬率相關係數熱力圖")
        ax2.set_xticks(range(len(names)))
        ax2.set_yticks(range(len(names)))
        ax2.set_xticklabels(names, rotation=30, ha="right")
        ax2.set_yticklabels(names)

        for i in range(len(names)):
            for j in range(len(names)):
                value = corr.iloc[i, j]
                ax2.text(
                    j,
                    i,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    color="white" if abs(value) > 0.6 else "black",
                    fontsize=10,
                )

        fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)

        # 3. 股票1 vs 股票2 散點圖
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.scatter(returns[names[0]], returns[names[1]], alpha=0.6)
        ax3.axhline(0, color="gray", linewidth=0.8)
        ax3.axvline(0, color="gray", linewidth=0.8)
        ax3.set_title(f"{names[0]} vs {names[1]} 日報酬率散點圖")
        ax3.set_xlabel(names[0])
        ax3.set_ylabel(names[1])
        ax3.grid(True, alpha=0.3)

        # 4. 股票3 vs 股票4 散點圖
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.scatter(returns[names[2]], returns[names[3]], alpha=0.6)
        ax4.axhline(0, color="gray", linewidth=0.8)
        ax4.axvline(0, color="gray", linewidth=0.8)
        ax4.set_title(f"{names[2]} vs {names[3]} 日報酬率散點圖")
        ax4.set_xlabel(names[2])
        ax4.set_ylabel(names[3])
        ax4.grid(True, alpha=0.3)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.canvas = None


if __name__ == "__main__":
    root = tk.Tk()
    app = TaiwanStockAnalyzer4(root)
    root.mainloop()