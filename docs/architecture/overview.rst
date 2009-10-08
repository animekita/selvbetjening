========
Oversigt
========

Selvbetjening er opdelt i tre forskellige typer moduler; data, clients og viewhelpers.

 Data moduler::
  Data modulerne indeholder informationer og procedurer der er centrale for selvbetjening. Data modulerne er indbyrdes afhængige af hinanden så alle data modulerne er påkrævet for en installation.
 Client moduler::
  Client modulerne står for manipulation af data modulerne. Modulerne er kun afhængige af data modulerne og ikke af andre client moduler. Disse er derfor velegnet til at fjerne og tilføje alt efter den enkelte forenings behov.
 Viewhelpers::
  Bruges af clienterne til diverse formål såsom rendering af formularer. Kan bruges af flere forskellige clienter.

.. image:: images/architecture.png

Ud over disse tre typer moduler så definere hvert modul de nødvendige stukturer brugt af Djangos administrations interface. Derved kan alle brugte moduler i en installation administreres af dette samlet interface.
