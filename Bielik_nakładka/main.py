import tkinter as tk
import requests
import threading
from pathlib import Path
from datetime import datetime, timedelta
import time
import konfiguracje
import csv
import json

# ==== wartości ogólne
aktualna_rozmowa = None
ladowanie = False
animacja_index = 0
animacje = {
    "animacja_1": ["|", "/", "-", "\\", "|", "/", "-", "\\"],
    "animacja_2": ["˂", "˄", "˃", "˅"],
    "animacja_3": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    "animacja_4": ["⠁", "⠂", "⠄", "⠂"],
    "animacja_5": ["⠈", "⠐", "⠠", "⢀", "⠄", "⠂"],
    "animacja_6": [". ", ".. ", "..."],
    "animacja_7": ["●○○", "○●○", "○○●"],
    "animacja_8": ["◢", "◣", "◤", "◥"]
}
# ==== definicje

def uruchom_animacje():
    if ladowanie == True :
        global animacja_index

        if not ladowanie:
            return

        rozmowa.config(state="normal")
        rozmowa.delete("end-2c", "end-1c")

        rozmowa.insert(
            tk.END,
            animacje[konfiguracje.wybor_animacji][animacja_index]
        )

        rozmowa.see(tk.END)
        rozmowa.config(state="disabled")

        animacja_index += 1

        if animacja_index >= len(animacje[konfiguracje.wybor_animacji]):
            animacja_index = 0

        okno.after(100, uruchom_animacje)


def wyslij():

    global aktualna_rozmowa, ladowanie

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

    ladowanie = True

    uruchom_animacje()

    with open(aktualna_rozmowa, "a", encoding="utf-8") as plik:
        plik.write("\nTy: " + tekst + "\n\n")
        rozmowa.see(tk.END)

    rozmowa.config(state="disabled")

    pole_wiadomosci.delete(0, tk.END)

    threading.Thread(
        target=zapytaj_bielika,
        args=(tekst,),
        daemon=True
    ).start()

def zapytaj_bielika(tekst):


    def rozpocznij_odpowiedz():
        
        global ladowanie

        ladowanie = False

        rozmowa.config(state="normal")
        rozmowa.delete("end-2c", "end-1c")
        rozmowa.insert(tk.END, "\nBielik: ")
        rozmowa.config(state="disabled")

    def pokaz_fragment(fragment):
        rozmowa.config(state="normal")
        rozmowa.insert(tk.END, fragment)
        rozmowa.see(tk.END)
        rozmowa.config(state="disabled")
    
    model = "bielik-michal"

    godzina = datetime.now().strftime("%H:%M:%S")

    start = time.perf_counter()

    fragmenty = []

    if czy_podaje_szybkie_odpowiedzi.get():
        limit_tokenow = 150
        temperatura = 0.5
    else:
        limit_tokenow = 2048
        temperatura = 0.7
    
    try:
        odpowiedz = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": tekst,
                "stream": True,
                "options": {
                    "num_predict": limit_tokenow,
                    "temperature": temperatura
                }
            },
            stream=True
        )

        odpowiedz.raise_for_status()

        okno.after(0, rozpocznij_odpowiedz)

        for linia in odpowiedz.iter_lines():
            if not linia:
                continue

            dane = json.loads(linia)

            if "error" in dane:
                raise RuntimeError(dane["error"])

            fragment = dane.get("response", "")

            fragmenty.append(fragment)

            okno.after(
                0,
                lambda fragment=fragment: pokaz_fragment(fragment)
            )

        tekst_bielika = "".join(fragmenty)

    except Exception as e:
        tekst_bielika = f"BŁĄD: {e}"

    czas = time.perf_counter() - start





    
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
            "\n" +
            f"godzina: {godzina} | "
            f"czas: {czas:.2f} | "
            f"model: {model} | "
            f"pamięć: {czy_z_pamięci.get()} | "
            f"baza: {z_bazy.get()} | "
            f"online: {czy_online.get()}\n"
        )
        rozmowa.see(tk.END)


    #rozmowa.insert(tk.END,"\nBielik: " + tekst + "\n\n")
    rozmowa.delete("end-2c", "end-1c")

    with open(aktualna_rozmowa, "a", encoding="utf-8") as plik:
         plik.write("\nBielik: " + tekst + "\n")

    rozmowa.config(state="disabled")

    Godzina.config(text="Godzina: " + godzina)
    Czas.config(text=f"Czas: {czas:.2f} s")
    Model.config(text="Model: " + model)



    czy_online.config (text= "")


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

    wybor_animacji = tk.StringVar(value=konfiguracje.wybor_animacji)
    wybor_przeglądarki = tk.StringVar(value=konfiguracje.wyszukiwarka)
    ekran_powitalny = tk.BooleanVar(value=True)

    wybor_wyszukiwarki = tk.OptionMenu(
        okno_opcji,
        wybor_przeglądarki,
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

    wybor_animacji_ladowania_napis = tk.Label(
        okno_opcji,
        text="wybor animacji dla ladowania",
        bg=konfiguracje.kolor_tla,
        fg=konfiguracje.kolor_liter_zwykle
    )

    wybor_animacji_ladowania_napis.pack()


    animacje = {
        "animacja_1": ["|", "/", "-", "\\", "|", "/", "-", "\\"],
        "animacja_2": ["˂", "˄", "˃", "˅"],
        "animacja_3": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "animacja_4": ["⠁", "⠂", "⠄", "⠂"],
        "animacja_5": ["⠈", "⠐", "⠠", "⢀", "⠄", "⠂"],
        "animacja_6": [". ", ".. ", "..."],
        "animacja_7": ["●○○", "○●○", "○○●"],
        "animacja_8": ["◢", "◣", "◤", "◥"]
    }

    wybor_animacji_ladowania = tk.OptionMenu(
        okno_opcji,
        wybor_animacji,
        *animacje.keys()
    )

    wybor_animacji_ladowania.pack()

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

        nowa_wyszukiwarka = wybor_przeglądarki.get()
        nowa_animacja = wybor_animacji.get()

        nowa_dodatkowe_info_w_konwersacji = dodatkowe_info_w_konwersacji.get()
        nowy_ekran_powitalny = ekran_powitalny.get()

        konfiguracje.wyszukiwarka = nowa_wyszukiwarka
        konfiguracje.wybor_animacji = nowa_animacja

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

        for i, linia in enumerate(linie):
            if linia.startswith("wybor_animacji ="):
                linie[i] = f'wybor_animacji = "{nowa_animacja}"\n'
                break
                
        with open(sciezka, "w", encoding="utf-8") as plik:
            plik.writelines(linie)

        okno_opcji.destroy()

    tk.Button(
        okno_opcji,
        text="Zapisz ustawienia",
        command=zapisz_ustawienia_programu
    ).pack()

def baza_danych():
    
    global dodatkowe_info_w_konwersacji

    okno_opcji = tk.Toplevel(okno)
    okno_opcji.title("Opcje programu")
    okno_opcji.geometry("400x300")
    okno_opcji.configure(bg=konfiguracje.kolor_tla)


# ==== wracaj do roboty !!!!



    napis = tk.Label(
        okno_opcji,
        text="wybor preferowanej przeglądarki",
        bg=konfiguracje.kolor_tla,
        fg=konfiguracje.kolor_liter_zwykle
    )

    napis.pack()

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
    label="Baza danych"
)

okno.config(menu=menu)


# ----------

def okno_pomocy ():
    
    okno_pomocy = tk.Toplevel(okno)
    okno_pomocy.title("Opcje programu")
    okno_pomocy.geometry("400x300")
    okno_pomocy.configure(bg=konfiguracje.kolor_tla)

    napis = tk.Label(
        okno_pomocy,
        text="Tu się potem walnie instrukcję",
        bg=konfiguracje.kolor_tla,
        fg=konfiguracje.kolor_liter_zwykle
    )

    napis.pack(anchor="nw")

menu.add_command(
    label="Pomoc",
    command=okno_pomocy

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
    text="wyszukiwanie:",
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

menu_rozmowy = tk.Menu(rozmowa, tearoff=0)

menu_rozmowy.add_command(
    label="Kopiuj",
    command=lambda: rozmowa.event_generate("<<Copy>>")
)

menu_rozmowy.add_command(
    label="Zaznacz wszystko",
    command=lambda: rozmowa.tag_add("sel", "1.0", "end-1c")
)

menu_rozmowy.add_command(
    label="Wyjaśnij dokładniej",
)

rozmowa.pack(
    fill="both",
    expand=True
)

def wyjasnij_dokladniej():
    print("Wybrano: Wyjaśnij dokładniej")

def pokaz_menu_rozmowy(event):
    menu_rozmowy.tk_popup(event.x_root, event.y_root)

rozmowa.bind("<Button-3>", pokaz_menu_rozmowy)

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


menu_wiadomości = tk.Menu(rozmowa, tearoff=0)

menu_wiadomości.add_command(
    label="Kopiuj",
    command=lambda: pole_wiadomosci.event_generate("<<Copy>>")
)

menu_wiadomości.add_command(
    label="Wytnij",
    command=lambda: pole_wiadomosci.event_generate("<<Cut>>")
)

menu_wiadomości.add_command(
    label="Wklej",
    command=lambda: pole_wiadomosci.event_generate("<<Paste>>")
)

menu_wiadomości.add_command(
    label="Zaznacz wszystko",
    command=lambda: pole_wiadomosci.select_range(0, tk.END)
)

pole_wiadomosci.pack(
    side="left",
    fill="x",
    expand=True
)

def pokaz_menu_wiadomosci(event):
    menu_wiadomości.tk_popup(event.x_root, event.y_root)
    menu_wiadomości.grab_release()

pole_wiadomosci.bind("<Button-3>", pokaz_menu_wiadomosci)

# ==== PRZYCISK WYŚLIJ ====

przycisk = tk.Button(
    dolny_panel,
    text="Wyślij",
    command=wyslij

)

okno.bind("<Return>", lambda event: wyslij())

pole_wiadomosci.bind("<Return>", lambda event: wyslij())

przycisk.pack(
    side="right"
)


# ==== START PROGRAMU ====

ile_dni_wyświetlić_w_koaendarzu = range(5)
if konfiguracje.Ekran_powitalny == True:

    data = datetime.now()

    rozmowa.config(state="normal")
    rozmowa.insert(tk.END, "Witaj użytkowniku!\nKalendarz:\n")

    for n in ile_dni_wyświetlić_w_koaendarzu :
        rozmowa.insert(tk.END, "\n" + data.strftime("%d:%m:%Y"))

        with open("kalendarz.csv" , "r" , encoding="utf-8-sig") as kalendarz:
            dane = csv.DictReader(kalendarz)

            for wiersz in dane:
                if wiersz["month"] ==  data.strftime("%m") and wiersz["day"] == data.strftime("%d"):
                    rozmowa.insert(tk.END,"\n" +(wiersz["Nazwa okazji / Święto"]))
                    rozmowa.insert(tk.END,"\n" +(wiersz["Imieniny"]) + "\n")


        data = data + timedelta(days=1)

    rozmowa.insert(tk.END, "\nwybierz konwersacje i możemy zaczynać : )\n")

    rozmowa.config(state="disabled")


okno.minsize(600, 400)
okno.mainloop()