========
Oversigt
========

Selvbetjening er opdelt i fire forskellige typer moduler; core, viewbase, portal, sadmin, api og notify.

 Core
  Core modulerne definerer informationer og tilbyder funktionalitet som er centrale for selvbetjening. Der antages at alle core moduler altid er installeret eftersom de regnes som at være centrale for Selvbetjening.

 ViewBase
  ViewBase modulerne er målrettet rendering af elementer til en webbrowser og skal ses som en hjælp til andre moduler der har behov for dette.

 Portal
  Portal modulerne implementerer et web interface målrettet medlemmer af en forening.

 SAdmin
  SAdmin modulerne implementerer et web interface målrettet administrationen af en forening.

 API
  API modulerne blotlægger et webservice API (pull) som kan bruges af andre systemer til at snakke med Selvbetjening.

 Notify
  Notify modulerne implementerer et push baseret system til at meddele andre systemer om hændelser i Selvbetjening..


.. image:: images/architecture.png

Ud over disse tre typer moduler så definere hvert modul de nødvendige stukturer brugt af Djangos administrations interface. Derved kan alle brugte moduler i en installation administreres af dette samlet interface.
