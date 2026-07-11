import os
import subprocess
from langchain_core.tools import tool

@tool
def kreiraj_ili_zapisi_datoteku(putanja: str, sadrzaj: str) -> str:
    """
    Kreira novu datoteku ili prepisuje postojecu na zadanoj putanji s definiranim sadrzajem.
    Koristi ovaj alat kada trebas stvoriti Dockerfile, skripte ili konfiguracijske datoteke.
    """
    try:
        # Osiguraj da direktorij postoji
        os.makedirs(os.path.dirname(os.path.abspath(putanja)), exist_ok=True)
        
        with open(putanja, "w", encoding="utf-8") as f:
            f.write(sadrzaj)
        return f"Uspjesno kreirana datoteka na putanji: {putanja}"
    except Exception as e:
        return f"Greska prilikom zapisivanja datoteke: {str(e)}"

@tool
def pokreni_lokalnu_naredbu(naredba: str) -> str:
    """
    Izvrsava bash naredbu na lokalnom sustavu unutar projekta i vraca ispis (stdout/stderr).
    Koristi ovaj alat za pokretanje testova, provjeru lintera ili bildanje Docker slika.
    """
    try:
        # Pokrećemo naredbu i hvatamo izlaz
        rezultat = subprocess.run(
            naredba, 
            shell=True, 
            text=True, 
            capture_output=True, 
            timeout=30
        )
        
        if rezultat.returncode == 0:
            return f"Naredba uspjesno izvrsena. Izlaz:\n{rezultat.stdout}"
        else:
            return f"Naredba je pala s kodom {rezultat.returncode}. Error:\n{rezultat.stderr}"
    except subprocess.TimeoutExpired:
        return "Greska: Izvrsavanje naredbe je prekinuto zbog timeouta (30s)."
    except Exception as e:
        return f"Greska prilikom izvrsavanja naredbe: {str(e)}"