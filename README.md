# Leiðrétting ljóslestrarvillna

Þessi gagnahirsla inniheldur meðal annars:

* tvö þjálfuð transformer-líkön (PyTorch og fairseq) til leiðréttingar á ljóslestrarvillum
* `infer.py` til að leiðrétta ljóslestrarvillur
* `train.py` til að þjálfa transformer-líkön (PyTorch)

Tólið á að virka að forritseiningum uppsettum (`python3 -m pip install -r requirements.txt`) en til þess að þjálfa ný líkön þarf að útbúa þjálfunargögn (sjá [uppsetningu gagna](#uppsetning-gagna)).

PyTorch-líkanið var þjálfað með WordPiece-tilreiðara og fairseq með SentencePiece, báðum skipt í 3000 einingar. Fyrrnefnda líkanið nær meiri nákvæmni með tilliti til bókstafa en hið síðarnefnda sé litið til orða.

Í núverandi mynd nær leiðréttingartólið þessum árangri með prófunargögnin til hliðsjónar:

<table>
  <tr>
    <th></th>
    <th>PyTorch</th>
    <th>fairseq</th>
    <th>Combined</th>
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
    <tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</table>
(ERR = Error Rate Reduction: fækkun ljóslestrarvillna í prósentum talið)

<br>

Líkönin voru þjálfuð á u.þ.b. 900.000 línum (~7.000.000 orð) en af þeim voru ekki nema um 50.000 (~400.000 orð) úr raunverulegum ljóslesnum gögnum. Ætla má að aukið magn slíkra gagna gæti bætt tólið umtalsvert.
<br>
<br>

## Uppsetning gagna
---
Sökum skorts raungagna á forminu **ljóslesinn/leiðréttur texti** voru gervivillur (e. artificial errors) settar inn í texta sem m.a. voru sóttir úr [Risamálheildinni](https://repository.clarin.is/repository/xmlui/handle/20.500.12537/192). Villurnar voru fengnar úr þeim ljóslesnu/leiðréttu gögnum sem til eru. Eftirfarandi skriftur má nota í þeim tilgangi:

* `setup.py --type errors` til þess að sækja villur í texta og setja upp í SQLite-gagnagrunn.
* `utils/noise_to_corpus.py --corpus /path/to/corpus/` til þess að setja gervivillur inn í texta.

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
parent_dir
└───original
|
└───corrected
|    |    corrected_1.txt
|    |    corrected_2.txt
```

Skjölin í `corrected` eru einfaldlega venjulegir textar, sem eru þá „leiðréttir“, þ.e. ekki er búið að setja í þá villur. Skriftan býr svo til „ljóslesnar“ útgáfur leiðréttu textanna, þ.e. setur inn í þá þekktar ljóslestrarvillur og vistar þær í `original`.

Að þessu loknu þarf að harðkóða þjálfunargögnin inn í `globals.py` og keyra `python3 setup.py --type dataframes`.

Ekki er hægt að deila þjálfunargögnunum vegna leyfismála en hægur leikur er að sækja gögn sem henta til þjálfunar í Risamálheildina. Athygli er þó vakin á því að mikið magn nútímatexta getur valdið því að líkönin fara að alhæfa um of og nútímavæða eldri stafsetningu.



## Tilreiðing
---
WordPiece-tilreiðarann sem PyTorch-transformer-módelið styðst við er að finna í `ocr_tokenizers/`. Hægt er að þjálfa nýjan slíkan:

`python3 train_wordpiece_tokenizer.py --vocab-size <fjöldi orðhluta> --min-freq <lágmarkstíðni orðhluta> --corpus <path/to/corpus/>`

Þessi skrifta þjálfar tilreiðara og vistar hann í `ocr_tokenizers/`. Athugið að tilreiðarinn er harðkóðaður inni í `globals.py` og nauðsynlegt er að nota sama tilreiðarann við þjálfun og prófun.

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

##### Lykilskrár

* `globals.py`: Breytur sem aðrar forritseiningar nota </br>
* `train_wordpiece_tokenizer.py`: Þjálfar tilreiðara </br>
* `setup.py --type errors`: Setur upp villuskjal og -gagnagrunn </br>
* `utils/noise_to_corpus.py`: Setur ljóslestrarvillur inn í venjulegan texta
* `setup.py --type dataframes`: Vistar þjálfunar- og matsgögn í Pandas-gagnaramma </br>
* `train.py`: Þjálfar Transformer-líkan </br>
* `infer.py --model <módel> --infile <ljóslesin textaskrá>`: Les yfir og leiðréttir ljóslesinn texta

Sökum þess hve lítið magn leiðréttra ljóslesinna texta fyrirfinnst er hér gert ráð fyrir að notandi útvegi venjulega íslenska texta, t.d. úr [Risamálheildinni](https://repository.clarin.is/repository/xmlui/handle/20.500.12537/192), sem eru svo fylltir af villum úr ljóslestrargögnunum í `data/parallel/50k_gold`. Notandi þarf einnig sjálfur að sjá um að skipta gögunum í þjálfunar-, mats- og prófunargögn. 

---

### Ferli

Fyrsta þarf að þjálfa tilreiðara (e. *tokenizer*). </br>

`$ python3 train_wordpiece_tokenizer.py --vocab-size 3000 --min-freq 3 --corpus data/parallel/50k_gold`.

`--vocab-size`: Fjöldi orðhluta </br>
`--min-freq`: Lágmarkstíðni orðhluta </br>
`--corpus`: Mappa sem inniheldur ljóslesna og leiðrétta texta

Þessi skipun þjálfar WordPiece-tilreiðara, sem vistaður er í `ocr_tokenizers/`. Mappan sem vísað er til með `--corpus` þarf að innihalda ljóslesna texta og leiðréttar útgáfur þeirra en þó ekki endilega allt gagnasafnið sem notað er til þjálfunar á líkaninu sjálfu síðar meir. Gögnin í `data/paralell/50k_gold` eru raunveruleg ljóslesin og leiðrétt skjöl, svo þau henta til þess. **Mikilvægt er að sami tilreiðarinn sé notaður við uppsetningu gagnanna, þjálfun og prófun.**


Að tilreiðara þjálfuðum þarf að sækja ljóslestrarvillurnar í grunngögnin (`data/parallel/50k_gold`) og setja upp villuskjal og -gagnagrunn:

`$ python3 setup.py --errors`

Athugið að staðsetning ljóslestrargagnanna er harðkóðuð inn í `setup.py`.


Þegar villugögnin hafa verið sett upp þarf að sækja venjulega texta (t.d. úr Risamálheildinni) og koma þeim einhvers staðar fyrir, t.d. í `data/ocr_dataset/corrected`. Þá er hægt að keyra ljóslestrarvillurnar inn í þá.

`cd utils` </br>
`$ python3 noise_to_corpus.py --corpus data/ocr_dataset/corrected`

Þessar skipanir búa til möppu í `data/ocr_dataset`, `original`, og þá eru þjálfunargögnin tilbúin. Skilgreina þarf staðsetningu þeirra í `globals.py`.


Þjálfunargögnin eru geymd í Pandas-gagnarömmum (e. *dataframes*) við keyrslu og til þess að koma í veg fyrir að þá þurfi að setja upp í hvert skipti sem líkan er þjálfað eða prófað eru þeir vistaðir einu sinni. Þeim þarf ekki að breyta, að því gefnu að þjálfunar- og matsgögn og tilreiðari haldist óbreytt. Þeir eru settir upp svona:

`$ python3 setup.py --type dataframes`

Breytist þjálfunar- eða matsgögn eða tilreiðari þarf að keyra þessa skipun aftur.


Fyrsta skrefið er að setja saman gagnasafn, sem samanstendur af ljóslesnum textum og leiðréttum útgáfum þeirra. Í þessari gagnahirslu er að finna u.þ.b. 50.000 línur af slíkum samhliða gögnum, sem duga þó tæplega til þess að þjálfa gott módel og því þarf að drýgja þær með því að setja villurnar úr þeim inn í venjulega texta. Þessi gögn skulu sett upp á sama sniði og í trénu hér fyrir neðan og mikilvægt er að ljóslesnu gögnin (það á einnig við um venjulegu textana sem villurnar hafa verið settar inn í) séu í möppu sem heitir `corrected` og að leiðréttu gögnin (einnig venjulegu textarnir án villna) séu í möppu sem heitir `corrected`.

```
parent_dir
└───original
|    |    original_1.txt
|    |    original_2.txt
|
└───corrected
|    |    corrected_1.txt
|    |    corrected_2.txt
```

Áður en hægt er að þjálfa líkanið þarf að setja upp nauðsynleg gögn, þ.m.t. Pandas-gagnaramma (e. **dataframe**), SQLite-gagnagrunn og villuskjöl:

`$ python3 setup.py`

Athugið að áður en þessi skrifta er keyrð þarf að skilgreina nokkrar breytur í `globals.py`:

`ORIGINAL_FILES = 'mappan/sem/ljóslesin/gögn/eru/í'` </br>
`CORRECTED_FILES = 'mappan/sem/leiðréttu/gögnin/eru/í'` </br>
`ORIGINAL_VAL_FILES = 'mappan/sem/ljóslesnu/matsgögnin/eru/í'` </br>
`CORRECTED_VAL_FILES = 'mappan/sem/leiðréttu/matsgögnin/eru/í'` </br>




