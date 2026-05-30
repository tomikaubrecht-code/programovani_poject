# Volební scraper - Projekt 3 (Engeto)

## O co jde v projektu?
Tento skript v jazyce Python umožňuje získat detailní výsledky parlamentních voleb z roku 2017 pro konkrétní okres nebo územní celek z [oficiální webové stránky voleb](https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ) a uložit je přehledně do `.csv` souboru.

## Jak na to?
Před spuštěním projektu si vytvořte virtuální prostředí a nainstalujte potřebné knihovny uvedené v souboru `requirements.txt`. Skript následně spustíte z příkazového řádku zadáním dvou argumentů (odkaz na územní celek a název výstupního souboru):

```bash
pip install -r requirements.txt
python projekt_3.py <odkaz_uzemniho_celku> <vystupni_soubor.csv>