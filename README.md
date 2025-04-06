# Cubing Algs

Python module providing tools manipulating cubing algorythms.

## Example

``` python
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.transform.size import expand_moves

algo = parse_moves("F R U2 F'")
print(algo.transform(mirror_moves, expand_moves))
# F U U R' F'
```
