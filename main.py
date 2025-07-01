from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

# Omogući CORS za Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ili tačno tvoja Flutter domena u deployu
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/oglasi")
async def oglasi(
    godina_od: int = Query(1990),
    godina_do: int = Query(2025),
    cijena_do: int = Query(15000),
):
    url = (
        "https://www.willhaben.at/iad/gebrauchtwagen/auto/gebrauchtwagenboerse?"
        f"SELLER_TYPE=PRIVATE&rows=30&page=1&sort=1"
        f"&PRICE_FROM=0&PRICE_TO={cijena_do}"
        f"&YEAR_FROM={godina_od}&YEAR_TO={godina_do}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        oglasi = []
        for ad in soup.select("div.SearchResults__AdWrapper-sc-1i0g3sn-2"):
            naslov = ad.select_one("h3")
            cijena = ad.select_one("strong[itemprop='price']")
            link = ad.select_one("a")["href"] if ad.select_one("a") else None
            opis = ad.select_one("div.SearchResults__DescriptionContainer-sc-1i0g3sn-14")
            if naslov and cijena:
                oglasi.append({
                    "naslov": naslov.get_text(strip=True),
                    "cijena": cijena.get_text(strip=True),
                    "link": f"https://www.willhaben.at{link}" if link else None,
                    "opis": opis.get_text(strip=True) if opis else "",
                    "kontaktInfo": None  # Dodaj scraping kontakt info kasnije
                })

        return oglasi
