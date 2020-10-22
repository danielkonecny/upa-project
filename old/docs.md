# Dokumentace k projektu UPA

## Zvolené téma
COVID-19 (varianta 04) - dr. Rychlý

## Řešitelé
* Filip Jeřábek (xjerab24)
* Daniel Konečný (xkonec75)
* Tomáš Ryšavý (xrysav27)

## Zvolené dotazy a formulace vlastního dotazu

### Dotaz varianty A
V grafech zobrazte tempo změny počtů aktuálně nemocných (absolutní i procentuální přírůstek pozitivních případů a klouzavý průměr různých délek v různých časech).

### Dotaz varianty B
Určete vliv počtu nemocných a jeho změny v čase na sousední okresy (aneb zjistěte jak se šíří nákaza přes hranice okresů).

### Vlastní dotaz
`Vymyslet vlastní.`
Inspiraci pro další možné dotazy můžete čerpat ze [Seznam Zprávy: COVID-19 v České republice](https://www.seznamzpravy.cz/clanek/koronavirus-v-cislech-jak-nakaza-postupuje-ceskem-92585).

## Stručná charakteristika zvolené datové sady
Zdrojem dat jsou otevřené datové sady publikované Ministerstvem zdravotnictví České republiky týkající se onemocnění COVID-19 dostupné [zde](https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19). Používaná data jsou z datové sady s názvem `COVID-19: Přehled epidemiologické situace dle hlášení krajských hygienických stanic podle okresu` a zpracovaná jsou v JSON formátu, který je dostupný na [této adrese](https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/kraj-okres-nakazeni-vyleceni-umrti.json). Datová sada obsahuje denní informace o přírůtsku nakažených, vyléčených a zemřelých osob v jednotlivých krajích a okresech. Je aktualizovaná s týdenním zpožděním z důvodu validace informací krajskými hygienickými stanicemi.

Data ve formátu JSON jsou stažena z internetové adresy uvedené výše. Kořenový JSON objekt obsahuje informaci o čase vytvoření této datové sady, dále zdroj, ze kterého data pocházejí, a poté pole samotných dat o přírůstcích. Jedna položka tohoto pole odpovídá informacím z jednoho dne v jednom okrese a navíc je uvedený i kraj. Dále obsahuje kumulativní počet nakažených, vyléčených a zemřelých.

```
{
    "modified": "2020-10-21T01:01:32+02:00",
    "source": "https:\/\/onemocneni-aktualne.mzcr.cz\/",
    "data": [
        {
            "datum": "2020-03-01",
            "kraj_nuts_kod": "CZ010",
            "okres_lau_kod": "CZ0100",
            "kumulativni_pocet_nakazenych": 2,
            "kumulativni_pocet_vylecenych": 0,
            "kumulativni_pocet_umrti": 0
        },
        {
            "datum": "2020-03-01",
            "kraj_nuts_kod": "CZ020",
            "okres_lau_kod": "CZ020A",
            "kumulativni_pocet_nakazenych": 0,
            "kumulativni_pocet_vylecenych": 0,
            "kumulativni_pocet_umrti": 0
        }
    ]
}
```

## Zvolený způsob uložení surových dat:
`Zde stručně charakterizujte NoSQL databázi, která bude využita pro uložení zvolených zdrojových dat.`
