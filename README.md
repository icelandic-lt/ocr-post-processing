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

### Ferlið

Áður en hægt er að þjálfa líkanið þarf að sækja villur í ljóslesnu skjölin, svo hægt sé að setja þau inn í raunverulegu textana:


