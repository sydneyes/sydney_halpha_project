# Julian Date converter
This submodule is to convert from Gregorian calenderdates or Julian Calender dates
to the julian date format. This is done using 

## Overview
Simple conversions between Julian Dates and Julian/Gregorian calendar dates, 
supporting ancient dates (BCE). You can check `juliandate's` calculations 
against the US Naval Observeratory's [Julian Date Converter](https://aa.usno.navy.mil/data/JulianDate).

## Usage 
 _Converting from Julian Date to Gregorian or Julian Calendar Date
A Julian Date such as `2440423.345486` indicates the number of days (and fractional part) 
since noon January 1, 4713 BCE (Julian) or November 24, 4714 BCE (Gregorian), 
a system proposed by [Joseph Scaliger](https://en.wikipedia.org/wiki/Joseph_Justus_Scaliger)
 in 1583. `2440423` is the number of full days, 
and the fractional part, `0.345486` indicates that a little more than a third of a 
day has passed (since noon).

## Reference


## Sources
The conversion formulas are taken from pages 604 and 606 of:
Seidelmann, P.K. 2006 _Explanatory Supplement to the Astronomical Almanac: A Revision to the 
Explanatory Supplement to the Astronomical Ephemeris and the American Ephemeris and Nautical Almanac._ 
Sausalito, University Science Books.
and pages 617–619 of:

Urban, Sean E., and P. Kenneth Seidelmann, eds. _Explanatory Supplement to the Astronomical Almanac_. 
3. ed. Mill Valley, Calif: University Science Books, 2012.


## Math
### Converting Julian calendar date to Julian Day Number
To convert a Gregorian calendar date $\mathbf{D/M/Y}$ we use the formula from [wikipedia](https://en.wikipedia.org/wiki/Julian_day). The algorithm is valid for all (possibly proleptic) Gregorian calendar dates after November 23, −4713. Divisions are integer divisions towards zero; fractional parts are ignored.

$$ 
\mathbf{JDN} = (1461 \cdot (\mathbf{Y} + 4800 + (\mathbf{M} − 14)/12))/4 +(367 \cdot (\mathbf{M} − 2 − 12 \cdot ((\mathbf{M} − 14)/12)))/12 − (3 \cdot ((\mathbf{Y} + 4900 + (\mathbf{M} - 14)/12)/100))/4 + \mathbf{D} − 32075
$$

### Converting Julian calendar date to Julian Day Number
The algorithm is valid for all (possibly proleptic) Julian calendar years ≥ −4712, that is, for all JDN ≥ 0. Divisions are integer divisions, fractional parts are ignored.

$$
\mathbf{JDN} = 367 \cdot \mathbf{Y} − (7 \cdot (\mathbf{Y} + 5001 + (\mathbf{M} − 9)/7))/4 + (275 \cdot \mathbf{M})/9 + \mathbf{D} + 1729777
$$



## Aknowledgement
This tool is based on modified source code originally available at a public 
repository https://github.com/seanredmond/juliandate from the user 
[Sean Redmond](https://github.com/seanredmond). 
We thank the original contributors for their foundational work!


