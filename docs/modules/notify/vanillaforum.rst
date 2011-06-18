***********************
Vanilla Forum 2+ Notify
***********************

Dette modul gør det muligt at spejle alle brugerinformationer i selvbetjening med en `Vanilla Forum 2+ <http://vanillaforums.org/>`_ installation. Forummet skal indstilles således at den ikke selv ændre i disse oplysninger, men i stedet henviser nye og eksisterende brugere til selvbetjening.

Følgende informationer spejles mellem de to installationer for hver bruger:

* Brugernavn
* E-mail
* Oprettelsesdato (kun igennem sync kommandoen)
* Profil billede
* Notifikation-indstillinger (ikke implementeret)
* Udvalgte bruger-grupper (inklusiv standard bruger gruppe) (ikke implementeret)

Bemærk at overstående bliver spejlet løbende når ændringer indtræffer i selvbetjening. For at få alle informationer spejlet uden de nødvendigvis er ændret er der stillet en kommando til rådighed igennem *management.py*. Dette er f.eks. nødvendigt efter den indledende installation.
