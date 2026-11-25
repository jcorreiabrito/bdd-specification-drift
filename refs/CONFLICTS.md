# Reference merge report

- Input rows: 85
- Unique works (by DOI): 78
- Input files: verified.bdd.csv, verified.decay.csv, verified.intersect.csv, verified.mutation.csv

## Cross-facet duplicates resolved

- `10.1007/s11219-023-09616-6` also cited as mutation:Leotta2023Mutta, bdd:leotta2024mutta
- `10.1016/j.jss.2023.111749` also cited as bdd:binamungu2023mapping
- `10.1109/icse.2017.61` also cited as mutation:Chekam2017FaultRevelation
- `10.1109/saner.2018.8330207` also cited as bdd:binamungu2018maintaining
- `10.1145/1062455.1062530` also cited as intersect:andrews2005ismutation
- `10.1145/3350768.3351301` also cited as bdd:oliveira2019howtoevaluate

## Field conflicts to adjudicate

- DOI `10.1109/saner.2018.8330207` field `venue`: kept `2018 IEEE 25th International Conference on Software Analysis Evolution and Reengineering (SANER)` (from intersect) vs `IEEE International Conference on Software Analysis Evolution and Reengineering (SANER)` (from bdd:binamungu2018maintaining)
- DOI `10.1007/s11219-023-09616-6` field `venue`: kept `Software Quality Journal` (from intersect) vs `Software Quality Journal 32` (from mutation:Leotta2023Mutta)
- DOI `10.1007/s11219-023-09616-6` field `year`: kept `2023` (from intersect) vs `2024` (from bdd:leotta2024mutta)
- DOI `10.1145/1062455.1062530` field `venue`: kept `ICSE 2005` (from mutation) vs `Proceedings of the 27th International Conference on Software Engineering (ICSE)` (from intersect:andrews2005ismutation)
- DOI `10.1109/icse.2017.61` field `venue`: kept `Proceedings of the 39th International Conference on Software Engineering (ICSE)` (from intersect) vs `ICSE 2017` (from mutation:Chekam2017FaultRevelation)