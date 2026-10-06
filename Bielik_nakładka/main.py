import tkinter as tk
import requests
import threading
import os
from pathlib import Path
from datetime import datetime
import time




def wyslij():
    tekst = pole_wiadomosci.get()

    if not tekst:
        return

    rozmowa.config(state="normal")

    rozmowa.insert(
        tk.END,
        "\nTy: " + tekst + "\n\n"
    )

    rozmowa.config(state="disabled")

    pole_wiadomosci.delete(0, tk.END)

    threading.Thread(
        target=zapytaj_bielika,
        args=(tekst,),
        daemon=True
    ).start()

def zapytaj_bielika(tekst):

    model = "bielik-michal"

    godzina = datetime.now().strftime("%H:%M:%S")

    start = time.perf_counter()

    odpowiedz = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": tekst,
            "stream": False
        }
    )

    koniec = time.perf_counter()

    czas = koniec - start

    print("STATUS:", odpowiedz.status_code)
    print("ODPOWIEDŹ:", odpowiedz.text)

    dane = odpowiedz.json()

    if "error" in dane:
        okno.after(
            0,
            lambda: pokaz_odpowiedz(
                "BŁĄD: " + dane["error"]
            )
        )
        return

    tekst_bielika = dane.get("response", "")

    okno.after(
        0,
        lambda: pokaz_odpowiedz(
            tekst_bielika,
            godzina,
            czas,
            model
        )
    )

def pokaz_odpowiedz(tekst, godzina, czas, model):

    rozmowa.config(state="normal")

    rozmowa.insert(
        tk.END,
        "Bielik: " + tekst + "\n"
    )

    rozmowa.config(state="disabled")

    Godzina.config(text="Godzina: " + godzina)
    Czas.config(text=f"Czas: {czas:.2f} s")
    Model.config(text="Model: " + model)

def nowa_rozmowa():
    rozmowa.delete("1.0", tk.END)

# ===== OKON OPCJI PRAMU =====

def opcje_programu():
    okno_opcji = tk.Toplevel(okno)
    okno_opcji.title("Opcje programu")
    okno_opcji.geometry("400x300")
    okno_opcji.configure(bg="black")

    napis = tk.Label(
        okno_opcji,
        text="Tutaj będą opcje programu",
        bg="black",
        fg="white"
    )

    napis.pack()

# ===== GŁÓWNY EKRAN =====

okno = tk.Tk()

okno.title("Bielik")
okno.geometry("800x600")
okno.configure(bg="black")


# ===== MENU GÓRA =====

menu = tk.Menu(
    okno,
    bg="black",
    fg="white"
)

game_menu = tk.Menu(
    menu,
    tearoff=0
)

game_menu.add_command(
    label="Zapisz konwersacje",
    command=nowa_rozmowa
)

game_menu.add_command(
    label="Zakończ sesję",
    command=nowa_rozmowa
)

game_menu.add_command(
    label="Wyjdź",
    command=okno.destroy
)

menu.add_cascade(
    label="Konwersacja",
    menu=game_menu
)
# ----------
opcje_menu = tk.Menu(
    menu,
    tearoff=0
)

menu.add_cascade(
    label="Opcje" ,
    menu=opcje_menu
)

opcje_menu.add_command(
    label = "Opcje programu",
    command=opcje_programu
)

opcje_menu.add_command(
    label = "Opcje wyglądu"
)

okno.config(menu=menu)


# ----------


menu.add_command(
    label="Pomoc"
)

# ==== GŁÓWNY PANEL ==== 

glowny_panel = tk.Frame(
    okno,
    bg="black"
)

glowny_panel.pack(
    fill="both",
    expand=True
)


# ==== UKŁAD 20% / 60% / 20% ==== 

glowny_panel.grid_columnconfigure(
    0,
    weight=2,
    uniform="kolumny",
    minsize=0
)

glowny_panel.grid_columnconfigure(
    1,
    weight=6,
    uniform="kolumny",
    minsize=0
)

glowny_panel.grid_columnconfigure(
    2,
    weight=2,
    uniform="kolumny",
    minsize=0
)

glowny_panel.grid_rowconfigure(
    0,
    weight=1,
    uniform="kolumny",
    minsize=0
)


# ==== LEWE MENU - 20% ==== 

lewe_menu = tk.Frame(
    glowny_panel,
    bg="black"
)

lewe_menu.grid(
    row=0,
    column=0,
    sticky="nsew"
)

lista = tk.Listbox(
    lewe_menu,
    bg="black",
    fg="white",
    selectbackground="gray",
    selectforeground="white"
)

lista.pack(
    fill="both",
    expand=True
)

folder = Path("Zapis_konwersacji")

for plik in folder.iterdir():
    if plik.suffix == ".txt":
        lista.insert(tk.END, plik.stem)

# ==== PANEL ROZMOWY - 60% ==== 

panel_rozmowy = tk.Frame(
    glowny_panel,
    bg="black"
)

panel_rozmowy.grid(
    row=0,
    column=1,
    sticky="nsew"
)



# ==== PRAWE MENU - 20% ==== 

prawe_menu = tk.Frame(
    glowny_panel,
    bg="black"
)

prawe_menu.grid(
    row=0,
    column=2,
    sticky="nsew"
)

Godzina = tk.Label(prawe_menu,text="Godzina :",bg="black",fg="white")
Godzina.pack()
Czas = tk.Label(prawe_menu,text="Czas :",bg="black",fg="white")
Czas.pack()
Model = tk.Label(prawe_menu,text="Model :",bg="black",fg="white")
Model.pack()
czy_online = tk.Label(prawe_menu,text="Z Internetem :",bg="black",fg="white")
czy_online.pack()
czy_szuka_z_bazy = tk.Label(prawe_menu,text="Z bzay:",bg="black",fg="white")
czy_szuka_z_bazy.pack()

czy_z_pamięci = tk.BooleanVar(value=True)
czy_szuka_online = tk.BooleanVar(value=True)
czy_szuka_z_bazy = tk.BooleanVar(value=True)

czy_z_pamięci = tk.Checkbutton(prawe_menu,text="czy z pamięci ogólnej",variable=czy_szuka_online,bg="black",fg="white",selectcolor="black"
)
czy_z_pamięci.pack(side="bottom")

czy_online = tk.Checkbutton(prawe_menu,text="Wyszukiwanie Online",variable=czy_szuka_online,bg="black",fg="white",selectcolor="black"
)
czy_online.pack(side="bottom")

z_bazy = tk.Checkbutton(prawe_menu,text="Korzystanie z bazy",variable=czy_szuka_z_bazy,bg="black",fg="white",selectcolor="black"
)
z_bazy.pack(side="bottom")


# ==== POLE ROZMOWY ==== 

rozmowa = tk.Text(
    panel_rozmowy,
    bg="black",
    fg="white",
    state="disabled",
    insertbackground="white"
)


rozmowa.pack(
    fill="both",
    expand=True
)


# ==== DOLNY PANEL ==== 

dolny_panel = tk.Frame(
    okno,
    bg="black"
)

dolny_panel.pack(
    fill="x"
)


# ==== POLE WIADOMOŚCI ==== 

pole_wiadomosci = tk.Entry(
    dolny_panel,
    bg="black",
    fg="white",
    insertbackground="white"
)

pole_wiadomosci.pack(
    side="left",
    fill="x",
    expand=True
)


# ==== PRZYCISK WYŚLIJ ==== 

przycisk = tk.Button(
    dolny_panel,
    text="Wyślij",
    command=wyslij
)

przycisk.pack(
    side="right"
)


# ==== START PROGRAMU ====
okno.minsize(600, 400)
okno.mainloop()