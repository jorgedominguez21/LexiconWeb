# constantes.py
CATEGORIAS_GRAMATICALES = {
    "Sustantivo": "sust",
    "Adjetivo": "adj",
    "Verbo": "verb",
    "Adverbio": "adv",
    "Pronombre": "pron",
    "Preposición": "prep",
    "Conjunción": "conj",
    "Interjección": "inter"
}

# También es útil tener el inverso para mostrar el nombre bonito en la UI
CATEGORIAS_INVERSAS = {v: k for k, v in CATEGORIAS_GRAMATICALES.items()}