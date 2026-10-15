import tkinter as tk
import requests
import threading
import os
from pathlib import Path
from datetime import datetime
import time
import konfiguracje



aktualna_rozmowa = None

def wyslij():

    def wyslij():
        global aktualna_rozmowa

        if aktualna_rozmowa is None:
            print("Nie wybrano rozmowy")
            return

    tekst = pole_wiadomosci.get()

    if not tekst:
        return

    rozmowa.config(state="normal")

    rozmowa.insert(
        tk.END,
        "\nTy: " + tekst + "\n\n"
    )

    with open(aktualna_rozmowa, "a", encoding="utf-8") as plik:
        plik.write("\nTy: " + tekst + "\n\n")

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
                "BŁĄD: " + dane["error"],
                godzina,
                czas,
                model,
                czy_z_pamięci_checkbox,
                czy_szuka_z_bazy,
                czy_szuka_online
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
            model,
            czy_z_pamięci_checkbox,
            czy_szuka_z_bazy,
            czy_szuka_online
        )
    )


def wczytaj_rozmowe(nazwa):

    plik = folder / f"{nazwa}.txt"

    with open(plik, "r", encoding="utf-8") as f:
        zawartosc = f.read()

    rozmowa.config(state="normal")

    rozmowa.delete("1.0", tk.END)
    rozmowa.insert(tk.END, zawartosc)

    rozmowa.config(state="disabled")

    print(zawartosc)



def pokaz_rozmowy():
    for plik in folder.iterdir():
        if plik.suffix == ".txt":

            przycisk = tk.Button(
                lewe_menu,
                text=plik.stem,
                command=lambda nazwa=plik.stem: wczytaj_rozmowe(nazwa)
            )

            przycisk.pack(fill="x")

def pokaz_odpowiedz(
    tekst,
    godzina,
    czas,
    model,
    czy_z_pamięci,
    z_bazy,
    czy_online
):

    rozmowa.config(state="normal")

    if dodatkowe_info_w_konwersacji.get():
        rozmowa.insert(
            tk.END,
            f"godzina: {godzina} | "
            f"czas: {czas:.2f} | "
            f"model: {model} | "
            f"pamięć: {czy_z_pamięci.get()} | "
            f"baza: {z_bazy.get()} | "
            f"online: {czy_online.get()}\n"
        )

    rozmowa.insert(
        tk.END,
        "\nBielik: " + tekst + "\n"
    )

    with open(aktualna_rozmowa, "a", encoding="utf-8") as plik:
        plik.write("\nBielik: " + tekst + "\n")

    rozmowa.config(state="disabled")

    Godzina.config(text="Godzina: " + godzina)
    Czas.config(text=f"Czas: {czas:.2f} s")
    Model.config(text="Model: " + model)



    if czy_szuka_online.get():
        try:
            requests.get(
                "https://www." + konfiguracje.wyszukiwarka + ".com",
                timeout=5
            )
            status_online.config(text="wyszukiwanie: online")
        except:
            status_online.config(text="wyszukiwanie: offline")
    else:
        status_online.config(text="wyszukiwanie: offline")

    if czy_z_pamięci == True:
        status_online.config(text="wyszukiwanie: offline")
    else:
        status_online.config(text="wyszukiwanie: offline")


# ===== OKNO OPCJI PROGRAMU =====

def opcje_programu():

    global dodatkowe_info_w_konwersacji

    okno_opcji = tk.Toplevel(okno)
    okno_opcji.title("Opcje programu")
    okno_opcji.geometry("400x300")
    okno_opcji.configure(bg=konfiguracje.kolor_tla)

    napis = tk.Label(
        okno_opcji,
        text="wybor preferowanej przeglądarki",
        bg=konfiguracje.kolor_tla,
        fg=konfiguracje.kolor_liter_zwykle
    )

    napis.pack()

    wybor = tk.StringVar(value=konfiguracje.wyszukiwarka)
    ekran_powitalny = tk.BooleanVar(value=True)

    wybor_wyszukiwarki = tk.OptionMenu(
        okno_opcji,
        wybor,
        "google",
        "Bing",
        "Brave",
        "DuckDuckGo",
        "SearXNG"
    )

    wybor_wyszukiwarki.pack()

    dodatkowe_info_pytanie = tk.Checkbutton(
        okno_opcji,
        text="zapis dodatkowych informacji przy rozmowie",
        variable=dodatkowe_info_w_konwersacji,
        bg=konfiguracje.kolor_tla,
        fg=konfiguracje.kolor_liter_zwykle,
        selectcolor="black"
    )

    dodatkowe_info_pytanie.pack()

    ekran_powitalny_pytanie = tk.Checkbutton(
        okno_opcji,
        text="ekran powitalny",
        variable=ekran_powitalny,
        bg=konfiguracje.kolor_tla,
        fg=konfiguracje.kolor_liter_zwykle,
        selectcolor="black"
    )

    ekran_powitalny_pytanie.pack()

    def zapisz_ustawienia_programu():

        nowa_wyszukiwarka = wybor.get()
        nowa_dodatkowe_info_w_konwersacji = dodatkowe_info_w_konwersacji.get()
        nowy_ekran_powitalny = ekran_powitalny.get()

        konfiguracje.wyszukiwarka = wybor.get()

        sciezka = Path(__file__).parent / "konfiguracje.py"

        with open(sciezka, "r", encoding="utf-8") as plik:
            linie = plik.readlines()

        for i, linia in enumerate(linie):
            if linia.startswith("wyszukiwarka ="):
                linie[i] = f'wyszukiwarka = "{nowa_wyszukiwarka}"\n'
                break

        for i, linia in enumerate(linie):
            if linia.startswith("wypisywanie_dodatkowych_informacji ="):
                linie[i] = f'wypisywanie_dodatkowych_informacji = {nowa_dodatkowe_info_w_konwersacji}\n'
                break

        for i, linia in enumerate(linie):
            if linia.startswith("Ekran_powitalny ="):
                linie[i] = f'Ekran_powitalny = {nowy_ekran_powitalny}\n'
                break

        with open(sciezka, "w", encoding="utf-8") as plik:
            plik.writelines(linie)

        okno_opcji.destroy()

    tk.Button(
        okno_opcji,
        text="Zapisz ustawienia",
        command=zapisz_ustawienia_programu
    ).pack()


# ===== GŁÓWNY EKRAN =====

okno = tk.Tk()

dodatkowe_info_w_konwersacji = tk.BooleanVar(value=True)

okno.title("Bielik")
okno.geometry("800x600")
okno.configure(bg=konfiguracje.kolor_tla)


# ===== MENU GÓRA =====

menu = tk.Menu(
    okno,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle
)


# ===== KONFIGURACJE KONWERSACJI =====

# --- operowanie na nowym txt
def nowa_rozmowa():

    okno_opcji = tk.Toplevel(okno)
    okno_opcji.title("Nowa konwersacja")
    okno_opcji.geometry("200x150")
    okno_opcji.configure(bg=konfiguracje.kolor_tla)

    napis = tk.Label(
        okno_opcji,
        text="Jak nazwać konwersacje?",
        bg=konfiguracje.kolor_tla,
        fg=konfiguracje.kolor_liter_zwykle
    )

    napis.pack()

    pole = tk.Entry(okno_opcji)
    pole.pack()

    folder = Path(__file__).parent / "Zapis_konwersacji"

    def zapisz_nowy_plik():

        global aktualna_rozmowa

        wartosc = pole.get()

        for plik in folder.iterdir():
            if plik.stem == wartosc:
                print("taki plik już istnieje:", plik)
                return

        sciezka = folder / f"{wartosc}.txt"
        sciezka.touch()

        aktualna_rozmowa = sciezka

        okno_opcji.destroy()

    tk.Button(
        okno_opcji,
        text="Zapisz nazwę",
        command=zapisz_nowy_plik
    ).pack()

# --- 

game_menu = tk.Menu(
    menu,
    tearoff=0
)

game_menu.add_command(
    label="Nowa konwersacja",
    command=nowa_rozmowa
)

game_menu.add_command(
    label="Nowa konwersacja bez zapisu",
    command=nowa_rozmowa
)

game_menu.add_command(
    label="Zapisz i wyjdź",
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
    label="Opcje",
    menu=opcje_menu
)

opcje_menu.add_command(
    label="Opcje programu",
    command=opcje_programu
)

opcje_menu.add_command(
    label="Opcje wyglądu"
)

okno.config(menu=menu)


# ----------

menu.add_command(
    label="Pomoc"
)


# ==== GŁÓWNY PANEL ====

glowny_panel = tk.Frame(
    okno,
    bg=konfiguracje.kolor_tla
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
    bg=konfiguracje.kolor_tla
)

lewe_menu.grid(
    row=0,
    column=0,
    sticky="nsew"
)

lista = tk.Listbox(
    lewe_menu,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle,
    selectbackground="gray",
    selectforeground="white"
)



folder = Path(__file__).parent / "Zapis_konwersacji"


def kliknieta_rozmowa(nazwa):
    global aktualna_rozmowa

    aktualna_rozmowa = folder / f"{nazwa}.txt"

    wczytaj_rozmowe(nazwa)


    print("Aktualna rozmowa:", aktualna_rozmowa)


for plik in folder.iterdir():

    if plik.suffix == ".txt":

        przycisk = tk.Button(
            lewe_menu,
            text=plik.stem,
            command=lambda nazwa=plik.stem: kliknieta_rozmowa(nazwa)
        )

        przycisk.pack(fill="x")




folder = Path(__file__).parent / "Zapis_konwersacji"

for plik in folder.iterdir():
    if plik.suffix == ".txt":
        lista.insert(tk.END, plik.stem)


# ==== PANEL ROZMOWY - 60% ====

panel_rozmowy = tk.Frame(
    glowny_panel,
    bg=konfiguracje.kolor_tla
)

panel_rozmowy.grid(
    row=0,
    column=1,
    sticky="nsew"
)


# ==== PRAWE MENU - 20% ====

prawe_menu = tk.Frame(
    glowny_panel,
    bg=konfiguracje.kolor_tla
)

prawe_menu.grid(
    row=0,
    column=2,
    sticky="nsew"
)


Godzina = tk.Label(
    prawe_menu,
    text="Godzina :",
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle
)
Godzina.pack()

Czas = tk.Label(
    prawe_menu,
    text="Czas :",
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle
)
Czas.pack()

Model = tk.Label(
    prawe_menu,
    text="Model :",
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle
)
Model.pack()

status_baza = tk.Label(
    prawe_menu,
    text="Z bazy:",
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle
)
status_baza.pack()

status_online = tk.Label(
    prawe_menu,
    text="wyszukiwanie: offline",
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle
)
status_online.pack()


czy_z_pamięci_checkbox = tk.BooleanVar(value=True)
czy_szuka_online = tk.BooleanVar(value=True)
czy_szuka_z_bazy = tk.BooleanVar(value=True)
czy_podaje_szybkie_odpowiedzi = tk.BooleanVar(value=False)


czy_z_pamięci = tk.Checkbutton(
    prawe_menu,
    text="czy z pamięci ogólnej",
    variable=czy_z_pamięci_checkbox,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle,
    selectcolor="black"
)

czy_z_pamięci.pack(side="bottom")


czy_online = tk.Checkbutton(
    prawe_menu,
    text="Wyszukiwanie Online",
    variable=czy_szuka_online,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle,
    selectcolor="black"
)

czy_online.pack(side="bottom")


z_bazy = tk.Checkbutton(
    prawe_menu,
    text="Korzystanie z bazy",
    variable=czy_szuka_z_bazy,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle,
    selectcolor="black"
)

z_bazy.pack(side="bottom")

Szybkie_odpowiedzi = tk.Checkbutton(
    prawe_menu,
    text="Szybkie_odpowiedzi",
    variable=czy_podaje_szybkie_odpowiedzi,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle,
    selectcolor="black"
)

Szybkie_odpowiedzi.pack(side="bottom")


# ==== POLE ROZMOWY ====

rozmowa = tk.Text(
    panel_rozmowy,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle,
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
    bg=konfiguracje.kolor_tla
)

dolny_panel.pack(
    fill="x"
)


# ==== POLE WIADOMOŚCI ====

pole_wiadomosci = tk.Entry(
    dolny_panel,
    bg=konfiguracje.kolor_tla,
    fg=konfiguracje.kolor_liter_zwykle,
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