import customtkinter as ctk
import json
import os
import random

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "tasks.json")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DailyFocus(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Daily Focus")
        self.geometry("920x620")
        self.minsize(820, 560)

        self.work_seconds = 25 * 60
        self.break_seconds = 5 * 60
        self.seconds_left = self.work_seconds
        self.running = False
        self.is_break = False
        self.after_id = None
        self.sessions = 0

        self.tasks = self.load_tasks()

        self.build_ui()
        self.refresh_tasks()
        self.update_timer_display()

    def load_tasks(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tasks", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"tasks": self.tasks}, f, ensure_ascii=False, indent=2)

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            sidebar, text="DAILY\nFOCUS", font=ctk.CTkFont(size=30, weight="bold")
        ).pack(pady=(45, 10))

        ctk.CTkLabel(
            sidebar, text="Focus • Plan • Repeat", text_color="#9ca3af"
        ).pack(pady=(0, 35))

        self.sessions_label = ctk.CTkLabel(
            sidebar, text="0", font=ctk.CTkFont(size=42, weight="bold")
        )
        self.sessions_label.pack(pady=(20, 0))
        ctk.CTkLabel(sidebar, text="Focus Sessions", text_color="#9ca3af").pack()

        self.mode_switch = ctk.CTkSwitch(
            sidebar, text="Dark Mode", command=self.toggle_mode
        )
        self.mode_switch.select()
        self.mode_switch.pack(side="bottom", pady=35)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=(8, 25), pady=25)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header, text="Good day 👋", font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")
        self.tip_label = ctk.CTkLabel(
            header, text=self.random_tip(), text_color="#9ca3af"
        )
        self.tip_label.pack(side="right", pady=8)

        timer_card = ctk.CTkFrame(main, corner_radius=20)
        timer_card.grid(row=1, column=0, sticky="ew", pady=18)

        self.mode_label = ctk.CTkLabel(
            timer_card, text="FOCUS", font=ctk.CTkFont(size=15, weight="bold")
        )
        self.mode_label.pack(pady=(25, 0))

        self.timer_label = ctk.CTkLabel(
            timer_card, text="25:00", font=ctk.CTkFont(size=72, weight="bold")
        )
        self.timer_label.pack(pady=4)

        buttons = ctk.CTkFrame(timer_card, fg_color="transparent")
        buttons.pack(pady=(5, 25))

        self.start_button = ctk.CTkButton(
            buttons, text="Start", width=120, height=38, command=self.toggle_timer
        )
        self.start_button.pack(side="left", padx=6)

        ctk.CTkButton(
            buttons, text="Reset", width=120, height=38, command=self.reset_timer
        ).pack(side="left", padx=6)

        tasks_card = ctk.CTkFrame(main, corner_radius=20)
        tasks_card.grid(row=2, column=0, sticky="nsew")
        tasks_card.grid_columnconfigure(0, weight=1)
        tasks_card.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(tasks_card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
        ctk.CTkLabel(
            top, text="Today's Tasks", font=ctk.CTkFont(size=21, weight="bold")
        ).pack(side="left")

        self.task_entry = ctk.CTkEntry(
            top, placeholder_text="Add a new task...", width=230
        )
        self.task_entry.pack(side="left", padx=15, fill="x", expand=True)
        self.task_entry.bind("<Return>", lambda _: self.add_task())

        ctk.CTkButton(top, text="+ Add", width=75, command=self.add_task).pack(
            side="right"
        )

        self.progress_label = ctk.CTkLabel(
            tasks_card, text="", text_color="#9ca3af"
        )
        self.progress_label.grid(row=1, column=0, sticky="w", padx=22)

        self.task_list = ctk.CTkScrollableFrame(tasks_card, fg_color="transparent")
        self.task_list.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)

    def random_tip(self):
        return random.choice([
            "Small steps still count.",
            "Focus on one thing.",
            "You’ve got this ✨",
            "Progress over perfection.",
            "Make today useful."
        ])

    def add_task(self):
        title = self.task_entry.get().strip()
        if not title:
            return
        self.tasks.append({"title": title, "done": False})
        self.task_entry.delete(0, "end")
        self.save_tasks()
        self.refresh_tasks()

    def toggle_task(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.refresh_tasks()

    def delete_task(self, index):
        del self.tasks[index]
        self.save_tasks()
        self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.task_list.winfo_children():
            widget.destroy()

        done = sum(task["done"] for task in self.tasks)
        total = len(self.tasks)
        self.progress_label.configure(text=f"{done}/{total} completed")

        if not self.tasks:
            ctk.CTkLabel(
                self.task_list,
                text="No tasks yet. Add something you want to accomplish today.",
                text_color="#8b93a1"
            ).pack(pady=35)
            return

        for i, task in enumerate(self.tasks):
            row = ctk.CTkFrame(self.task_list, corner_radius=12)
            row.pack(fill="x", pady=5, padx=3)

            cb = ctk.CTkCheckBox(
                row,
                text=task["title"],
                command=lambda idx=i: self.toggle_task(idx)
            )
            cb.pack(side="left", padx=15, pady=11)
            if task["done"]:
                cb.select()

            ctk.CTkButton(
                row, text="×", width=32, fg_color="transparent",
                hover_color="#3b2025", command=lambda idx=i: self.delete_task(idx)
            ).pack(side="right", padx=8)

    def update_timer_display(self):
        minutes, seconds = divmod(self.seconds_left, 60)
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")

    def toggle_timer(self):
        if self.running:
            self.running = False
            self.start_button.configure(text="Start")
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None
        else:
            self.running = True
            self.start_button.configure(text="Pause")
            self.tick()

    def tick(self):
        if not self.running:
            return
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.update_timer_display()
            self.after_id = self.after(1000, self.tick)
        else:
            self.running = False
            self.start_button.configure(text="Start")
            if not self.is_break:
                self.sessions += 1
                self.sessions_label.configure(text=str(self.sessions))
                self.is_break = True
                self.seconds_left = self.break_seconds
                self.mode_label.configure(text="BREAK")
            else:
                self.is_break = False
                self.seconds_left = self.work_seconds
                self.mode_label.configure(text="FOCUS")
            self.update_timer_display()

    def reset_timer(self):
        self.running = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.is_break = False
        self.seconds_left = self.work_seconds
        self.mode_label.configure(text="FOCUS")
        self.start_button.configure(text="Start")
        self.update_timer_display()

    def toggle_mode(self):
        mode = "dark" if self.mode_switch.get() else "light"
        ctk.set_appearance_mode(mode)


if __name__ == "__main__":
    app = DailyFocus()
    app.mainloop()
