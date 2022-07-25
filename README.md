# Leiðrétting ljóslestrarvillna

Þessi gagnahirsla inniheldur

* tvö þjálfuð transformer-líkön (PyTorch og fairseq) til leiðréttingar á ljóslestrarvillum
* `infer.py` til leiðréttingar á ljóslestrarvillum
* `train.py` til þjálfunar Transformer-líkana (PyTorch)

Forritið á að virka að því sóttu og forritseiningum uppsettum (`python3 -m pip install -r requirements.txt`).


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

Sökum þess hve lítið magn leiðréttra ljóslesinna texta fyrirfinnst er hér gert ráð fyrir að notandi útvegi venjulega íslenska texta, t.d. úr [Risamálheildinni](https://repository.clarin.is/repository/xmlui/handle/20.500.12537/192), sem eru svo fylltir af villum úr ljóslestrargögnunum í `data/parallel/50k_gold`. Notandi þarf einnig sjálfur að sjá um að skipta gögunum í þjálfunar-, mats- og prófunargögn. Dæmi um ljóslestrarvillur:


| orig | corr | freq |
|:------:|:------:|:------:|
|   p    |   þ  | 2779 |
|   i   |    í  |  1141    |
|   li   |   h   |  247    |
|   rn   |   m   |  166    |
|   ri   |   n   |  19    |

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




