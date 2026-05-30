# 猜數子遊戲，chatgpt幫忙(修改)

import tkinter as tk
from tkinter import messagebox
import random

# =========================
# 游戏初始化
# =========================

answer = random.randint(1, 100)
count = 0

# =========================
# 检查答案
# =========================

def check_guess():
    global count

    try:
        guess = int(entry.get())
    except ValueError:
        result_label.config(
            text="⚠ 請輸入數字哦！",
            fg="#ff4d8d"
        )
        return

    count += 1
    count_label.config(text=f"猜測次數：{count}")

    if guess > answer:
        result_label.config(
            text="📈 太大了～",
            fg="#d63384"
        )

    elif guess < answer:
        result_label.config(
            text="📉 太小了～",
            fg="#6f42c1"
        )

    else:
        result_label.config(
            text="🎉 猜對啦！",
            fg="#2a9d8f"
        )

        messagebox.showinfo(
            "恭喜",
            f"💖 猜對了！\n\n答案是 {answer}\n共猜了 {count} 次"
        )

        guess_btn.config(state="disabled")

    entry.delete(0, tk.END)


# =========================
# 重新開始
# =========================

def restart_game():
    global answer, count

    answer = random.randint(1, 100)
    count = 0

    count_label.config(text="猜測次數：0")

    result_label.config(
        text="請輸入 1 ~ 100",
        fg="#555555"
    )

    entry.delete(0, tk.END)

    guess_btn.config(state="normal")


# =========================
# 主視窗
# =========================

window = tk.Tk()
window.title("🎀 粉紫少女猜數字")
window.geometry("520x500")
window.configure(bg="#FDF2FF")
window.resizable(False, False)

# =========================
# 標題
# =========================

title_label = tk.Label(
    window,
    text="🎀 猜數字遊戲 🎀",
    font=("Helvetica", 26, "bold"),
    bg="#FDF2FF",
    fg="#C77DFF"
)

title_label.pack(pady=25)

# =========================
# 副標題
# =========================

subtitle = tk.Label(
    window,
    text="我已經想好一個 1 ~ 100 的數字啦！",
    font=("Helvetica", 13),
    bg="#FDF2FF",
    fg="#666666"
)

subtitle.pack()

# =========================
# 卡片區
# =========================

card = tk.Frame(
    window,
    bg="white",
    bd=0,
    padx=30,
    pady=30
)

card.pack(pady=25)

# =========================
# 輸入框
# =========================

entry = tk.Entry(
    card,
    font=("Helvetica", 22),
    justify="center",
    width=10,
    relief="solid",
    bd=1
)

entry.pack(pady=10)

# =========================
# 猜測按鈕
# =========================

guess_btn = tk.Button(
    card,
    text="💜 猜看看 💜",
    font=("Helvetica", 14, "bold"),
    bg="#C77DFF",
    fg="black",
    activebackground="#D8B4FE",
    width=14,
    command=check_guess
)

guess_btn.pack(pady=15)

# =========================
# 次數
# =========================

count_label = tk.Label(
    card,
    text="猜測次數：0",
    font=("Helvetica", 12),
    bg="white",
    fg="#666666"
)

count_label.pack()

# =========================
# 結果
# =========================

result_label = tk.Label(
    window,
    text="請輸入 1 ~ 100",
    font=("Helvetica", 18, "bold"),
    bg="#FDF2FF",
    fg="#555555"
)

result_label.pack(pady=20)

# =========================
# 重新開始
# =========================

restart_btn = tk.Button(
    window,
    text="🌸 重新開始",
    font=("Helvetica", 12),
    bg="#FFAFCC",
    fg="black",
    activebackground="#FFC8DD",
    width=12,
    command=restart_game
)

restart_btn.pack()

# =========================
# Enter 鍵直接猜
# =========================

window.bind("<Return>", lambda event: check_guess())

# =========================
# 啟動
# =========================

window.mainloop()