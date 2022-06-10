# OCR post-processing

Þessi gagnahirsla inniheldur tól til þess að þjálfa ljóslestrarvilluleiðréttingarlíkan.

Sökum þess hve lítið magn leiðréttra ljóslesinna texta fyrirfinnst eru þeir, í núverandi mynd kóðagrunnsins, notaðir til þess að kortleggja villur og einnig sem matsgögn (e. **validation data**) við þjálfun líkansins. Villurnar úr þessum textum eru svo settar af handahófi inn í venjulega texta, sem notandi þarf að útvega sjálfur (t.d. úr [Risamálheildinni](https://repository.clarin.is/repository/xmlui/handle/20.500.12537/192)), og þeir eru svo notaðir sem þjálfunargögn (e. **training data**). Dæmi um villurnar má sjá hér:

| orig | corr | freq |
|:------:|:------:|:------:|
|   p    |   þ  | 2779 |
|   i   |    í  |  1141    |
|   li   |   h   |  247    |
|   rn   |   m   |  166    |
|   ri   |   n   |  19    |

### Ferli

Fyrsta skrefið er að setja saman gagnasafn, sem samanstendur af ljóslesnum textum og leiðréttum útgáfum þeirra. Í þessari gagnahirslu er að finna u.þ.b. 50.000 línur af slíkum samhliða gögnum en þær duga tæplega til þess að þjálfa

Áður en hægt er að þjálfa líkanið þarf að setja upp nauðsynleg gögn, þ.m.t. Pandas-gagnaramma (e. **dataframe**), SQLite-gagnagrunn og villuskjöl:

`$ python3 setup.py`

Athugið að áður en þessi skrifta er keyrð þarf að skilgreina nokkrar breytur í `globals.py`:

`ORIGINAL_FILES = 'mappan/sem/ljóslesin/gögn/eru/í'` </br>
`CORRECTED_FILES = 'mappan/sem/leiðréttu/gögnin/eru/í'` </br>
`ORIGINAL_VAL_FILES = 'mappan/sem/ljóslesnu/matsgögnin/eru/í'` </br>
`CORRECTED_VAL_FILES = 'mappan/sem/leiðréttu/matsgögnin/eru/í'` </br>

Næst þarf að þjálfa tilreiðara (e. **tokenizer**):

`$ python3 train_wordpiece_tokenizer.py --vocab-size 3000 --min-freq 3 --corpus móðurmappa/ljóslesinna/texta`

Þessi skrifta „þjálfar“ WordPiece-tilreiðara.

`--vocab-size` ræður því niður í hversu marga orðhluta textarnir eru brotnir. </br>
`--min-freq` ræður því hversu oft orðhluti þarf að koma fyrir í textanum til að vera talinn með. </br>
`--corpus` vísar til möppunnar sem inniheldur ljóslesna og leiðrétta texta en uppbygging hennar þarf að vera með þessum hætti:
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