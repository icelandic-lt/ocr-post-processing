# Leiðrétting ljóslestrarvillna

Til þess að sækja ljóslestrarvilluleiðréttingarlíkönin þarf að nota [git lfs](https://git-lfs.github.com/).

Þessi gagnahirsla inniheldur meðal annars:

* tvö þjálfuð transformer-líkön (PyTorch og fairseq) til leiðréttingar á ljóslestrarvillum
* `infer.py --model path/to/model --infile /path/to/ocred/file` til að leiðrétta ljóslestrarvillur
* `train.py` til að þjálfa transformer-líkön (PyTorch)
* U.þ.b. 50.000 línur af **ljóslesnum/leiðréttum textum**

Hægt er að nota tólið að forritseiningum uppsettum (`python3 -m pip install -r requirements.txt`) en til þess að þjálfa ný líkön þarf að útbúa þjálfunargögn (sjá [uppsetningu gagna](#uppsetning-gagna)).

PyTorch-líkanið var þjálfað með WordPiece-tókara og fairseq með SentencePiece, báðum skipt í 3000 einingar. Fyrrnefnda líkanið stendur sig betur sé mælikvarðinn chrF en hið síðarnefnda er nákvæmara sé litið til BLEU.

Skriftan `train.py` þjálfar einungis PyTorch-líkan.

Í núverandi mynd nær leiðréttingartólið þessum árangri með prófunargögn frá 19. öld til hliðsjónar:

<table>
  <tr>
    <th></th>
    <th>PyTorch</th>
    <th>fairseq</th>
    <th>Saman</th>
  </tr>
  
  <tr>
    <th>chrF</th>
    <td>96.84</td>
    <td>96.35</td>
    <td>96.85</td>
  </tr>
  
  <tr>
    <th>chrF ERR</th>
    <td>41.2</td>
    <td>32.2</td>
    <td>41.5</td>
  </tr>
  <tr>
    <th>BLEU</th>
    <td>98.44</td>
    <td>98.52</td>
    <td>98.45</td>
    </tr>
  <tr>
    <th>BLEU ERR</th>
    <td>44.45</td>
    <td>47.24</td>
    <td>44.74</td>
  </tr>
</table>

Og þessum árangri á prófunargögnum frá 1980-1999:
<table>
  <tr>
    <th></th>
    <th>PyTorch</th>
    <th>fairseq</th>
    <th>Saman</th>
  </tr>
  
  <tr>
    <th>chrF</th>
    <td>96.83</td>
    <td>96.58</td>
    <td>96.85</td>
  </tr>
  
  <tr>
    <th>chrF ERR</th>
    <td>33.8</td>
    <td>28.6</td>
    <td>34.2</td>
  </tr>
  <tr>
    <th>BLEU</th>
    <td>98.45</td>
    <td>98.54</td>
    <td>98.46</td>
    </tr>
  <tr>
    <th>BLEU ERR</th>
    <td>31.92</td>
    <td>36.14</td>
    <td>32.27</td>
  </tr>
</table>


(ERR = Error Rate Reduction: fækkun ljóslestrarvillna í prósentum talið)

Líkönin voru þjálfuð á u.þ.b. 900.000 línum (~7.000.000 orð) en af þeim voru ekki nema um 50.000 (~400.000 orð) úr raunverulegum ljóslesnum gögnum. Ætla má að aukið magn slíkra gagna geti bætt tólið umtalsvert.


## Uppsetning gagna

Sökum skorts raungagna á forminu **ljóslesinn/leiðréttur texti** voru gervivillur (e. artificial errors) settar inn í texta sem m.a. voru sóttir úr [Risamálheildinni](https://repository.clarin.is/repository/xmlui/handle/20.500.12537/192). Villurnar voru fengnar úr þeim ljóslesnu/leiðréttu gögnum sem til eru (`data/parallel/50k_gold/`). Eftirfarandi skriftur má nota í þeim tilgangi:

* `setup.py --type errors` til þess að sækja villur í texta (ath. að slóð gagnanna er harðkóðuð inn í `setup.py`) og setja upp í SQLite-gagnagrunn.
* `utils/noise_to_corpus.py --corpus path/to/corpus/` til þess að setja gervivillur inn í texta.

Dæmi um ljóslestrarvillur:


| orig  | corr  | freq  |
| :---: | :---: | :---: |
|   p   |   þ   | 2779  |
|   i   |   í   | 1141  |
|  li   |   h   |  247  |
|  rn   |   m   |  166  |
|  ri   |   n   |  19   |

Til þess að hægt sé að keyra `utils/noise_to_corpus.py` þarf uppbygging `path/to/corpus/` að vera með þessum hætti:

```
corpus
└───original
|
└───corrected
|    |    corrected_1.txt
|    |    corrected_2.txt
```

Skjölin í `corrected` eru einfaldlega venjulegir textar, sem eru þá „leiðréttir“, þ.e. ekki er búið að setja í þá villur. Skriftan býr svo til „ljóslesnar“ útgáfur leiðréttu textanna, þ.e. setur inn í þá þekktar ljóslestrarvillur, auk þess sem orð eru af handahófi slitin í sundur eða þeim skeytt saman, og vistar þær í `original`.

Að þessu loknu þarf að harðkóða slóð þjálfunargagnanna inn í `globals.py` og keyra `python3 setup.py --type dataframes`.

Ekki er hægt að deila öllum þjálfunargögnunum vegna leyfismála en hægur leikur er að sækja gögn sem henta til þjálfunar í Risamálheildina. Athygli er þó vakin á því að mikið magn nútímatexta getur valdið því að líkönin fara að alhæfa um of og nútímavæða eldri stafsetningu. Notandi þarf sjálfur að skipta gögunum í þjálfunar-, mats- og prófunargögn. 




## Tókun

WordPiece-tókarann sem PyTorch-transformer-módelið styðst við er að finna í `ocr_tokenizers/`. Hægt er að þjálfa nýjan slíkan:

`python3 train_wordpiece_tokenizer.py --vocab-size <fjöldi orðhluta> --min-freq <lágmarkstíðni orðhluta> --corpus <path/to/corpus/>`

Þessi skrifta þjálfar tókara og vistar hann í `ocr_tokenizers/`. Athugið að tókarinn er harðkóðaður inni í `globals.py` og nauðsynlegt er að nota sama tókarann við þjálfun og prófun.

