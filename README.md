# Leiðrétting ljóslestrarvillna

Þessi gagnahirsla inniheldur tól til þess að þjálfa ljóslestrarvilluleiðréttingarlíkan.

Sökum þess hve lítið magn leiðréttra ljóslesinna texta fyrirfinnst er hér gert ráð fyrir að notandi útvegi venjulega íslensa texta, t.d. úr [Risamálheildinni](https://repository.clarin.is/repository/xmlui/handle/20.500.12537/192), sem eru svo fylltir af villum úr ljóslestrargögnunum sem eru hluti þessarar gagnahirslu. Sjá: `data/parallel/50k_gold`. Notandi þarf einnig sjálfur að sjá um að skipta gögunum í þjálfunar-, mats- og prófunargögn. Dæmi um ljóslestrarvillur:


| orig | corr | freq |
|:------:|:------:|:------:|
|   p    |   þ  | 2779 |
|   i   |    í  |  1141    |
|   li   |   h   |  247    |
|   rn   |   m   |  166    |
|   ri   |   n   |  19    |

### Ferli

Fyrsta skrefið er að þjálfa tilreiðara (e. *tokenizer*). </br>
`$ python3 train_wordpiece_tokenizer.py --vocab-size 3000 --min-freq 3 --corpus data/parallel/50k_gold`. </br>
Mappan sem vísað er til þarf að innihalda ljóslesna texta og leiðréttar útgáfur þeirra en ekki þó endilega gagnasafnið í heild sinni. Því er hægt að nota gögnin í `data/paralell/50k_gold` sem þjálfunargögn. **Mikilvægt er að sami tilreiðarinn sé notaður við uppsetningu gagnanna, þjálfun og prófun.**

Að tilreiðara þjálfuðum þarf að sækja ljóslestrarvillurnar í grunngögnin (`data/parallel/50k_gold`) og setja upp villuskjal og -gagnagrunn:

`$ python3 setup.py --errors`

Athugið að staðsetning ljóslestrargagnanna er harðkóðuð inn í `setup.py`.


Þegar villugögnin hafa verið sett upp þarf að sækja venjulega texta (t.d. úr Risamálheildinni) og koma þeim einhvers staðar fyrir, t.d. í `data/ocr_dataset/corrected`. Þá er hægt að keyra ljóslestrarvillurnar inn í þá.

`cd utils`
`$ python3 noise_to_corpus.py --corpus data/ocr_dataset/corrected`

Þetta býr til möppu í `data/ocr_dataset` sem heitir `original` og þá eru þjálfunargögnin tilbúin. Skilgreina þarf staðsetningu þeirra í `globals.py`.


Þjálfunargögnin eru geymd í Pandas-gagnarömmum (e. *dataframes*) við keyrslu og til þess að koma í veg fyrir að þá þurfi að setja upp í hvert skipti sem líkan er þjálfað eða prófað eru þeir vistaðir einu sinni. Þeim þarf ekki að breyta, að því gefnu að þjálfunar- og matsgögn og tilreiðari haldist óbreytt. Þeir eru settir upp svona:

`$ python3 setup.py --type dataframes`

Breytist þjálfunar eða matsgögn eða tilreiðari þarf að keyra þessa skipun aftur.


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




Þessi skrifta þjálfar WordPiece-tilreiðara.

`--vocab-size` ræður því niður í hversu marga orðhluta textarnir eru brotnir. </br>
`--min-freq` ræður því hversu oft orðhluti þarf að koma fyrir í textanum til að vera talinn með. </br>
`--corpus` vísar til möppunnar sem inniheldur ljóslesna og leiðrétta texta en uppbygging hennar þarf að vera með þessum hætti:
