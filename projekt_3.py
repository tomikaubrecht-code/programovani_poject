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
    try:
        odpoved = requests.get(url)
        odpoved.raise_for_status()
        return BeautifulSoup(odpoved.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"CHYBA: Nepodařilo se připojit k zadané URL: {e}")
        sys.exit(1)

def ziskej_odkazy_obci(hlavni_url):
    soup = ziskej_soup(hlavni_url)
    zakladni_url = "https://volby.cz/pls/ps2017nss/"
    obce = []

    bunky_s_kody = soup.find_all("td", class_="cislo")
    
    for bunka in bunky_s_kody:
        odkaz_element = bunka.find("a")
        if odkaz_element:
            kod_obce = odkaz_element.text
            odkaz_obce = zakladni_url + odkaz_element["href"]
            nazev_obce = bunka.find_next_sibling("td").text
            
            obce.append({
                "kod": kod_obce,
                "nazev": nazev_obce,
                "odkaz": odkaz_obce
            })
            
    return obce

def ziskej_data_z_obce(url_obce):
    soup = ziskej_soup(url_obce)
    
    volici = soup.find("td", headers="sa2").text.replace('\xa0', '')
    obalky = soup.find("td", headers="sa3").text.replace('\xa0', '')
    platne_hlasy = soup.find("td", headers="sa6").text.replace('\xa0', '')
    
    data_obce = {
        "Voliči v seznamu": volici,
        "Vydané obálky": obalky,
        "Platné hlasy": platne_hlasy
    }
    
    nazvy_stran = soup.find_all("td", class_="overflow_name")
    hlasy_stran = soup.find_all("td", headers=["t1sa2 t1sb3", "t2sa2 t2sb3"])
    
    for strana, hlasy in zip(nazvy_stran, hlasy_stran):
        data_obce[strana.text] = hlasy.text.replace('\xa0', '')
        
    return data_obce

def main():
    url, jmeno_souboru = zkontroluj_argumenty()
    
    print(f"STAHUJI DATA Z VYBRANÉHO ODKAZU: {url}")
    
    obce = ziskej_odkazy_obci(url)
    if not obce:
        print("CHYBA: Na zadané adrese nebyly nalezeny žádné obce. Zkontrolujte odkaz.")
        sys.exit(1)

    prvni_obec_data = ziskej_data_z_obce(obce[0]["odkaz"])
    strany = list(prvni_obec_data.keys())[3:]
    
    hlavicka = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"] + strany

    print(f"UKLÁDÁM DATA DO SOUBORU: {jmeno_souboru}")
    
    with open(jmeno_souboru, mode="w", newline="", encoding="utf-8-sig") as csv_soubor:
        writer = csv.writer(csv_soubor, delimiter=";")
        writer.writerow(hlavicka)
        
        for obec in obce:
            data = ziskej_data_z_obce(obec["odkaz"])
            
            radek = [
                obec["kod"],
                obec["nazev"],
                data["Voliči v seznamu"],
                data["Vydané obálky"],
                data["Platné hlasy"]
            ]
            
            for strana in strany:
                radek.append(data.get(strana, "0"))
                
            writer.writerow(radek)
            
    print("DOKONČENO: Data byla úspěšně uložena.")

if __name__ == "__main__":
    main()
