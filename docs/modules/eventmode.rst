*****************
Eventmode Modulet
*****************

Analyse
=======

System Definition
-----------------

Eventmode modulet indeholder en række værktøjer primært til brug ved arrangementer. Værktøjerne er målrettet personel der står for registreringen af deltagere ved arrangementets start samt under et arrangement.

Eventmode giver mulighed for:

* Tilgå arrangement information såsom tilvalg og deltagere
* Lave et "checkin" på en deltager
* Lave et "checkin" på en bruger (ikke tilmeldte personer)

Problem Området
---------------

Til et arrangement er der på forhånd lavet en liste af tilmeldinger og i visse tilfælde en række ekstra tilvalg disse deltagere har lavet. Møder en tilmeldt op til et arrangement burde denne person derefter registreres som en deltager.

Disse informationer tilgås til et arrangement fra nogle få udvalgte event maskiner der er dedikeret til dette formål.

Anvendelses Området
-------------------

Event maskinerne betjenes af personer instrueret og godkendt i brugen af maskinerne. Maskinerne vil blive brugt til et arrangement og der skal derfor tages højde for at der er en høj risiko for at ikke godkengt personel får adgang til disse.

Design
======

Eventmode har to overordnet opgaver; implementer værktøjer til at løse diverse opgaver til et arrangement og sørg for at disse værktøjer kun kan bruges på godkendte maskiner. Første opgave løses ved at lave en række *forms* og *views* der kan arbejde på et bestemt arrangement. Anden opgave løses ved at registrere "event maskiner" som har adgang til eventmode, samt implementere en decorator der kan godkende adgang til et view baseret på den kalende maskine.
