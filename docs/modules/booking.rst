***************
Booking Modulet
***************

Baggrund
========

Til vores arrangementer vil vi have nogle større anime biografer. Hvad der vises i disse styres af arrangementets gæster, hvor disse kan vælge imellem en samling af anime som er blevet medbragt af andre deltagere. Eftersom biografen kan være noget afsidesliggende, og der er andre folk end vores gæster i HUSET, så vil den medbragte anime være placeret på et bord ved receptionen. For at se en anime, skal vores gæster så tage en anime fra dette bord og tage det med til biografen hvor de så kan se denne anime.

Formål
======

Formålet med booking systemet (herefter betegnet som Booking) er at skabe et simpelt system til at administrere brugen af anime biografen. Booking vil holde styr på hvilken anime vil blive vist hvornår, således at gæster til arrangementet kan danne sig et overblik over ting der snart vil blive vist. Samtidig vil booking kunne bruges til at holde styr hvilken anime der er blevet udlånet, og til hvem. Derved kan man fra receptionen se om biografen er fri, og vi kan fra receptionen sikre os at kun en anime er taget derfra ad gangen. Dette skulle sikre de medbragte anime betydeligt.

Så, med Booking vil vi opnå følgende:

 * Vores gæster vil kunne danne sig et overblik over anime som vises senere
 * Man kan reservere et bestemt tidspunkt
 * Hvis der er nogen der er ved at se en film, kan man reservere biografen efter dem, hvilket formindsker mulige konflikter
 * Vi kan holde styr på og overvåge den anime der er udlånt til os

Hvem bruger booking
===================

Der er to typer af brugere:

Gæster
  Vil gerne reservere biografen, fjerne deres reservation, samt se hvad der vises nu samt senere på dagen.
Officials
  Vil notere at en anime er blevet fjernet fra bordet, og hvem der har taget den med.

Usecases
========

Gæst reservere tid online
-------------------------

 1. Gæsten ser en liste over reservationer, og notere sig den tid hun gerne vil have
 2. Gæsten vælger så at reservere en tid, kræver bruger på selvbetjening
 3. Gæsten oplyser tid samt titel på anime, og oplyses at hun skal sørge for at denne anime er til stede til arrangementet 

Gæst reservere tid ved arrangementet
------------------------------------

 0. Gæsten ser på det anime der er til rådighed ved arrangementet <ser på bordet>
 1. Gæsten ser en liste over reservationer, og notere sig den tid hun gerne vil have
 2. Gæsten vælger så at reservere en tid, der kræves selvbetjening bruger
 3. Gæsten oplyser tid samt titel på anime
 4. Gæsten logges af sin bruger igen automatisk

Gæst afbestiller reservation
----------------------------

 0. Gæst beder om at afbestille reservation
 1. Der bedes om selvbetjening brugeroplysninger
 2. En liste over reservationer for denne bruger vises, der er mulighed for at fjerne disse
 3. Bruger logges automatisk af

Checkout af anime
-----------------

 0. Gæst siger til reception at hun tager en anime, og oplyser den reservation den er forbundet med
 1. Der registreres gæstens brugernavn samt reservation og anime navn

Checkin af anime
----------------

 0. Gæst siger til reception at aflevere en anime, og oplyser den reservation den er forbundet med
 1. Der registreres at denne er blevet afleveret
