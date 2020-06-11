# Create PlanetMicrobe Datapackages

This is a first pass writing a program to annotate an marine dataset with ontology terms.

## Requirements

Given a data set like [OSD](https://github.com/hurwitzlab/planet-microbe-datapackages/blob/master/OSD/osd_sample.tsv):

```
$ csvchk osd_sample.tsv
// ****** Record 1 ****** //
Sample ID                    : OSD186_2014-06-21_2.4m_NPL022
Sample label (BioSample)     : SAMEA3275469
Sample label (BioArchive)    : ABOKL60
Sample label (ENA)           : ERS667478
URL file                     : https://www.ebi.ac.uk/ena/data/view/ERS667478
Campaign                     : OSD-Jun-2014
Site label                   : OSD186
Site number                  : 186
Event                        : OSD186_20140621T1704Z
Device                       : Bottle, Kemmerer
Comment OBJECTIVE            : Participation in OSD
Comment PLATFORM             : Dock
Comment DEVICE REPORTED      : 5L-Kimmerer, YSI85
Comment DESCRIPTION          : collected with Kimmer below surface of water (total depth at site 2.4m)
URI                          : http://store.pangaea.de/Projects/OSD_2014/OSD186_20140621T1704Z.pdf
Date/Time                    : 2014-06-21T17:04
Latitude                     : 38.885507
Longitude                    : -76.5416
Date/Time 2                  : 2014-06-21T17:21
Latitude 2                   : 38.885507
Longitude 2                  : -76.5416
Depth                        : 2.4
TZ                           : UTC-05
Local time                   : 21-06-2014T12:04:00
Country, closest             : USA
Country, distance            : 456
BG province, closest, abbrev : NWCS
BG province, closest, desc   : Coastal - NW Atlantic Shelves Province
BG province, distance        : 0.035146239
LME, closest, desc           : Northeast U.S. Continental Shelf
LME, distance                : 212
Locality, site               : SERC Rhode River Maryland
Locality, region             : North Atlantic Ocean
URL ref                      : http://marineregions.org/gazetteer.php?p=details&id=1912
Biome                        : freshwater river biome
purl_biome                   : http://purl.obolibrary.org/obo/ENVO_01000253
Env feature                  : brackish estuary
purl_feature                 : http://purl.obolibrary.org/obo/ENVO_00002137
Material                     : brackish water
purl_material                : http://purl.obolibrary.org/obo/ENVO_00002019
Protocol Label               : NPL022
Quantity                     : 0.2;0.2;0.2;0.2;0.15;0.2
Container                    : Sterivex cartridge
Content                      : Not provided
Size-fraction, upper thresh  : No pre-filtration
Size-fraction, lower thresh  : 0.22
Treatment, chemicals         : None
Treatment, storage           : -20 Freezer
Temp                         : 26.8
Sal                          : 7.2
pH                           :
[PO4]3-                      :
[NO3]-                       :
POC                          :
[NO2]-                       :
DOC                          :
Plank nano/micro             :
PAR                          :
Cond                         :
PP C                         :
OXYGEN                       : 6.2
PON                          :
Plank meso/macro             :
Bact prod C                  :
DON                          :
[NH4]+                       :
Si(OH)4                      :
Turbidity                    :
Fluorometer                  : 37.6
Chl a                        :
```

The goal is to describe the columns using an ontology term from [an ontology file](./pmo_searchable_terms.tsv) with the following structure:

```
$ csvchk pmo_searchable_terms.tsv
// ****** Record 1 ****** //
PURL                                   : http://purl.obolibrary.org/obo/ENVO_3100030
PURL LABEL                             : acidity of water
MIXS WATER 4.0 STRUCTURED COMMENT NAME : ph
STANDARD UNIT PURL                     : http://purl.obolibrary.org/obo/UO_0000196
UNIT LABEL                             : pH
MIXS SPECIFIED UNIT                    : no
NOTES                                  :
```

For instance, the above term "pH" is found in the above OSD data as the column "pH".
The ultimate goal is to create a [Frictionless Datapackage](https://frictionlessdata.io/) where the fields are annotated with their ontology information, e.g.:

```
{
    "name": "pH",
    "type": "number",
    "format": "default",
    "rdfType": "http://purl.obolibrary.org/obo/ENVO_3100030",
    "pm:unitRdfType": "http://purl.obolibrary.org/obo/UO_0000196",
    "pm:source url": "https://doi.pangaea.de/10.1594/PANGAEA.854419",
    "pm:measurementSourceProtocolUrl": "https://www.microb3.eu/sites/default/files/deliverables/MB3_D4_3_PU.pdf"
}
```

## Associating data columns to ontology terms

The `purloiner.py` program is the first step to merge the "searchable terms" ontology information with a given data file like the above mentioned OSD sample file.
These are the program parameters:

```
$ ./purloiner.py -h
usage: purloiner.py [-h] -f FILE -o FILE [-O FILE] [-a FILE]

Add ontology terms

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Input file(s) (default: None)
  -o FILE, --ontology FILE
                        File of ontology terms (default: None)
  -O FILE, --outfile FILE
                        Output file (default: )
  -a FILE, --assoc_file FILE
                        Previous association file (default: None)
```

Here is how to run it to create the default output file (which is the input file + "_ontology", e.g., "osd_sample_ontology.tsv"):

```
./purloiner.py -o pmo_searchable_terms.tsv -f osd_sample.tsv
```

If you run this, you will be presented with a menu of the 70 fields present in the "osd_sample.tsv" file:

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Select a column                                                        │
  │                                                                         │
  │                                                                         │
  │    1 - Sample ID                                                        │
  │    2 - Sample label (BioSample)                                         │
  │    3 - Sample label (BioArchive)                                        │
  │    4 - Sample label (ENA)                                               │
  │    5 - URL file                                                         │
  │    6 - Campaign                                                         │
  │    7 - Site label                                                       │
  │    8 - Site number                                                      │
  │    9 - Event                                                            │
  │   10 - Device                                                           │
  │   11 - Comment OBJECTIVE                                                │
  │   12 - Comment PLATFORM                                                 │
  │   13 - Comment DEVICE REPORTED                                          │
  │   14 - Comment DESCRIPTION                                              │
  │   15 - URI                                                              │
  │   16 - Date/Time                                                        │
  │   17 - Latitude                                                         │
  │   18 - Longitude                                                        │
  │   19 - Date/Time 2                                                      │
  │   20 - Latitude 2                                                       │
  │   21 - Longitude 2                                                      │
  │   22 - Depth                                                            │
  │   23 - TZ                                                               │
  │   24 - Local time                                                       │
  │   25 - Country, closest                                                 │
  │   26 - Country, distance                                                │
  │   27 - BG province, closest, abbrev                                     │
  │   28 - BG province, closest, desc                                       │
  │   29 - BG province, distance                                            │
  │   30 - LME, closest, desc                                               │
  │   31 - LME, distance                                                    │
  │   32 - Locality, site                                                   │
  │   33 - Locality, region                                                 │
  │   34 - URL ref                                                          │
  │   35 - Biome                                                            │
  │   36 - purl_biome                                                       │
  │   37 - Env feature                                                      │
  │   38 - purl_feature                                                     │
  │   39 - Material                                                         │
  │   40 - purl_material                                                    │
  │   41 - Protocol Label                                                   │
  │   42 - Quantity                                                         │
  │   43 - Container                                                        │
  │   44 - Content                                                          │
  │   45 - Size-fraction, upper thresh                                      │
  │   46 - Size-fraction, lower thresh                                      │
  │   47 - Treatment, chemicals                                             │
  │   48 - Treatment, storage                                               │
  │   49 - Temp                                                             │
  │   50 - Sal                                                              │
  │   51 - pH                                                               │
  │   52 - [PO4]3-                                                          │
  │   53 - [NO3]-                                                           │
  │   54 - POC                                                              │
  │   55 - [NO2]-                                                           │
  │   56 - DOC                                                              │
  │   57 - Plank nano/micro                                                 │
  │   58 - PAR                                                              │
  │   59 - Cond                                                             │
  │   60 - PP C                                                             │
  │   61 - OXYGEN                                                           │
  │   62 - PON                                                              │
  │   63 - Plank meso/macro                                                 │
  │   64 - Bact prod C                                                      │
  │   65 - DON                                                              │
  │   66 - [NH4]+                                                           │
  │   67 - Si(OH)4                                                          │
  │   68 - Turbidity                                                        │
  │   69 - Fluorometer                                                      │
  │   70 - Chl a                                                            │
  │   71 - Exit                                                             │
  │                                                                         │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

Choose the number of a field you wish to annotate, e.g., "51" for "pH" and you will next be presented with a list of 87 ontology terms.
Pick the term you wish to associate, e.g., "1" for "acidity of water (ENVO_3100030)":

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Select ontology term for "pH"                                          │
  │                                                                         │
  │                                                                         │
  │    1 - acidity of water (ENVO_3100030)                                  │
  │    2 - alkalinity of water (PMO_00000139)                               │
  │    3 - aquatic sample maximum filter fractionatio... (PMO_00000023)     │
  │    4 - aquatic sample minimum filter fractionatio... (PMO_00000022)     │
  │    5 - atmospheric wind speed (ENVO_01001362)                           │
  │    6 - autotrophic organism biomass carbon aggreg... (PMO_00000163)     │
  │    7 - biome (ENVO_00000428)                                            │
  │    8 - concentration of 19'-butanoyloxyfucoxanthi... (PMO_00000156)     │
  │    9 - concentration of 19'-hexanoyloxyfucoxanthi... (PMO_00000157)     │
  │   10 - concentration of Adenosine 5-triphosphate ... (ENVO_3100001)     │
  │   11 - concentration of alloxanthine in water (ENVO_3100002)            │
  │   12 - concentration of ammonium in water (ENVO_3100004)                │
  │   13 - concentration of bacteriochlorophyll a in ... (ENVO_3100005)     │
  │   14 - concentration of bromide in liquid water (PMO_00000186)          │
  │   15 - concentration of calcium(2+) in liquid water (PMO_00000179)      │
  │   16 - concentration of carbon dioxide in liquid ... (PMO_00000174)     │
  │   17 - concentration of carbonate in liquid water (PMO_00000175)        │
  │   18 - concentration of carotene in water (ENVO_3100007)                │
  │   19 - concentration of chloride in water (ENVO_09000019)               │
  │   20 - concentration of chlorophyll a in water (ENVO_3100008)           │
  │   21 - concentration of chlorophyll b in water (ENVO_3100009)           │
  │   22 - concentration of chlorophyll in water (ENVO_3100036)             │
  │   23 - concentration of chlorophyllide a in water (ENVO_3100010)        │
  │   24 - concentration of divinyl chlorophyll a in ... (ENVO_3100012)     │
  │   25 - concentration of divinyl chlorophyll b in ... (ENVO_3100013)     │
  │   26 - concentration of fucoxanthin in water (ENVO_3100014)             │
  │   27 - concentration of hydrogen sulfide in water (ENVO_3100017)        │
  │   28 - concentration of hydrogencarbonate in liqu... (PMO_00000176)     │
  │   29 - concentration of lutein in water (ENVO_3100019)                  │
  │   30 - concentration of magnesium(2+) in liquid w... (PMO_00000180)     │
  │   31 - concentration of manganese(2+) in liquid w... (PMO_00000184)     │
  │   32 - concentration of neoxanthin in water (ENVO_3100021)              │
  │   33 - concentration of nitrate and nitrite in water (PMO_00000018)     │
  │   34 - concentration of nitrate in water (ENVO_3100022)                 │
  │   35 - concentration of nitrite in water (ENVO_3100023)                 │
  │   36 - concentration of oxygen in water (ENVO_09200021)                 │
  │   37 - concentration of peridinin in water (ENVO_3100025)               │
  │   38 - concentration of phosphate in water (ENVO_3100026)               │
  │   39 - concentration of potassium(1+) in liquid w... (PMO_00000181)     │
  │   40 - concentration of silicic acid in water (ENVO_3100034)            │
  │   41 - concentration of sodium(1+) in liquid water (PMO_00000182)       │
  │   42 - concentration of sulfate in liquid water (PMO_00000183)          │
  │   43 - concentration of urea in liquid water (PMO_00000173)             │
  │   44 - concentration of violaxanthin in water (ENVO_3100028)            │
  │   45 - concentration of zeaxanthin in water (ENVO_3100029)              │
  │   46 - conductivity of water (ENVO_09200018)                            │
  │   47 - depth of water (ENVO_3100031)                                    │
  │   48 - dissolved inorganic carbon (PMO_00000142)                        │
  │   49 - dissolved organic carbon (PMO_00000102)                          │
  │   50 - dissolved organic nitrogen (PMO_00000111)                        │
  │   51 - enumeration of heterotrophic prokaryote ag... (PMO_00000162)     │
  │   52 - enumeration of picoeukaryote aggregation (PMO_00000161)          │
  │   53 - enumeration of Prochlorococcus aggregation (PMO_00000159)        │
  │   54 - enumeration of prokaryote aggregation (PMO_00000185)             │
  │   55 - enumeration of Synechococcus aggregation (PMO_00000160)          │
  │   56 - environmental feature (ENVO_00002297)                            │
  │   57 - environmental material (ENVO_00010483)                           │
  │   58 - latitude coordinate measurement datum (OBI_0001620)              │
  │   59 - latitude coordinate measurement datum start (PMO_00000076)       │
  │   60 - latitude coordinate measurement datum stop (PMO_00000079)        │
  │   61 - liquid water salinity (PMO_00000014)                             │
  │   62 - longitude coordinate measurement datum (OBI_0001621)             │
  │   63 - longitude coordinate measurement datum start (PMO_00000077)      │
  │   64 - longitude coordinate measurement datum stop (PMO_00000078)       │
  │   65 - mass density of liquid water (PMO_00000191)                      │
  │   66 - mesoplankton and macroplankton aggregate (PMO_00000114)          │
  │   67 - nanoplankton and microplankton aggregate (PMO_00000101)          │
  │   68 - particulate carbon (PMO_00000150)                                │
  │   69 - particulate nitrogen (PMO_00000151)                              │
  │   70 - particulate organic carbon (PMO_00000103)                        │
  │   71 - particulate organic nitrogen (PMO_00000112)                      │
  │   72 - particulate phosphorus (PMO_00000153)                            │
  │   73 - particulate silica (PMO_00000165)                                │
  │   74 - photosynthetically active electromagnetic ... (PMO_00000015)     │
  │   75 - potential density (PMO_00000021)                                 │
  │   76 - potential temperature (PMO_00000020)                             │
  │   77 - pressure of water (ENVO_3100033)                                 │
  │   78 - primary productivity carbon (PMO_00000108)                       │
  │   79 - prokaryote derived carbon (PMO_00000116)                         │
  │   80 - prokaryotic leucine production  (PMO_00000189)                   │
  │   81 - specimen collection time measurement datum (OBI_0001619)         │
  │   82 - specimen collection time measurement datum... (PMO_00000008)     │
  │   83 - specimen collection time measurement datum... (PMO_00000009)     │
  │   84 - specimen identifier assigned by sequencing... (OBI_0001901)      │
  │   85 - stellar radiation (ENVO_01001211)                                │
  │   86 - temperature of water (ENVO_09200014)                             │
  │   87 - turbidity of water (PMO_00000121)                                │
  │   88 - Exit                                                             │
  │                                                                         │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

Repeat the column/term association step for as many columns in the input file as you like.
Choose the "Exit" option from the column selection menu to write the output file.

## Editing an existing association file

It is expected that a user would want to edit an existing column/assocation file.
To do so using the "osd_sample_ontology.tsv" we created above and assuming we'll want to overwrite it (otherwise give it a different `--outfile`):

```
$ ./purloiner.py -f osd_sample.tsv -o pmo_searchable_terms.tsv -a osd_sample_ontology.tsv
Output file "osd_sample_ontology.tsv" exists. Overwrite? [yN] y
```

Now you can see, for instance, that the column "pH" shows that it is currently associated to the term "ENVO_3100030":

```
  │   51 - pH => "ENVO_3100030" (acidity of water)                          │
```

Choose "51" if you wish to change this.
As before, when you are done creating the associations, "Exit" from the first (column) menu to write the output file.

## Creating a data package

Once you have the column/ontology association file, you can create a Frictionless Datapackage.
Let's use the existing [OSD ontology file](https://github.com/hurwitzlab/planet-microbe-datapackages/blob/master/OSD/ontology/osd.tsv) as an example:

```
$ csvchk osd.tsv
// ****** Record 1 ****** //
parameter                      : Sample ID
rdf type purl label            : centrally registered identifier
rdf type purl                  : http://purl.obolibrary.org/obo/IAO_0000578
pm:searchable                  : FALSE
units label                    :
units purl                     :
measurement source purl label  :
measurement source purl        :
pm:measurement source protocol : https://www.microb3.eu/sites/default/files/deliverables/MB3_D4_3_PU.pdf
pm:source url                  : https://doi.pangaea.de/10.1594/PANGAEA.854419
frictionless type              : string
frictionless format            :
```

The [mk_pkg.py](./mk_pkg.py) can assist you in making a datapackage.
Here are the program's parameters:

```
$ ./mk_pkg.py -h
usage: mk_pkg.py [-h] [-d FILE [FILE ...]] [-o FILE] [-O FILE] [-m [missing [missing ...]]]
                 [-f]

Make datapackage

optional arguments:
  -h, --help            show this help message and exit
  -d FILE [FILE ...], --data FILE [FILE ...]
                        Input file (default: None)
  -o FILE, --ontology FILE
                        Ontology file (default: None)
  -O FILE, --outfile FILE
                        Output file (default: datapackage.json)
  -m [missing [missing ...]], --missing [missing [missing ...]]
                        Missing value (default: None)
  -f, --force           Force overwrite of existing --outfile (default: False)
```

Using the above column/association file, I can create a datapackage for the OSD like so:

```
./mk_pkg.py -d osd_sample.tsv -o osd.tsv -m "nd"
```

By default, this will create an output file called "datapackage.json".

Alternatively, there is also the program [schema_tsv_to_json.py](https://github.com/hurwitzlab/planet-microbe-scripts/blob/master/scripts/schema_tsv_to_json.py) that can create a similar datapackage.
To run it using the above "osd.tsv" file:

```
$ /path/to/schema_tsv_to_json.py < osd.tsv > datapackage.json
```

## See Also

* https://frictionlessdata.io/
* https://pypi.org/project/datapackage/
* https://github.com/hurwitzlab/planet-microbe-datapackages

## Author

Ken Youens-Clark <kyclark@arizona.edu>
