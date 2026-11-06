import tkinter as tk
from tkinter import ttk
import json
import os
import threading
import time

CONFIG_FILE = "comfort_settings.json"

class ComfortZoneApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- НАСТРОЙКИ ОКНА ---
        self.title("ComfortZone — Ваше уютное цифровое пространство")
        self.geometry("850x650")
        self.minsize(700, 500)

        # --- STATE MANAGEMENT (Хранение состояния) ---
        self.font_size_modifier = 0
        self.is_online = True
        self.sound_enabled = True
        self.draft_text = ""
        self.last_deleted_task = None
        self.current_theme = "Тёмная"

        # Исходные данные
        self.tasks = [
            {"id": 1, "title": "Провести CustDev интервью (понять боли юзера)", "status": "Выполнено"},
            {"id": 2, "title": "Заложить Variables тем в Figma Design System", "status": "В процессе"},
            {"id": 3, "title": "Добавить VoiceOver / TalkBack разметку", "status": "Ожидание"}
        ]

        self.themes = {
            "Тёмная": {
                "bg": "#1E1E1E", "sidebar_bg": "#252526", "card_bg": "#2D2D30",
                "fg": "#FFFFFF", "text_sec": "#A0A0A0", "accent": "#007ACC",
                "banner_bg": "#2D2D30", "banner_fg": "#E0E0E0",
                "offline_bg": "#5A1F1F", "offline_fg": "#FFC0C0"
            },
            "Светлая": {
                "bg": "#F9F9F9", "sidebar_bg": "#F0F0F0", "card_bg": "#FFFFFF",
                "fg": "#111111", "text_sec": "#666666", "accent": "#007ACC",
                "banner_bg": "#EAEAEA", "banner_fg": "#333333",
                "offline_bg": "#FADBD8", "offline_fg": "#78281F"
            }
        }

        self.load_settings()
        self.apply_theme_colors()
        self.create_widgets()
        self.update_widget_fonts()  # Применяем размер из настроек

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.font_size_modifier = data.get("font_size", 0)
                    self.sound_enabled = data.get("sound", True)
                    self.draft_text = data.get("draft", "")
                    self.current_theme = data.get("theme", "Тёмная")
            except Exception:
                pass

    def save_settings(self):
        data = {
            "font_size": self.font_size_modifier,
            "sound": self.sound_enabled,
            "draft": self.draft_text_input.get("1.0", tk.END).strip() if hasattr(self, 'draft_text_input') else self.draft_text,
            "theme": self.current_theme
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            if hasattr(self, 'status_label') and self.is_online:
                self.status_label.config(text=" ✅ Изменения автоматически сохранены")
        except Exception:
            pass

    def apply_theme_colors(self):
        colors = self.themes[self.current_theme]
        self.configure(bg=colors["bg"])

    def get_font(self, size, weight="normal"):
        return ("Segoe UI", size + self.font_size_modifier, weight)

    def create_widgets(self):
        colors = self.themes[self.current_theme]

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 🛠 ЛЕВАЯ ПАНЕЛЬ
        # ==========================================
        self.sidebar = tk.Frame(self, bg=colors["sidebar_bg"], width=240)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.lbl_logo = tk.Label(self.sidebar, text="🛋 ComfortZone", font=self.get_font(18, "bold"), bg=colors["sidebar_bg"], fg=colors["fg"])
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.lbl_theme = tk.Label(self.sidebar, text="Режим оформления:", font=self.get_font(11, "bold"), bg=colors["sidebar_bg"], fg=colors["text_sec"])
        self.lbl_theme.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_menu = tk.OptionMenu(self.sidebar, self.theme_var, "Тёмная", "Светлая", command=self.change_theme_event)
        self.theme_menu.config(font=self.get_font(11), bg=colors["card_bg"], fg=colors["fg"], highlightthickness=0, bd=1, relief="flat")
        self.theme_menu.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.lbl_font = tk.Label(self.sidebar, text="Размер текста:", font=self.get_font(11, "bold"), bg=colors["sidebar_bg"], fg=colors["text_sec"])
        self.lbl_font.grid(row=3, column=0, padx=20, pady=(15, 0), sticky="w")
        
        self.font_slider = tk.Scale(self.sidebar, from_=-4, to=6, orient="horizontal", command=self.change_font_size, bg=colors["sidebar_bg"], fg=colors["fg"], highlightthickness=0, showvalue=False)
        self.font_slider.set(self.font_size_modifier)
        self.font_slider.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.sound_var = tk.BooleanVar(value=self.sound_enabled)
        self.sound_check = tk.Checkbutton(self.sidebar, text="Звуковой отклик", variable=self.sound_var, command=self.toggle_sound, font=self.get_font(11), bg=colors["sidebar_bg"], fg=colors["fg"], selectcolor=colors["sidebar_bg"], activebackground=colors["sidebar_bg"], activeforeground=colors["fg"])
        self.sound_check.grid(row=5, column=0, padx=20, pady=15, sticky="w")

        self.net_var = tk.BooleanVar(value=self.is_online)
        self.net_check = tk.Checkbutton(self.sidebar, text="Имитировать сеть", variable=self.net_var, command=self.toggle_network, font=self.get_font(11), bg=colors["sidebar_bg"], fg=colors["fg"], selectcolor=colors["sidebar_bg"], activebackground=colors["sidebar_bg"], activeforeground=colors["fg"])
        self.net_check.grid(row=6, column=0, padx=20, pady=10, sticky="w")

        # ==========================================
        # 📋 ГЛАВНАЯ ЧАСТЬ
        # ==========================================
        self.main_container = tk.Frame(self, bg=colors["bg"])
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)

        banner_bg_color = colors["offline_bg"] if not self.is_online else colors["banner_bg"]
        banner_fg_color = colors["offline_fg"] if not self.is_online else colors["banner_fg"]
        self.status_banner = tk.Frame(self.main_container, bg=banner_bg_color, height=40)
        self.status_banner.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.status_banner.pack_propagate(False)
        
        banner_text = " 📡 Вы не в сети. Изменения сохраняются локально." if not self.is_online else " ✨ Приложение готово к комфортной работе"
        self.status_label = tk.Label(self.status_banner, text=banner_text, font=self.get_font(11), bg=banner_bg_color, fg=banner_fg_color)
        self.status_label.pack(side="left", padx=15, pady=8)

        self.draft_frame = tk.Frame(self.main_container, bg=colors["card_bg"])
        self.draft_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15), ipady=5)
        
        self.lbl_draft_title = tk.Label(self.draft_frame, text="Умный черновик (Текст сохраняется автоматически при вводе):", font=self.get_font(11, "bold"), bg=colors["card_bg"], fg=colors["text_sec"])
        self.lbl_draft_title.pack(anchor="w", padx=10, pady=(5,0))
        
        self.draft_text_input = tk.Text(self.draft_frame, height=3, font=self.get_font(11), bg=colors["bg"], fg=colors["fg"], insertbackground=colors["fg"], bd=0)
        self.draft_text_input.pack(fill="x", padx=10, pady=5)
        self.draft_text_input.insert("1.0", self.draft_text)
        self.draft_text_input.bind("<KeyRelease>", lambda e: self.save_settings())

        self.tasks_frame = tk.Frame(self.main_container, bg=colors["card_bg"])
        self.tasks_frame.grid(row=2, column=0, sticky="nsew")
        self.tasks_frame.grid_columnconfigure(0, weight=1)
        self.tasks_frame.grid_rowconfigure(1, weight=1)

        tasks_header = tk.Frame(self.tasks_frame, bg=colors["card_bg"])
        tasks_header.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        
        self.lbl_tasks_title = tk.Label(tasks_header, text="Фокус-сессия (Задачи)", font=self.get_font(14, "bold"), bg=colors["card_bg"], fg=colors["fg"])
        self.lbl_tasks_title.pack(side="left")
        
        self.undo_btn = tk.Button(tasks_header, text="↩ Отменить удаление (Undo)", state="disabled", command=self.trigger_undo, font=self.get_font(10), bg=colors["bg"], fg=colors["fg"], activebackground=colors["accent"], highlightthickness=0, relief="flat", bd=1)
        self.undo_btn.pack(side="right")

        self.skeleton_frame = tk.Frame(self.tasks_frame, bg=colors["card_bg"])
        for i in range(3):
            sk = tk.Frame(self.skeleton_frame, bg=colors["banner_bg"], height=16, width=420)
            sk.grid(row=i, column=0, pady=12, padx=20, sticky="w")

        self.task_list_canvas = tk.Canvas(self.tasks_frame, bg=colors["card_bg"], highlightthickness=0)
        self.task_list_scroll = tk.Frame(self.task_list_canvas, bg=colors["card_bg"])
        
        self.trigger_skeleton_loading()

    def trigger_skeleton_loading(self):
        self.task_list_canvas.grid_forget()
        self.skeleton_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        
        def end_loading():
            time.sleep(0.5)
            if self.winfo_exists():
                self.skeleton_frame.grid_forget()
                self.task_list_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
                self.task_list_canvas.create_window((0, 0), window=self.task_list_scroll, anchor="nw")
                self.refresh_task_list()
            
        threading.Thread(target=end_loading, daemon=True).start()

    def refresh_task_list(self):
        for widget in self.task_list_scroll.winfo_children():
            widget.destroy()

        colors = self.themes[self.current_theme]

        if not self.tasks:
            empty_lbl = tk.Label(self.task_list_scroll, text="✨ Полный дзен! Все задачи выполнены.\nКогнитивная нагрузка на сегодня равна нулю.", font=self.get_font(12, "italic"), bg=colors["card_bg"], fg=colors["text_sec"])
            empty_lbl.pack(pady=40, fill="x", expand=True)
            return

        for task in self.tasks:
            item = tk.Frame(self.task_list_scroll, bg=colors["bg"], height=45)
            item.pack(fill="x", padx=15, pady=5)
            item.pack_propagate(False)

            lbl = tk.Label(item, text=task["title"], font=self.get_font(11), bg=colors["bg"], fg=colors["fg"])
            lbl.pack(side="left", padx=15)
            
            status_colors = {"Выполнено": "#2ecc71", "В процессе": "#f39c12", "Ожидание": "#95a5a6"}
            badge = tk.Label(item, text=f" {task['status']} ", bg=status_colors.get(task["status"]), fg="white", font=self.get_font(10, "bold"))
            badge.pack(side="left", padx=5)

            del_btn = tk.Button(item, text="🗑", font=self.get_font(11), bg=colors["bg"], fg="#E74C3C", bd=0, activebackground=colors["bg"], highlightthickness=0, command=lambda t_id=task["id"]: self.delete_task(t_id))
            del_btn.pack(side="right", padx=15)

    def update_widget_fonts(self):
        """Обновление шрифтов всех существующих статических элементов без пересоздания UI"""
        if hasattr(self, 'lbl_logo'): self.lbl_logo.config(font=self.get_font(18, "bold"))
        if hasattr(self, 'lbl_theme'): self.lbl_theme.config(font=self.get_font(11, "bold"))
        if hasattr(self, 'theme_menu'): self.theme_menu.config(font=self.get_font(11))
        if hasattr(self, 'lbl_font'): self.lbl_font.config(font=self.get_font(11, "bold"))
        if hasattr(self, 'sound_check'): self.sound_check.config(font=self.get_font(11))
        if hasattr(self, 'net_check'): self.net_check.config(font=self.get_font(11))
        if hasattr(self, 'status_label'): self.status_label.config(font=self.get_font(11))
        if hasattr(self, 'lbl_draft_title'): self.lbl_draft_title.config(font=self.get_font(11, "bold"))
        if hasattr(self, 'draft_text_input'): self.draft_text_input.config(font=self.get_font(11))
        if hasattr(self, 'lbl_tasks_title'): self.lbl_tasks_title.config(font=self.get_font(14, "bold"))
        if hasattr(self, 'undo_btn'): self.undo_btn.config(font=self.get_font(10))
        self.refresh_task_list()

    def delete_task(self, task_id):
        self.play_feedback_signal()
        for task in self.tasks:
            if task["id"] == task_id:
                self.last_deleted_task = task
                self.tasks.remove(task)
                break
        
        self.undo_btn.config(state="normal")
        self.refresh_task_list()
        
        def expire_undo():
            time.sleep(7)
            if self.winfo_exists():
                self.undo_btn.config(state="disabled")
        threading.Thread(target=expire_undo, daemon=True).start()

    def trigger_undo(self):
        if self.last_deleted_task:
            self.play_feedback_signal()
            self.tasks.append(self.last_deleted_task)
            self.tasks.sort(key=lambda x: x["id"])
            self.last_deleted_task = None
            self.undo_btn.config(state="disabled")
            self.refresh_task_list()

    def change_theme_event(self, new_theme: str):
        self.play_feedback_signal()
        self.current_theme = new_theme
        self.apply_theme_colors()
        self.save_settings()
        self.create_widgets()
        self.update_widget_fonts()

    def change_font_size(self, value):
        self.font_size_modifier = int(value)
        self.save_settings()
        self.update_widget_fonts()  # Плавное изменение шрифта без мерцания

    def toggle_sound(self):
        self.sound_enabled = self.sound_var.get()
        self.save_settings()
        self.play_feedback_signal()

    def toggle_network(self):
        self.is_online = self.net_var.get()
        self.play_feedback_signal()
        colors = self.themes[self.current_theme]
        
        if self.is_online:
            self.status_banner.config(bg=colors["banner_bg"])
            self.status_label.config(text=" ✨ Приложение синхронизировано с облаком", bg=colors["banner_bg"], fg=colors["banner_fg"])
        else:
            self.status_banner.config(bg=colors["offline_bg"])
            self.status_label.config(text=" 📡 Вы не в сети. Мы сохраняем все ваши изменения локально.", bg=colors["offline_bg"], fg=colors["offline_fg"])

    def play_feedback_signal(self):
        if self.sound_enabled:
            self.bell()

    def on_closing(self):
        self.save_settings()
        self.destroy()

if __name__ == "__main__":
    app = ComfortZoneApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()