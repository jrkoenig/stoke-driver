STOKE Driver
===

Introduction
------------
This code runs STOKE many times, to evaluate performance of the search procedure. Here we are only concerned with synthesis of programs, not optimizations, but support for the later isn't much more complicated. This code supports both synthesizing locally on one machine and parallelizing the synthesis across multiple machines.


Getting Started
---

The simplest way to run the driver is to invoke `python localsynth.py`. This will generate `results.jsonl` and `logs/` in the current directory. This requires STOKE to be on your `PATH`.

The other way to run the driver is to use a PostgreSQL database to distribute the workload amongst multiple servers. The setup for this is not yet documented.

Structure
---

- Setup
  - `dbsetup.py` sets up the PostgreSQL database.
- Launching
  - `localsynth.py` Synthesizes examples locally, useful for testing.
  - `submitseries.py` Sends a series (set of STOKE runs) to the queue.
  - `launch.sh` Sets up paths and launches `serversynth.py`, which runs the synthesis worker.
- Output
  - `status.py` Prints information about all the series and the synthesis queue.
  - `resultsummary.py` Allows inspection of the results.
- `gulwani/` is the input data for the Gulwani bitwise program examples. See formats below.
- Dependencies
  - `pg.py` Wraps the database in a more convenient API.
  - `pgmq.py` Handles the queue messaging layer, built on PostgreSQL.
  - `pmap.py` Implements a parallel map using python threads.
  - `synthtarget.py` Defines a STOKE target, which is live-in/-out + testcases + target asm.
  - `targetbuilder.py` Generates STOKE targets from C files. Parses `gulwani/gulwani.json`.
  - `stokerunner.py` Sets up STOKE and runs it on the given target.
  - `stokeversion.py` Contains logic for building multiple versions of STOKE and keeping them isolated.


Formats
---
#### Example C++ code
This represents synthesis targets as a C++ file. Metadata is in a .json file. The JSON file is an array of entries. Each entry looks like:

```json
{ "src_file": "p01.cc",
  "func": "p01",
  "argc": 1,
  "retc": 1,
  "use_mem": false,
  "name": "p01",
  "tags": ["bit-manip", "gulwani"]}
```
The important elements are `name`, `src_file`, and `argc`/`retc`/`use_mem`. The name is used to identify the target uniquely. `src_file` gives the location of the source C++ file. The last three give the ABI for this function. `argc` is the number of arguments (only general purpose are supported). `retc` is the number of returns (only 0 or 1). `use_mem` tells whether memory is live out and whether to propose memory operations in the search (this is the one element where the target affects the search).

Tags are deprecated, and `func` tells which function is the target.

The C++ file looks like:

``` cpp
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

extern \"C"  {
  int32_t p01(int32_t x) {
    int32_t o1 = x - 1;
    return x & o1;
  }
}

int main() {
  srand(244245);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p01(i));
  }
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p01(rand()));
  }
  return 0;
}
```

The function to synthesize is `extern "C"`-ed so that its name is not mangled. The testcases are executed by `main()`.

TODO: Include CPU flags, because these control acceptable programs and thus the class of programs to search for (rather than how to search for them).

#### Synth Target
The `targetbuilder` takes C++ code and turns it into a SynthTarget python object. This contains the important ABI data from the example format, plus generated testcases and the assembly of the target. This can be serialized into a JSON document. This JSON document is only tens of KB, even if there are many testcases, due to compression. The serialization is used to store targets in the synth queue.

#### JSONL
This format contains summaries of the results of running a series of STOKE runs. Each line is a json encoded value:

    {"name":"p03","iters":544,"elapsed":0.0285951,"cost":0, "limit":20000000,"correct":true,"asm":".p03:\nxorq %rax, %rax..."}
        
There are no newlines within the JSON document, thus allowing a very simple python parsing routine:

```python
for l in open("results.jsonl"):
    data = json.loads(l)
    # use data['name'], data['elapsed'], etc.
```

The keys are:

- `name` gulwani example, `p01`, `p02`, etc.
- `iters` total iterations of the search. Equal to limit if the search timed out.
- `elapsed` search time in seconds.
- `cost` the cost at the end of the search. Zero if and only if the search ended early. Always corresponds to the cost of the `asm` program.
- `limit` the timeout limit. Always 20M iterations.
- `correct` whether the cost is zero. No verification is performed!
- `asm` the assembly of the final program
