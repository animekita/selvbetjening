.. Selvbetjening documentation master file

Velkommen til dokumentationen for Selvbetjening
===============================================

Dette dokument beskriver Selvbetjening, et system målrettet foreninger der skal bruge et system til tilmelding af arrangementer og håndtering af medlemmer.

Denne dokumentation er målrettet software udviklere der skal arbejde på Selvbetjening. Der antages derfor at personer der læser dette har en vis teoretisk og praktisk forståelse inden for datalogi.

System Definition
=================

Selvbetjening fungere som den elektroniske grænseflade mellem en foreningen og dens medlemmer. Selvbetjening er tænkt som en samling moduler der udgør hjertet i den tekniske del af foreningen. Visse services, såsom et forum, installeres separat og kobles sammen med Selvbetjening for at danne en samlet løsning.

Følgende områder er derfor i fokus for Selvbetjening:

1. Et samlet system hvor medlemmer opretter *en* bruger som sammenknytter alle foreningens elektroniske systemer. F.eks. en forenings forum og selvbetjening selv.
2. Administration og tilmelding til arrangement.
3. Administration af kontingenter, betalinger, brugeroplysninger og nyhedsbrev.
4. Modularitet, ikke alle installationer er ens, derfor skal Selvbetjening kunne modificeres efter den enkelte forenings behov.

Arkitektur
==========

.. toctree::
   :maxdepth: 1
   :glob:

   architecture/*

Core
----

.. toctree::
   :maxdepth: 1
   :glob:

   modules/core/*

ViewBase
--------

.. toctree::
   :maxdepth: 1
   :glob:

   modules/viewbase/*

Portal
------

.. toctree::
   :maxdepth: 1
   :glob:

   modules/portal/*

SAdmin
------

.. toctree::
   :maxdepth: 1
   :glob:

   modules/sadmin/*

API
---

.. toctree::
   :maxdepth: 1
   :glob:

   modules/api/*

Notify
------

.. toctree::
   :maxdepth: 1
   :glob:

   modules/notify/*

Appendix
========

.. toctree::
   :maxdepth: 1
   :glob:

   appendix/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

