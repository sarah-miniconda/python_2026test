# 猜數子遊戲，chatgpt幫忙

import tkinter as tk
from tkinter import messagebox
import random

# =========================
# 遊戲初始化
# =========================
answer = random.randint(1, 100)
count = 0

# =========================
# 猜測功能
# =========================
def check_guess():
    global count

    guess = entry.get()

    # 檢查輸入
    if not guess.isdigit():
        result_label.config(
            text="⚠ 請輸入數字！",
            fg="#ff4d6d"
        )
        return

    guess = int(guess)
    count += 1

    # 判斷大小
    if guess > answer:
        result_label.config(
            text=f"📈 太大了！目前猜了 {count} 次",
            fg="#ff9f1c"
        )

    elif guess < answer:
        result_label.config(
            text=f"📉 太小了！目前猜了 {count} 次",
            fg="#00b4d8"
        )

    else:
        result_label.config(
            text=f"🎉 恭喜答對！答案是 {answer}",
            fg="#2a9d8f"
        )

        messagebox.showinfo(
            "恭喜！",
            f"你猜對了！\n答案是 {answer}\n總共猜了 {count} 次"
        )

        guess_button.config(state="disabled")


# =========================
# 重新開始
# =========================
def restart_game():
    global answer, count

    answer = random.randint(1, 100)
    count = 0

    entry.delete(0, tk.END)

    result_label.config(
        text="請輸入 1~100 的數字",
        fg="white"
    )

    guess_button.config(state="normal")


# =========================
# 主視窗
# =========================
window = tk.Tk()
window.title("🎮 猜數字遊戲")
window.geometry("520x420")
window.configure(bg="#1e1e2f")
window.resizable(False, False)

# =========================
# 標題
# =========================
title_label = tk.Label(
    window,
    text="🎲 猜數字遊戲",
    font=("Helvetica", 28, "bold"),
    bg="#1e1e2f",
    fg="#ffffff"
)

title_label.pack(pady=25)

# =========================
# 說明文字
# =========================
info_label = tk.Label(
    window,
    text="我已經想好 1~100 的數字啦！",
    font=("Helvetica", 14),
    bg="#1e1e2f",
    fg="#cfcfcf"
)

info_label.pack(pady=5)

# =========================
# 輸入框
# =========================
entry = tk.Entry(
    window,
    font=("Helvetica", 22),
    justify="center",
    width=10,
    bd=0,
    relief="flat",
    bg="#ffffff",
    fg="#000000"
)

entry.pack(pady=25, ipady=10)

# =========================
# 猜測按鈕
# =========================
guess_button = tk.Button(
    window,
    text="猜看看！",
    font=("Helvetica", 16, "bold"),
    bg="#7b2cbf",
    fg="white",
    activebackground="#9d4edd",
    activeforeground="white",
    padx=25,
    pady=10,
    bd=0,
    cursor="hand2",
    command=check_guess
)

guess_button.pack(pady=10)

# =========================
# 重新開始按鈕
# =========================
restart_button = tk.Button(
    window,
    text="重新開始",
    font=("Helvetica", 13),
    bg="#3a86ff",
    fg="white",
    activebackground="#5390ff",
    activeforeground="white",
    padx=20,
    pady=8,
    bd=0,
    cursor="hand2",
    command=restart_game
)

restart_button.pack(pady=10)

# =========================
# 結果顯示
# =========================
result_label = tk.Label(
    window,
    text="請輸入 1~100 的數字",
    font=("Helvetica", 16, "bold"),
    bg="#1e1e2f",
    fg="white"
)

result_label.pack(pady=30)

# =========================
# Enter 鍵直接猜
# =========================
window.bind("<Return>", lambda event: check_guess())

# =========================
# 執行程式
# =========================
window.mainloop()