# Configuratie voor bouwvergunningen data
# Configuration for building permits data

# Nederlandse kolomnamen mapping
DUTCH_COLUMN_NAMES = {
    # Identificatie kolommen
    'REFNIS': 'refnis_code',
    'REFNIS_NL': 'gemeente_naam_nl', 
    'REFNIS_FR': 'gemeente_naam_fr',
    
    # Tijd kolommen  
    'CD_YEAR': 'jaar',
    'CD_PERIOD': 'periode',
    
    # Nieuwbouw woningen
    'MS_BUILDING_RES_NEW': 'nieuwbouw_gebouwen_wonen',
    'MS_DWELLING_RES_NEW': 'nieuwbouw_woningen_totaal',
    'MS_APARTMENT_RES_NEW': 'nieuwbouw_appartementen',
    'MS_SINGLE_HOUSE_RES_NEW': 'nieuwbouw_eengezinswoningen',
    'MS_TOTAL_SURFACE_RES_NEW': 'nieuwbouw_oppervlakte_wonen_m2',
    
    # Renovatie woningen
    'MS_BUILDING_RES_RENOVATION': 'renovatie_gebouwen_wonen',
    
    # Nieuwbouw niet-residentieel
    'MS_BUILDING_NONRES_NEW': 'nieuwbouw_gebouwen_bedrijven',
    'MS_VOLUME_NONRES_NEW': 'nieuwbouw_volume_bedrijven_m3',
    'MS_BUILDING_NONRES_RENOVATION': 'renovatie_gebouwen_bedrijven',
    
    # Geografische codes
    'CD_REFNIS_NATION': 'code_land',
    'CD_REFNIS_REGION': 'code_gewest', 
    'CD_REFNIS_PROVINCE': 'code_provincie',
    'CD_REFNIS_DISTRICT': 'code_arrondissement',
    'CD_REFNIS_MUNICIPALITY': 'code_gemeente',
    'CD_REFNIS_LEVEL': 'geografisch_niveau'
}

# Omgekeerde mapping (Nederlands naar Engels)
ENGLISH_COLUMN_NAMES = {v: k for k, v in DUTCH_COLUMN_NAMES.items()}

# Beschrijvingen van kolommen in het Nederlands
COLUMN_DESCRIPTIONS = {
    'refnis_code': 'Unieke REFNIS identificatiecode voor het geografische gebied',
    'gemeente_naam_nl': 'Nederlandse naam van de gemeente/regio',
    'gemeente_naam_fr': 'Franse naam van de gemeente/regio',
    'jaar': 'Jaar van de bouwvergunning',
    'periode': 'Periode binnen het jaar (0=heel jaar, 1-4=kwartalen)',
    'nieuwbouw_gebouwen_wonen': 'Aantal nieuwe woongebouwen waarvoor vergunning is verleend',
    'nieuwbouw_woningen_totaal': 'Totaal aantal nieuwe woningen waarvoor vergunning is verleend',
    'nieuwbouw_appartementen': 'Aantal nieuwe appartementen waarvoor vergunning is verleend',
    'nieuwbouw_eengezinswoningen': 'Aantal nieuwe eengezinswoningen waarvoor vergunning is verleend',
    'nieuwbouw_oppervlakte_wonen_m2': 'Totale oppervlakte nieuwe woningen in vierkante meters',
    'renovatie_gebouwen_wonen': 'Aantal woongebouwen waarvoor renovatievergunning is verleend',
    'nieuwbouw_gebouwen_bedrijven': 'Aantal nieuwe niet-residentiële gebouwen waarvoor vergunning is verleend',
    'nieuwbouw_volume_bedrijven_m3': 'Volume nieuwe niet-residentiële gebouwen in kubieke meters',
    'renovatie_gebouwen_bedrijven': 'Aantal niet-residentiële gebouwen waarvoor renovatievergunning is verleend',
    'code_land': 'Code voor het land (België = 1000)',
    'code_gewest': 'Code voor het gewest (Vlaanderen, Wallonië, Brussel)',
    'code_provincie': 'Code voor de provincie',
    'code_arrondissement': 'Code voor het arrondissement',
    'code_gemeente': 'Code voor de gemeente',
    'geografisch_niveau': 'Niveau van geografische aggregatie (1=land, 2=gewest, etc.)'
}

# Originele kolommen (voor referentie)
ORIGINAL_COLUMNS = [
    'REFNIS', 'REFNIS_NL', 'REFNIS_FR', 'CD_YEAR', 'CD_PERIOD',
    'MS_BUILDING_RES_NEW', 'MS_DWELLING_RES_NEW', 'MS_APARTMENT_RES_NEW', 
    'MS_SINGLE_HOUSE_RES_NEW', 'MS_TOTAL_SURFACE_RES_NEW',
    'MS_BUILDING_RES_RENOVATION', 'MS_BUILDING_NONRES_NEW', 
    'MS_VOLUME_NONRES_NEW', 'MS_BUILDING_NONRES_RENOVATION',
    'CD_REFNIS_NATION', 'CD_REFNIS_REGION', 'CD_REFNIS_PROVINCE',
    'CD_REFNIS_DISTRICT', 'CD_REFNIS_MUNICIPALITY', 'CD_REFNIS_LEVEL'
]