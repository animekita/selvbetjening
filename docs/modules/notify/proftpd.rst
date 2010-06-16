**************
Proftpd Notify
**************

Proftpd notify modulet integrere ftp serveren proftpd med selvbetjening.

Der antages at proftpd bruger sql som back-end for dens brugere.

Bestemte bruger grupper i selvbetjening bliver synkroniseret med
grupper i proftpd, således at ændringer i de tilknyttede brugere i
selvbetjening bliver reflekteret i proftpd.

En selvbetjening gruppe kan derfor være tilknyttet en, og kun en,
gruppe i proftpd. Eftersom proftpd gruppe navnet er dens primære
nøgle så synkroniseres deres navne ikke imellem de to.

Slettes selvbetjening gruppen bliver der ikke ændret noget ved
proftpd gruppen.