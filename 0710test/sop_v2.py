from __future__ import annotations

import re
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import messagebox, ttk
from typing import Literal


ItemType = Literal["main", "sub", "cp", "exception"]


@dataclass
class SOPItem:
    """單一 SOP 項目。"""

    item_type: ItemType
    number: str
    title: str
    details: list[str] = field(default_factory=list)
    owner: str = ""
    storage: str = ""

    @property
    def details_text(self) -> str:
        return "\n".join(self.details)


# =========================================================
# 文字解析
# =========================================================

MAIN_PATTERN = re.compile(
    r"^(?P<number>\d+)[.．、]\s*(?P<title>.+)$"
)

SUB_PATTERN = re.compile(
    r"^(?P<number>\d+\.\d+)[.．、]?\s*(?P<title>.+)$"
)

CP_PATTERN = re.compile(
    r"^(?P<number>CP\s*\d+)\s*[：:、.\-]?\s*(?P<title>.+)$",
    re.IGNORECASE,
)

BULLET_PATTERN = re.compile(
    r"^\s*[-–—•▪●○□☐✓✔＊*]\s*(?P<text>.+)$"
)

NUMBERED_DETAIL_PATTERN = re.compile(
    r"^\s*\d+[.．、]\s*(?P<text>.+)$"
)


def normalize_line(line: str) -> str:
    """統一空白與部分中文符號。"""
    return (
        line.replace("\u3000", " ")
        .replace("\t", " ")
        .strip()
    )


def parse_sop(raw_text: str) -> tuple[str, list[SOPItem]]:
    """
    將原始文字解析為：
    1. 文件標題
    2. SOPItem 清單
    """
    lines = [
        normalize_line(line)
        for line in raw_text.splitlines()
        if normalize_line(line)
    ]

    if not lines:
        return "", []

    document_title = ""
    items: list[SOPItem] = []
    current_item: SOPItem | None = None

    for line in lines:
        # 二級標題要先判斷，否則 1.1 可能被誤認為其他格式。
        sub_match = SUB_PATTERN.match(line)
        if sub_match:
            current_item = SOPItem(
                item_type="sub",
                number=sub_match.group("number"),
                title=sub_match.group("title").strip(),
            )
            items.append(current_item)
            continue

        main_match = MAIN_PATTERN.match(line)
        if main_match:
            title = main_match.group("title").strip()

            item_type: ItemType = "main"
            if "異常" in title:
                item_type = "exception"

            current_item = SOPItem(
                item_type=item_type,
                number=main_match.group("number"),
                title=title,
            )
            items.append(current_item)
            continue

        cp_match = CP_PATTERN.match(line)
        if cp_match:
            current_item = SOPItem(
                item_type="cp",
                number=cp_match.group("number").upper().replace(" ", ""),
                title=cp_match.group("title").strip(),
            )
            items.append(current_item)
            continue

        bullet_match = BULLET_PATTERN.match(line)
        if bullet_match and current_item:
            current_item.details.append(bullet_match.group("text").strip())
            continue

        numbered_detail_match = NUMBERED_DETAIL_PATTERN.match(line)
        if numbered_detail_match and current_item:
            current_item.details.append(
                numbered_detail_match.group("text").strip()
            )
            continue

        # 尚未抓到任何流程項目時，第一行視為文件標題。
        if not items and not document_title:
            document_title = line
            continue

        # 其他普通文字，附加到目前項目的具體做法。
        if current_item:
            current_item.details.append(line)
        elif not document_title:
            document_title = line

    return document_title, items


# =========================================================
# GUI
# =========================================================

class SOPBuilderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("SOP Builder v0.2")
        self.root.geometry("1480x820")
        self.root.minsize(1150, 680)

        self.items: list[SOPItem] = []
        self.selected_index: int | None = None

        self._configure_style()
        self._build_ui()

    # -----------------------------------------------------
    # UI 外觀
    # -----------------------------------------------------

    def _configure_style(self) -> None:
        style = ttk.Style()

        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")

        style.configure(
            "Title.TLabel",
            font=("PingFang TC", 20, "bold"),
        )
        style.configure(
            "Section.TLabel",
            font=("PingFang TC", 11, "bold"),
        )
        style.configure(
            "Treeview",
            font=("PingFang TC", 10),
            rowheight=29,
        )
        style.configure(
            "Treeview.Heading",
            font=("PingFang TC", 10, "bold"),
        )
        style.configure(
            "TButton",
            font=("PingFang TC", 10),
            padding=(9, 5),
        )

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        title = ttk.Label(
            outer,
            text="SOP Builder",
            style="Title.TLabel",
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            outer,
            text="貼上原始內容、解析階層，並在輸出前人工確認與修改。",
        )
        subtitle.pack(anchor="w", pady=(0, 12))

        # 上方文件名稱
        title_frame = ttk.Frame(outer)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            title_frame,
            text="SOP 名稱：",
            style="Section.TLabel",
        ).pack(side="left")

        self.document_title_var = tk.StringVar()
        self.document_title_entry = ttk.Entry(
            title_frame,
            textvariable=self.document_title_var,
        )
        self.document_title_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        # 主區域：左、中、右
        main_paned = ttk.Panedwindow(
            outer,
            orient="horizontal",
        )
        main_paned.pack(fill="both", expand=True)

        self.input_frame = self._build_input_panel(main_paned)
        self.tree_frame = self._build_tree_panel(main_paned)
        self.editor_frame = self._build_editor_panel(main_paned)

        main_paned.add(self.input_frame, weight=3)
        main_paned.add(self.tree_frame, weight=4)
        main_paned.add(self.editor_frame, weight=3)

        # 底部狀態列
        self.status_var = tk.StringVar(
            value="請貼上 SOP 文字，再按「解析文字」。"
        )
        status = ttk.Label(
            outer,
            textvariable=self.status_var,
            anchor="w",
        )
        status.pack(fill="x", pady=(8, 0))

    def _build_input_panel(
        self,
        parent: ttk.Panedwindow,
    ) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(
            parent,
            text="① 原始文字",
            padding=10,
        )

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(
            toolbar,
            text="解析文字",
            command=self.parse_input,
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="清空",
            command=self.clear_all,
        ).pack(side="left", padx=(6, 0))

        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True)

        self.input_text = tk.Text(
            text_frame,
            wrap="word",
            undo=True,
            font=("PingFang TC", 11),
            padx=10,
            pady=10,
        )

        scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.input_text.yview,
        )
        self.input_text.configure(
            yscrollcommand=scrollbar.set
        )

        self.input_text.pack(
            side="left",
            fill="both",
            expand=True,
        )
        scrollbar.pack(side="right", fill="y")

        return frame

    def _build_tree_panel(
        self,
        parent: ttk.Panedwindow,
    ) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(
            parent,
            text="② 結構化內容",
            padding=10,
        )

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(
            toolbar,
            text="新增一級",
            command=lambda: self.add_item("main"),
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="新增二級",
            command=lambda: self.add_item("sub"),
        ).pack(side="left", padx=(5, 0))

        ttk.Button(
            toolbar,
            text="新增 CP",
            command=lambda: self.add_item("cp"),
        ).pack(side="left", padx=(5, 0))

        ttk.Button(
            toolbar,
            text="刪除",
            command=self.delete_selected,
        ).pack(side="left", padx=(12, 0))

        ttk.Button(
            toolbar,
            text="上移",
            command=lambda: self.move_selected(-1),
        ).pack(side="left", padx=(5, 0))

        ttk.Button(
            toolbar,
            text="下移",
            command=lambda: self.move_selected(1),
        ).pack(side="left", padx=(5, 0))

        tree_container = ttk.Frame(frame)
        tree_container.pack(fill="both", expand=True)

        columns = (
            "type",
            "number",
            "title",
            "owner",
        )

        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.tree.heading("type", text="類型")
        self.tree.heading("number", text="編號")
        self.tree.heading("title", text="標題")
        self.tree.heading("owner", text="承辦人")

        self.tree.column(
            "type",
            width=72,
            minwidth=65,
            anchor="center",
            stretch=False,
        )
        self.tree.column(
            "number",
            width=75,
            minwidth=60,
            anchor="center",
            stretch=False,
        )
        self.tree.column(
            "title",
            width=260,
            minwidth=160,
            anchor="w",
        )
        self.tree.column(
            "owner",
            width=110,
            minwidth=80,
            anchor="center",
        )

        y_scroll = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview,
        )
        x_scroll = ttk.Scrollbar(
            tree_container,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        y_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        x_scroll.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_tree_select,
        )
        self.tree.bind(
            "<Double-1>",
            self.on_tree_double_click,
        )

        return frame

    def _build_editor_panel(
        self,
        parent: ttk.Panedwindow,
    ) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(
            parent,
            text="③ 編輯選取項目",
            padding=12,
        )

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)

        ttk.Label(frame, text="類型").grid(
            row=0,
            column=0,
            sticky="w",
            pady=5,
        )

        self.type_var = tk.StringVar(value="main")
        self.type_combo = ttk.Combobox(
            frame,
            textvariable=self.type_var,
            state="readonly",
            values=[
                "main",
                "sub",
                "cp",
                "exception",
            ],
        )
        self.type_combo.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=5,
        )

        ttk.Label(frame, text="編號").grid(
            row=1,
            column=0,
            sticky="w",
            pady=5,
        )

        self.number_var = tk.StringVar()
        ttk.Entry(
            frame,
            textvariable=self.number_var,
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            pady=5,
        )

        ttk.Label(frame, text="標題").grid(
            row=2,
            column=0,
            sticky="w",
            pady=5,
        )

        self.title_var = tk.StringVar()
        ttk.Entry(
            frame,
            textvariable=self.title_var,
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=5,
        )

        ttk.Label(frame, text="承辦人").grid(
            row=3,
            column=0,
            sticky="w",
            pady=5,
        )

        self.owner_var = tk.StringVar()
        ttk.Entry(
            frame,
            textvariable=self.owner_var,
        ).grid(
            row=3,
            column=1,
            sticky="ew",
            pady=5,
        )

        details_label = ttk.Label(
            frame,
            text="具體做法",
        )
        details_label.grid(
            row=4,
            column=0,
            sticky="nw",
            pady=5,
        )

        details_container = ttk.Frame(frame)
        details_container.grid(
            row=4,
            column=1,
            sticky="nsew",
            pady=5,
        )
        details_container.rowconfigure(0, weight=1)
        details_container.columnconfigure(0, weight=1)

        self.details_text = tk.Text(
            details_container,
            wrap="word",
            height=12,
            undo=True,
            font=("PingFang TC", 10),
            padx=7,
            pady=7,
        )

        details_scrollbar = ttk.Scrollbar(
            details_container,
            orient="vertical",
            command=self.details_text.yview,
        )
        self.details_text.configure(
            yscrollcommand=details_scrollbar.set
        )

        self.details_text.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        details_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        ttk.Label(frame, text="資料存放").grid(
            row=5,
            column=0,
            sticky="w",
            pady=5,
        )

        self.storage_var = tk.StringVar()
        ttk.Entry(
            frame,
            textvariable=self.storage_var,
        ).grid(
            row=5,
            column=1,
            sticky="ew",
            pady=5,
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 0),
        )

        ttk.Button(
            button_frame,
            text="套用修改",
            command=self.apply_changes,
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="取消選取",
            command=self.clear_editor,
        ).pack(side="left", padx=(7, 0))

        return frame

    # -----------------------------------------------------
    # 解析與顯示
    # -----------------------------------------------------

    def parse_input(self) -> None:
        raw_text = self.input_text.get(
            "1.0",
            "end",
        ).strip()

        if not raw_text:
            messagebox.showwarning(
                "尚未輸入內容",
                "請先在左側貼上 SOP 文字。",
            )
            return

        title, parsed_items = parse_sop(raw_text)

        if not parsed_items:
            messagebox.showwarning(
                "無法解析",
                "沒有辨識到一級標題、二級標題或 CP。",
            )
            return

        self.document_title_var.set(title)
        self.items = parsed_items
        self.selected_index = None

        self.refresh_tree()
        self.clear_editor()

        self.status_var.set(
            f"解析完成：共 {len(self.items)} 個項目。"
        )

    def refresh_tree(
        self,
        selected_index: int | None = None,
    ) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        type_labels = {
            "main": "一級",
            "sub": "二級",
            "cp": "CP",
            "exception": "異常",
        }

        for index, item in enumerate(self.items):
            indent = ""
            if item.item_type == "sub":
                indent = "　└ "

            item_id = self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    type_labels[item.item_type],
                    item.number,
                    indent + item.title,
                    item.owner,
                ),
            )

            if item.item_type == "main":
                self.tree.item(
                    item_id,
                    tags=("main",),
                )
            elif item.item_type == "cp":
                self.tree.item(
                    item_id,
                    tags=("cp",),
                )
            elif item.item_type == "exception":
                self.tree.item(
                    item_id,
                    tags=("exception",),
                )

        self.tree.tag_configure(
            "main",
            background="#DDEBF7",
        )
        self.tree.tag_configure(
            "cp",
            background="#FFF2CC",
        )
        self.tree.tag_configure(
            "exception",
            background="#FCE4D6",
        )

        if (
            selected_index is not None
            and 0 <= selected_index < len(self.items)
        ):
            item_id = str(selected_index)
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            self.tree.see(item_id)

    # -----------------------------------------------------
    # 選取與編輯
    # -----------------------------------------------------

    def on_tree_select(
        self,
        _event: tk.Event | None = None,
    ) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        index = int(selection[0])

        if not 0 <= index < len(self.items):
            return

        self.selected_index = index
        item = self.items[index]

        self.type_var.set(item.item_type)
        self.number_var.set(item.number)
        self.title_var.set(item.title)
        self.owner_var.set(item.owner)
        self.storage_var.set(item.storage)

        self.details_text.delete("1.0", "end")
        self.details_text.insert(
            "1.0",
            item.details_text,
        )

        self.status_var.set(
            f"目前選取：{item.number} {item.title}"
        )

    def on_tree_double_click(
        self,
        _event: tk.Event,
    ) -> None:
        """
        雙擊表格列後，把游標移到右側標題欄。
        """
        self.on_tree_select()
        self.root.after(
            50,
            lambda: self._focus_title_entry(),
        )

    def _focus_title_entry(self) -> None:
        for child in self.editor_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                variable_name = str(child.cget("textvariable"))
                if variable_name == str(self.title_var):
                    child.focus_set()
                    child.selection_range(0, "end")
                    break

    def apply_changes(self) -> None:
        if self.selected_index is None:
            messagebox.showwarning(
                "尚未選取",
                "請先在中間表格選取一個項目。",
            )
            return

        title = self.title_var.get().strip()

        if not title:
            messagebox.showwarning(
                "標題不可空白",
                "請填寫項目標題。",
            )
            return

        item = self.items[self.selected_index]

        item.item_type = self.type_var.get()  # type: ignore[assignment]
        item.number = self.number_var.get().strip()
        item.title = title
        item.owner = self.owner_var.get().strip()
        item.storage = self.storage_var.get().strip()

        detail_lines = [
            line.strip()
            for line in self.details_text.get(
                "1.0",
                "end",
            ).splitlines()
            if line.strip()
        ]
        item.details = detail_lines

        current_index = self.selected_index
        self.refresh_tree(current_index)

        self.status_var.set(
            f"已更新：{item.number} {item.title}"
        )

    def clear_editor(self) -> None:
        self.selected_index = None
        self.type_var.set("main")
        self.number_var.set("")
        self.title_var.set("")
        self.owner_var.set("")
        self.storage_var.set("")
        self.details_text.delete("1.0", "end")

        for selected in self.tree.selection():
            self.tree.selection_remove(selected)

    # -----------------------------------------------------
    # 新增、刪除、排序
    # -----------------------------------------------------

    def add_item(self, item_type: ItemType) -> None:
        new_item = SOPItem(
            item_type=item_type,
            number=self._suggest_number(item_type),
            title="新項目",
        )

        if self.selected_index is None:
            insert_index = len(self.items)
        else:
            insert_index = self.selected_index + 1

        self.items.insert(
            insert_index,
            new_item,
        )

        self.refresh_tree(insert_index)
        self.on_tree_select()

        self.status_var.set(
            "已新增項目，請在右側修改內容。"
        )

    def _suggest_number(
        self,
        item_type: ItemType,
    ) -> str:
        if item_type in {"main", "exception"}:
            main_numbers = []

            for item in self.items:
                if (
                    item.item_type in {"main", "exception"}
                    and item.number.isdigit()
                ):
                    main_numbers.append(int(item.number))

            next_number = (
                max(main_numbers) + 1
                if main_numbers
                else 1
            )
            return str(next_number)

        if item_type == "cp":
            cp_numbers = []

            for item in self.items:
                match = re.search(
                    r"\d+",
                    item.number,
                )
                if item.item_type == "cp" and match:
                    cp_numbers.append(
                        int(match.group())
                    )

            next_number = (
                max(cp_numbers) + 1
                if cp_numbers
                else 1
            )
            return f"CP{next_number}"

        # 新增二級標題時，尋找選取位置之前最近的一級標題。
        parent_number = "1"

        start_index = (
            self.selected_index
            if self.selected_index is not None
            else len(self.items) - 1
        )

        for index in range(
            start_index,
            -1,
            -1,
        ):
            item = self.items[index]

            if (
                item.item_type in {"main", "exception"}
                and item.number
            ):
                parent_number = item.number
                break

        sub_numbers = []

        for item in self.items:
            if item.item_type != "sub":
                continue

            match = re.fullmatch(
                rf"{re.escape(parent_number)}\.(\d+)",
                item.number,
            )

            if match:
                sub_numbers.append(
                    int(match.group(1))
                )

        next_sub_number = (
            max(sub_numbers) + 1
            if sub_numbers
            else 1
        )

        return f"{parent_number}.{next_sub_number}"

    def delete_selected(self) -> None:
        if self.selected_index is None:
            messagebox.showwarning(
                "尚未選取",
                "請先選取要刪除的項目。",
            )
            return

        item = self.items[self.selected_index]

        confirmed = messagebox.askyesno(
            "確認刪除",
            f"確定刪除「{item.number} {item.title}」嗎？",
        )

        if not confirmed:
            return

        deleted_index = self.selected_index
        del self.items[deleted_index]

        self.clear_editor()

        next_index: int | None = None
        if self.items:
            next_index = min(
                deleted_index,
                len(self.items) - 1,
            )

        self.refresh_tree(next_index)

        if next_index is not None:
            self.on_tree_select()

        self.status_var.set("已刪除項目。")

    def move_selected(self, direction: int) -> None:
        if self.selected_index is None:
            messagebox.showwarning(
                "尚未選取",
                "請先選取要移動的項目。",
            )
            return

        old_index = self.selected_index
        new_index = old_index + direction

        if not 0 <= new_index < len(self.items):
            return

        self.items[old_index], self.items[new_index] = (
            self.items[new_index],
            self.items[old_index],
        )

        self.selected_index = new_index
        self.refresh_tree(new_index)
        self.on_tree_select()

        self.status_var.set("已調整項目順序。")

    # -----------------------------------------------------
    # 清空
    # -----------------------------------------------------

    def clear_all(self) -> None:
        if self.input_text.get("1.0", "end").strip() or self.items:
            confirmed = messagebox.askyesno(
                "確認清空",
                "確定清空目前所有內容嗎？",
            )
            if not confirmed:
                return

        self.input_text.delete("1.0", "end")
        self.document_title_var.set("")
        self.items.clear()
        self.clear_editor()
        self.refresh_tree()

        self.status_var.set(
            "內容已清空，請貼上新的 SOP 文字。"
        )


def main() -> None:
    root = tk.Tk()
    SOPBuilderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()