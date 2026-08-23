"""Make the executable LangChain call explicit in the public diagram."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
NOTEBOOK = HERE / "BeliefLens_LangChain_measurement.ipynb"


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text())
    record_cell = notebook["cells"][8]
    record_source = "".join(record_cell["source"])
    record_old = "record = {\n    'observation_id': archived['scenario_id'],"
    record_new = "record = {\n    'measurement_id': 'spy-regime-v5:example-001',\n    'observation_id': archived['scenario_id'],"
    if record_old in record_source:
        record_source = record_source.replace(record_old, record_new)
    elif record_new not in record_source:
        raise RuntimeError("expected example record source was not found")
    record_cell["source"] = record_source.splitlines(keepends=True)
    record_cell["outputs"] = []
    record_cell["execution_count"] = None

    workflow_cell = notebook["cells"][12]
    workflow_source = "".join(workflow_cell["source"])
    workflow_old = "chain = RunnableLambda(observe) | RunnableLambda(calibrate) | RunnableLambda(gate)"
    workflow_new = "belieflens = RunnableLambda(calibrate)\nchain = RunnableLambda(observe) | belieflens | RunnableLambda(gate)"
    if workflow_old in workflow_source:
        workflow_source = workflow_source.replace(workflow_old, workflow_new)
    elif workflow_new not in workflow_source:
        raise RuntimeError("expected LangChain workflow source was not found")
    if "span.set_attribute('measurement.id'" not in workflow_source:
        workflow_source = workflow_source.replace(
            "span.set_attribute('observation.id', str(value['observation_id']))",
            "span.set_attribute('measurement.id', str(value['measurement_id']))\n        span.set_attribute('observation.id', str(value['observation_id']))",
        )
        workflow_source = workflow_source.replace(
            "span.set_attribute('measurement.leading_state', out['leading_state'])",
            "span.set_attribute('measurement.id', str(value['measurement_id']))\n        span.set_attribute('measurement.leading_state', out['leading_state'])",
        )
        workflow_source = workflow_source.replace(
            "span.set_attribute('governance.route', next_route)",
            "span.set_attribute('measurement.id', str(value['measurement_id']))\n        span.set_attribute('governance.route', next_route)",
        )
    workflow_source = workflow_source.replace(
        "with tracer.start_as_current_span('langchain.workflow'):\n    traced_result = chain.invoke(record)",
        "with tracer.start_as_current_span('langchain.workflow') as workflow_span:\n    workflow_span.set_attribute('measurement.id', record['measurement_id'])\n    traced_result = chain.invoke(record)",
    )
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
    current = """a.text(.02,.92,'MINIMAL LANGCHAIN CALL',color='#53d2c0',size=16,weight='bold')
a.text(.02,.84,'belieflens = RunnableLambda(calibrate)',color='white',size=11.5,family='monospace')
a.text(.02,.77,'chain = observe | belieflens | gate',color='white',size=11.5,family='monospace')
a.text(.02,.69,'result = chain.invoke(record)',color='#ffb347',size=12.5,weight='bold',family='monospace')
"""
    new = """a.text(.02,.92,'MINIMAL LANGCHAIN CALL',color='#53d2c0',size=16,weight='bold')
a.text(.02,.84,'belieflens = RunnableLambda(calibrate)',color='white',size=11.5,family='monospace')
a.text(.02,.77,'chain = observe | belieflens | gate',color='white',size=11.5,family='monospace')
a.text(.02,.69,'record["measurement_id"] =',color='#d4deec',size=10.5,family='monospace')
a.text(.02,.64,'    "spy-regime-v5:example-001"',color='#d4deec',size=10.5,family='monospace')
a.text(.02,.57,'result = chain.invoke(record)',color='#ffb347',size=12.5,weight='bold',family='monospace')
"""
    if old in source:
        source = source.replace(old, new)
    elif prior in source:
        source = source.replace(prior, new)
    elif current in source:
        source = source.replace(current, new)
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
    source = source.replace(
        "items=[(.03,'observe','phrase probabilities'),(.37,'calibrate','frozen semantic map'),(.71,'gate','route action')]",
        "items=[(.03,'observe','phrase probabilities'),(.37,'BeliefLens','semantic calibration'),(.71,'gate','route action')]",
    )
    source = source.replace("(x,.48),.25,.18", "(x,.35),.25,.15")
    source = source.replace("x+.125,.59", "x+.125,.445").replace("x+.125,.52", "x+.125,.385")
    source = source.replace("(y,.57),(x,.57)", "(y,.425),(x,.425)")
    source = source.replace("a.text(.03,.31", "a.text(.03,.245").replace("a.text(.03,.22", "a.text(.03,.165")
    if "b.text(.02,.79,'measurement: '" not in source:
        source = source.replace(
            "b.text(.02,.84,'service: belieflens-langchain-local',color='#d4deec',size=10,family='monospace')",
            "b.text(.02,.84,'service: belieflens-langchain-local',color='#d4deec',size=10,family='monospace')\n"
            "b.text(.02,.79,'measurement: '+record['measurement_id'],color='#ffb347',size=9.5,family='monospace')",
        )
    cell["source"] = source.splitlines(keepends=True)
    cell["outputs"] = []
    cell["execution_count"] = None
    NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
