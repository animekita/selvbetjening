Versioner
=========

Til at angive versioner bruges formatet x.y.z, hvor x er major version, y minor version og z bugfix. Der gælder de følgende regler:

1. Skifter man mellem forskellige patch versioner i samme major og minor versionslinje må systemet ikke gå ned. APIen skal være stabil i disse udgivelser. Den eneste forskel må være rettelser af fejl.
2. Går man en minor version op kan der forekomme nye funktioner og APIer. Men der må ikke forsvinde nogen funktionalitet eller ændres noget der ikke er bagud kompatibelt. Det skal derfor være sikkert at gå en minor version op, men ikke nødvendigvis sikkert at gå en ned.
3. Skifter major version må der ændres på alt API. Det er derfor ikke et krav her at være bagud kompatibel.

Udgivelsesadministration
------------------------

Som udgangspunkt opretholdes der to linjer af kode under udvikling, en bugfix- og udviklingslinje. 

En bugfix-linje indeholder rettelser for en bestemt udgivelse. For at holde administrationen så let som muligt skal antallet af bugfix-linjer holdes nede. Derfor vil der normalt kun være en bugfix linje til den nyeste udgivelse.

Udviklingslinjen er rettet mod enten en minor eller major udgivelse. Rettelser der bliver tilføjet til en bugfix-linje skal også tilføjes til trunk.
