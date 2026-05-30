"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Tomáš Aubrecht
email: tomik.aubrecht@gmail.com
discord: Tomik A.


"""

import sys
import csv
import requests
from bs4 import BeautifulSoup

def zkontroluj_argumenty():
    """Zkontroluje, zda uživatel zadal správný počet argumentů a platný odkaz."""
    if len(sys.argv) != 3:
        print("CHYBA: Špatný počet argumentů.")
        print("Spusťte program ve formátu: python projekt_3.py <odkaz_na_uzemni_celek> <jmeno_souboru.csv>")
        sys.exit(1)
    
    url = sys.argv[1]
    if not url.startswith("https://volby.cz/pls/ps2017nss/"):
        print("CHYBA: Zadaný odkaz není platný odkaz pro volby 2017 (musí začínat 'https://volby.cz/pls/ps2017nss/').")
        sys.exit(1)
        
    return sys.argv[1], sys.argv[2]

def ziskej_soup(url):
    """Stáhne HTML z URL a vrátí BeautifulSoup objekt."""
    try:
        odpoved = requests.get(url)
        odpoved.raise_for_status()
        # Využití response.content zabrání problémům s českou diakritikou
        return BeautifulSoup(odpoved.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"CHYBA: Nepodařilo se připojit k zadané URL: {e}")
        sys.exit(1)

def ziskej_odkazy_obci(hlavni_url):
    """Získá kódy, názvy a URL odkazy jednotlivých obcí z hlavního odkazu."""
    soup = ziskej_soup(hlavni_url)
    zakladni_url = "https://volby.cz/pls/ps2017nss/"
    obce = []

    # Hledání buněk tabulky s třídou 'cislo', které obsahují odkazy na obce
    bunky_s_kody = soup.find_all("td", class_="cislo")
    
    for bunka in bunky_s_kody:
        odkaz_element = bunka.find("a")
        if odkaz_element:
            kod_obce = odkaz_element.text
            odkaz_obce = zakladni_url + odkaz_element["href"]
            # Název obce je v následující buňce
            nazev_obce = bunka.find_next_sibling("td").text
            
            obce.append({
                "kod": kod_obce,
                "nazev": nazev_obce,
                "odkaz": odkaz_obce
            })
            
    return obce

def ziskej_data_z_obce(url_obce):
    """Ze stránky konkrétní obce vytáhne statistiky a hlasy pro strany."""
    soup = ziskej_soup(url_obce)
    
    # Základní statistiky: voliči, obálky, platné hlasy
    volici = soup.find("td", headers="sa2").text.replace('\xa0', '')
    obalky = soup.find("td", headers="sa3").text.replace('\xa0', '')
    platne_hlasy = soup.find("td", headers="sa6").text.replace('\xa0', '')
    
    data_obce = {
        "Voliči v seznamu": volici,
        "Vydané obálky": obalky,
        "Platné hlasy": platne_hlasy
    }
    
    # Hlasy pro politické strany
    # Strany jsou uloženy v tabulkách, kde má název strany typicky třídu 'overflow_name'
    nazvy_stran = soup.find_all("td", class_="overflow_name")
    hlasy_stran = soup.find_all("td", headers=["t1sa2 t1sb3", "t2sa2 t2sb3"])
    
    for strana, hlasy in zip(nazvy_stran, hlasy_stran):
        data_obce[strana.text] = hlasy.text.replace('\xa0', '')
        
    return data_obce

def main():
    # 1. Kontrola vstupů
    url, jmeno_souboru = zkontroluj_argumenty()
    
    print(f"STAHUJI DATA Z VYBRANÉHO ODKAZU: {url}")
    
    # 2. Získání seznamu obcí
    obce = ziskej_odkazy_obci(url)
    if not obce:
        print("CHYBA: Na zadané adrese nebyly nalezeny žádné obce. Zkontrolujte odkaz.")
        sys.exit(1)
        
    # 3. Stažení dat z první obce pro vytvoření hlavičky CSV
    prvni_obec_data = ziskej_data_z_obce(obce[0]["odkaz"])
    strany = list(prvni_obec_data.keys())[3:] # Názvy stran (od 4. klíče dál)
    
    hlavicka = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"] + strany
    
    # 4. Sběr dat a zápis do CSV
    print(f"UKLÁDÁM DATA DO SOUBORU: {jmeno_souboru}")
    
    with open(jmeno_souboru, mode="w", newline="", encoding="utf-8-sig") as csv_soubor:
        writer = csv.writer(csv_soubor, delimiter=";")
        writer.writerow(hlavicka)
        
        for obec in obce:
            # print(f"Zpracovávám: {obec['nazev']}...") # Volitelné: odkomentuj pro sledování průběhu
            data = ziskej_data_z_obce(obec["odkaz"])
            
            radek = [
                obec["kod"],
                obec["nazev"],
                data["Voliči v seznamu"],
                data["Vydané obálky"],
                data["Platné hlasy"]
            ]
            
            # Přidání hlasů pro jednotlivé strany
            for strana in strany:
                radek.append(data.get(strana, "0"))
                
            writer.writerow(radek)
            
    print("DOKONČENO: Data byla úspěšně uložena.")

if __name__ == "__main__":
    main()