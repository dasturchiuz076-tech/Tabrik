import customtkinter as ctk
from tkinter import messagebox, colorchooser
from datetime import datetime, date
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import json

# ==================== DASTUR SOZLAMALARI ====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

APP_NAME = "💼 NTX Byudjet Nazorati"
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)
DATA_FILE = os.path.join(DATA_FOLDER, "transactions.json")


# ==================== YORDAMCHI FUNKSIYALAR ====================
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ==================== ASOSIY ILLOVA SINFI ====================
class BudgetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1150x700")
        self.active_user = None
        self.is_fullscreen = False

        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        self.container = ctk.CTkFrame(self, corner_radius=20)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.frames = {}
        for F in (LoginPage, MainMenu, IncomePage, ExpensePage, BalancePage, HistoryPage, SettingsPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()


# ==================== LOGIN SAHIFASI ====================
class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="💰 NTX Byudjet Dasturi", font=("Segoe UI", 32, "bold")).pack(pady=60)

        self.username = ctk.CTkEntry(self, placeholder_text="Foydalanuvchi nomi", width=320, height=45)
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(self, placeholder_text="Parol", show="*", width=320, height=45)
        self.password.pack(pady=10)

        ctk.CTkButton(self, text="Kirish", command=self.login, width=220, height=45).pack(pady=30)
        self.info_label = ctk.CTkLabel(self, text="", text_color="red")
        self.info_label.pack()

    def login(self):
        u, p = self.username.get(), self.password.get()
        if u.strip() == "" or p.strip() == "":
            self.info_label.configure(text="⚠️ Login va parolni kiriting!")
        else:
            self.controller.active_user = u
            messagebox.showinfo("Xush kelibsiz", f"Salom, {u}!")
            self.controller.show_frame(MainMenu)


# ==================== ASOSIY MENYU ====================
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="🏠 Asosiy menyu", font=("Segoe UI", 26, "bold")).pack(pady=40)

        btn = {"width": 280, "height": 55, "corner_radius": 10, "font": ("Segoe UI", 15, "bold")}
        ctk.CTkButton(self, text="💰 Daromad qo‘shish", command=lambda: controller.show_frame(IncomePage), **btn).pack(pady=10)
        ctk.CTkButton(self, text="💸 Xarajat qo‘shish", command=lambda: controller.show_frame(ExpensePage), **btn).pack(pady=10)
        ctk.CTkButton(self, text="📊 Balans", command=lambda: controller.show_frame(BalancePage), **btn).pack(pady=10)
        ctk.CTkButton(self, text="📜 Tarix", command=lambda: controller.show_frame(HistoryPage), **btn).pack(pady=10)
        ctk.CTkButton(self, text="⚙️ Sozlamalar", command=lambda: controller.show_frame(SettingsPage), **btn).pack(pady=10)
        ctk.CTkButton(self, text="🚪 Chiqish", fg_color="#c62828", command=self.exit_app, **btn).pack(pady=25)

    def exit_app(self):
        if messagebox.askyesno("Chiqish", "Dasturdan chiqmoqchimisiz?"):
            self.controller.destroy()


# ==================== DAROMAD SAHIFASI ====================
class IncomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="💰 Daromad qo‘shish", font=("Segoe UI", 24, "bold")).pack(pady=25)

        self.amount = ctk.CTkEntry(self, placeholder_text="Miqdor (so‘mda)", width=300)
        self.amount.pack(pady=10)
        self.note = ctk.CTkEntry(self, placeholder_text="Izoh (masalan: maosh)", width=300)
        self.note.pack(pady=10)
        self.category = ctk.CTkComboBox(self, values=["Maosh", "Bonus", "Boshqa"], width=300)
        self.category.pack(pady=10)
        self.date_entry = DateEntry(self, width=17, background="darkblue", foreground="white")
        self.date_entry.pack(pady=10)

        ctk.CTkButton(self, text="Qo‘shish", command=self.add_income, width=200).pack(pady=15)
        ctk.CTkButton(self, text="⬅ Orqaga", command=lambda: controller.show_frame(MainMenu)).pack(pady=10)

    def add_income(self):
        try:
            data = load_data()
            record = {
                "type": "income",
                "amount": float(self.amount.get()),
                "note": self.note.get(),
                "category": self.category.get(),
                "date": str(self.date_entry.get_date())
            }
            data.append(record)
            save_data(data)
            messagebox.showinfo("✅", "Daromad qo‘shildi!")
        except ValueError:
            messagebox.showerror("Xato", "Miqdor raqam bo‘lishi kerak!")


# ==================== XARAJAT SAHIFASI ====================
class ExpensePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="💸 Xarajat qo‘shish", font=("Segoe UI", 24, "bold")).pack(pady=25)

        self.amount = ctk.CTkEntry(self, placeholder_text="Miqdor (so‘mda)", width=300)
        self.amount.pack(pady=10)
        self.note = ctk.CTkEntry(self, placeholder_text="Izoh (masalan: transport, ovqat...)", width=300)
        self.note.pack(pady=10)
        self.category = ctk.CTkComboBox(self, values=["Ovqat", "Transport", "O‘yin", "Boshqa"], width=300)
        self.category.pack(pady=10)
        self.date_entry = DateEntry(self, width=17, background="darkblue", foreground="white")
        self.date_entry.pack(pady=10)

        ctk.CTkButton(self, text="Qo‘shish", command=self.add_expense, width=200, fg_color="#ff5252").pack(pady=15)
        ctk.CTkButton(self, text="⬅ Orqaga", command=lambda: controller.show_frame(MainMenu)).pack(pady=10)

    def add_expense(self):
        try:
            data = load_data()
            record = {
                "type": "expense",
                "amount": float(self.amount.get()),
                "note": self.note.get(),
                "category": self.category.get(),
                "date": str(self.date_entry.get_date())
            }
            data.append(record)
            save_data(data)
            messagebox.showinfo("✅", "Xarajat qo‘shildi!")
        except ValueError:
            messagebox.showerror("Xato", "Miqdor raqam bo‘lishi kerak!")


# ==================== BALANS SAHIFASI ====================
class BalancePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.canvas = None

        ctk.CTkLabel(self, text="📊 Balans", font=("Segoe UI", 24, "bold")).pack(pady=25)
        ctk.CTkButton(self, text="Hisobni yangilash", command=self.show_balance, width=200).pack(pady=10)
        ctk.CTkButton(self, text="⬅ Orqaga", command=lambda: controller.show_frame(MainMenu)).pack(pady=10)

    def show_balance(self):
        data = load_data()
        income = sum(x["amount"] for x in data if x["type"] == "income")
        expense = sum(x["amount"] for x in data if x["type"] == "expense")
        balance = income - expense

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(5, 4), facecolor="#1e1e1e")
        ax.bar(["Daromad", "Xarajat", "Balans"], [income, expense, balance],
               color=["#4caf50", "#e53935", "#2196f3"], width=0.5)
        ax.set_facecolor("#1e1e1e")
        ax.set_title("Moliya holati", color="white")
        ax.tick_params(colors="white")

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

        if expense > 0:
            percent = (expense / income) * 100 if income else 0
            messagebox.showinfo("Hisobot", f"Siz daromadingizning {percent:.1f}% qismini sarfladingiz.")


# ==================== TARIX SAHIFASI ====================
class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="📜 Moliya tarixi", font=("Segoe UI", 24, "bold")).pack(pady=30)
        self.text_box = ctk.CTkTextbox(self, width=850, height=400, corner_radius=15, font=("Consolas", 12))
        self.text_box.pack(pady=10)
        ctk.CTkButton(self, text="Yangilash", command=self.load_history).pack(pady=10)
        ctk.CTkButton(self, text="⬅ Orqaga", command=lambda: controller.show_frame(MainMenu)).pack(pady=10)

    def load_history(self):
        self.text_box.delete("1.0", "end")
        data = load_data()
        if not data:
            self.text_box.insert("end", "Ma'lumotlar topilmadi.")
            return
        for i in data:
            t = "Daromad" if i["type"] == "income" else "Xarajat"
            self.text_box.insert("end", f"{i['date']} | {t:<8} | {i['category']:<10} | {i['amount']:>10,.0f} so‘m | {i['note']}\n")


# ==================== SOZLAMALAR SAHIFASI ====================
class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="⚙️ Sozlamalar", font=("Segoe UI", 24, "bold")).pack(pady=30)
        ctk.CTkButton(self, text="🎨 Tema o‘zgartirish", command=self.change_theme, width=250).pack(pady=10)
        ctk.CTkButton(self, text="🌈 Rang tanlash", command=self.pick_color, width=250).pack(pady=10)
        ctk.CTkButton(self, text="⬅ Orqaga", command=lambda: controller.show_frame(MainMenu), width=200).pack(pady=30)

    def change_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        messagebox.showinfo("Tema", f"Tema {new_mode.upper()} ga o‘zgartirildi!")

    def pick_color(self):
        color = colorchooser.askcolor(title="Rang tanlang")[1]
        if color:
            self.configure(fg_color=color)


# ==================== ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()
