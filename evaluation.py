from __future__ import annotations

from mqt import qfr
from mqt.bench import get_benchmark

import itertools
import pandas as pd
from datetime import datetime

class Evaluation:
    def __init__(self, benchlist: list[str], qbit_range: range, args: list[dict], abs_level: str="alg", verbose: bool=False) -> None:
        if qbit_range.start < 2 or qbit_range.stop > 130:
            print("too many or few quibits")
            raise Exception
        self._benchlist = benchlist
        self._qbit_range = qbit_range
        self._abs_level = abs_level
        self._args = args
        self._list_results = dict()
        self._verbose = verbose      

    def run_evaluation(self, check_equality = False) -> None:
        i = 1
        num_combs = len(self._qbit_range)*len(self._benchlist)*len(self._args)
        for nqbit, benchname in itertools.product(self._qbit_range, self._benchlist):
            try:
                qc = get_benchmark(benchname, self._abs_level, nqbit)   
                qc.remove_final_measurements()         
            except Exception as e:
                i+=len(self._args)
                print('Exception in get_benchmark:\n', e)
                continue
            mats = []
            for arg in self._args:
                if self._verbose:
                    print(f"----------------{i}/{num_combs} name: {benchname}, size: {nqbit}, label: {arg['label']}----------------")
                try:
                    i+=1
                    results = qfr.construct(qc, store_dd=arg['store_dd'], store_matrix=arg['store_matrix'], reduceT=arg['reduceT'])
                    
                    if check_equality:
                        mat = results['functionality']['matrix']
                        if not mat in mats:
                            mats.append(mat)

                    newres = {'label': arg['label'],**results['circuit'], **results['statistics']}
                    # newres = dict()
                    # newres['name'] = results['circuit']['name']
                    
                    # newres['n_qubits'] = results['circuit']['n_qubits']
                    # newres['n_gates'] = results['circuit']['n_qubits']
                    # newres['final_nodecount-'+arg['label']] = results['statistics']['final_nodecount']
                    # newres['construction_time-'+arg['label']] = results['statistics']['construction_time']
                        
                    if not arg['label'] in self._list_results:
                        self._list_results[arg['label']] = []
                    self._list_results[arg['label']].append(newres)
                except Exception as e:
                    print('Exception in qfr.construct:\n', e)
                    print(e)
                    continue

            if check_equality:
                if len(mats)>1:
                    print("!not equal!")

    def export_to_excel(self, dirpath: str) -> None:
        if self._list_results:
            now = datetime.now()
            file_name = datetime.strftime(now, "%Y%m%d_%H%M%S")
            with pd.ExcelWriter(dirpath+file_name+'.xlsx', engine="openpyxl") as writer:
                column = 0
                for x in self._list_results:
                    dataframe_results = pd.DataFrame.from_dict(self._list_results[x])
                    dataframe_results.to_excel(writer, sheet_name="Sheet_1", startcol=column, index=False)
                    column += len(dataframe_results.columns)+1




qbit_interval = range(3,7)

scalable_benchmarks = ["ae", "dj", "grover-noancilla", "grover-v-chain", "ghz",
                        "graphstate", "portfolioqaoa", "portfoliovqe", "qaoa", "qft",
                          "qftentangled", "qgan", "qpeexact", "qpeinexact", "qwalk-noancilla",
                            "qwalk-v-chain", "realamprandom", "su2random", "twolocalrandom",
                              "vqe", "wstate"]

params = [{'label': 'regular', 'store_dd': False, 'store_matrix': False, 'reduceT': False},
          {'label': 'reduceT', 'store_dd': False, 'store_matrix': False, 'reduceT': True}]

params2 = [{'label': 'regular', 'store_dd': False, 'store_matrix': True, 'reduceT': False},
          {'label': 'reduceT', 'store_dd': False, 'store_matrix': True, 'reduceT': True}]

QFR_Eval = Evaluation(['grover-v-chain'], qbit_interval, params2, verbose=True)

QFR_Eval.run_evaluation(check_equality=False)

QFR_Eval.export_to_excel("test/evaluation/excel/")

# # scalable_benchmarks = ["grover-noancilla", "grover-v-chain", "ghz",
# #                         "graphstate", "portfolioqaoa", "portfoliovqe", "qaoa", "qft",
# #                           "qftentangled", "qgan", "qpeexact", "qpeinexact", "qwalk-noancilla",
# #                             "qwalk-v-chain", "realamprandom", "su2random", "twolocalrandom",
# #                               "vqe", "wstate"]

# abstraction_level = "alg"

# verbose = True


# for benchname in scalable_benchmarks:
#     for nqbit in range(qbit_interval[0],qbit_interval[1]+1):

#         try:
#             qc = get_benchmark(benchname, abstraction_level, nqbit)   
#             qc.remove_final_measurements()         
#             if verbose:
#                 print("----------------test {} with circuit size {}----------------".format(benchname, nqbit))

        
#             resultsN = qfr.construct(qc, store_dd=False, store_matrix=False, reduceT=False)
#             numNodesN = resultsN['statistics']['final_nodecount']
#             # matN = resultsN['functionality']['matrix']
#             # ddN = resultsN['functionality']['dd']

#             resultsT = qfr.construct(qc, store_dd=False, store_matrix=False, reduceT=True)
#             numNodesT = resultsT['statistics']['final_nodecount']
#             # matT = resultsT['functionality']['matrix']
#             # ddT = resultsT['functionality']['dd']
#             failed = False
#         except Exception as e:
#             print(benchname)
#             print(e)
#             continue
        
#         if numNodesT<numNodesN:
#             print(numNodesN,"->",numNodesT)

#         # if matN == matT and numNodesT<=numNodesN:
#         #     print("\tprobably passed")
#         #     if numNodesT<numNodesN:
#         #         print(numNodesN,"->",numNodesT)
#         # else:
#         #     print("\tfailed")
#         #     failed = True

#         if(failed):
#             print("--normal:")
#             print('#nodes:',numNodesN)
#             print(ddN)
#             for c in matN:
#                 print(c)
#             print("--transpose:")
#             print('#nodes:',numNodesT)
#             print(ddT)
#             for c in matT:
#                 print(c)
    