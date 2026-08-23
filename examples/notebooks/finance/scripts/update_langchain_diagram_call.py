"""Make the executable LangChain call explicit in the public diagram."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
NOTEBOOK = HERE / "BeliefLens_LangChain_measurement.ipynb"


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text())
    workflow_cell = notebook["cells"][12]
    workflow_source = "".join(workflow_cell["source"])
    workflow_old = "chain = RunnableLambda(observe) | RunnableLambda(calibrate) | RunnableLambda(gate)"
    workflow_new = "belieflens = RunnableLambda(calibrate)\nchain = RunnableLambda(observe) | belieflens | RunnableLambda(gate)"
    if workflow_old in workflow_source:
        workflow_source = workflow_source.replace(workflow_old, workflow_new)
    elif workflow_new not in workflow_source:
        raise RuntimeError("expected LangChain workflow source was not found")
    workflow_cell["source"] = workflow_source.splitlines(keepends=True)
    workflow_cell["outputs"] = []
    workflow_cell["execution_count"] = None

    cell = notebook["cells"][14]
    source = "".join(cell["source"])
    old = """a.text(.02,.92,'LANGCHAIN',color='#53d2c0',size=16,weight='bold')
a.text(.02,.83,'chain = observe | calibrate | gate',color='white',size=14,family='monospace')
"""
    prior = """a.text(.02,.92,'MINIMAL LANGCHAIN CALL',color='#53d2c0',size=16,weight='bold')
a.text(.02,.83,'belieflens = RunnableLambda(',color='white',size=12.5,family='monospace')
a.text(.02,.77,'    apply_frozen_calibration)',color='white',size=12.5,family='monospace')
a.text(.02,.69,'result = belieflens.invoke(record)',color='#ffb347',size=12.5,weight='bold',family='monospace')
"""
    new = """a.text(.02,.92,'MINIMAL LANGCHAIN CALL',color='#53d2c0',size=16,weight='bold')
a.text(.02,.84,'belieflens = RunnableLambda(calibrate)',color='white',size=11.5,family='monospace')
a.text(.02,.77,'chain = observe | belieflens | gate',color='white',size=11.5,family='monospace')
a.text(.02,.69,'result = chain.invoke(record)',color='#ffb347',size=12.5,weight='bold',family='monospace')
"""
    if old in source:
        source = source.replace(old, new)
    elif prior in source:
        source = source.replace(prior, new)
    elif new not in source:
        raise RuntimeError("expected LangChain diagram source was not found")
    trace_old = """b.text(.02,.92,'JAEGER-COMPATIBLE TRACE',color='#53d2c0',size=16,weight='bold')
b.text(.02,.84,'service: belieflens-langchain-local',color='#d4deec',size=10,family='monospace')
order=['langchain.workflow','observe.language_probabilities','measure.semantic_calibration','governance.acceptance_gate']
colors=['#367fb6','#53d2c0','#ffb347','#e98383']
for i,(name,col) in enumerate(zip(order,colors)):
 y=.68-i*.14; b.text(.02+(.03 if i else 0),y+.025,name,color='white',size=9.5,family='monospace')
 b.add_patch(FancyBboxPatch((.48+i*.035,y),.40-i*.045,.065,boxstyle='round,pad=.006',facecolor=col,edgecolor='white',lw=.7))
"""
    trace_new = """b.text(.02,.92,'RECORDED OPENTELEMETRY TRACE',color='#53d2c0',size=15,weight='bold')
b.text(.02,.84,'service: belieflens-langchain-local',color='#d4deec',size=10,family='monospace')
order=['langchain.workflow','observe.language_probabilities','measure.semantic_calibration','governance.acceptance_gate']
colors=['#367fb6','#53d2c0','#ffb347','#e98383']
span_by_name={s.name:s for s in spans}
for i,(name,col) in enumerate(zip(order,colors)):
 y=.68-i*.14
 duration=(span_by_name[name].end_time-span_by_name[name].start_time)/1e6
 b.text(.02+(.03 if i else 0),y+.025,f'{name}  {duration:.2f} ms',color='white',size=8.8,family='monospace')
 b.add_patch(FancyBboxPatch((.55+i*.025,y),.34-i*.035,.065,boxstyle='round,pad=.006',facecolor=col,edgecolor='white',lw=.7))
"""
    trace_prior = trace_new
    if trace_old in source:
        source = source.replace(trace_old, trace_new)
    elif trace_prior not in source:
        raise RuntimeError("expected trace diagram source was not found")
    source = source.replace(
        "fig.suptitle('A calibrated BeliefLens measurement inside LangChain',color='white',size=20,weight='bold')",
        "fig.suptitle('BeliefLens invoked from LangChain—and traced',color='white',size=20,weight='bold')",
    )
    cell["source"] = source.splitlines(keepends=True)
    cell["outputs"] = []
    cell["execution_count"] = None
    NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
