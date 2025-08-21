# MDSAPP/core/models/dossier.py

from pydantic import BaseModel, Field
from typing import List

class Woning(BaseModel):
    """Defines the structure for a single property."""
    adres: str = Field(description="Fictief maar realistisch adres van de woning")
    vraagprijs: int = Field(description="De vraagprijs in euro")
    bouwjaar: int = Field(description="Het bouwjaar van de woning")
    oppervlakte_m2: int = Field(description="De woonoppervlakte in vierkante meters")
    kamers: int = Field(description="Het totaal aantal kamers")

class Woonwensen(BaseModel):
    """Defines the search criteria of the client."""
    regio: str = Field(description="De regio of stad waar de klant zoekt")
    woningtype: str = Field(description="Het type woning, bijv. Appartement, Rijtjeshuis")
    min_kamers: int
    vereisten: List[str] = Field(description="Een lijst met specifieke eisen, bijv. 'Tuin op het zuiden'")

class Klantprofiel(BaseModel):
    """Defines the profile of the client."""
    naam: str = Field(description="Fictieve naam van de klant (bijv. 'Familie De Vries')")
    budget: int = Field(description="Het maximale budget van de klant in euro")
    huidige_situatie: str = Field(description="Een korte omschrijving van de huidige woonsituatie en reden van verhuizing")

class Klantdossier(BaseModel):
    """The main model that combines all parts of a customer dossier."""
    bronnen: List[str] = Field(default_factory=list, description="Lijst van bronnen gebruikt voor het genereren van dit dossier")
    klantprofiel: Klantprofiel
    woonwensen: Woonwensen
    voorgestelde_woningen: List[Woning] = Field(description="Een lijst van 1 tot 3 fictieve woningen die passen bij het zoekprofiel")
