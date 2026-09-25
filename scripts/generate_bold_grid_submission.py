"""Generate and validate a TACVU2 ZIP using the tested Bold grid-cleanup notebook.
Reads only manifest, questions, OCR and page images from the selected test split.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def validate(predictions, questions, manifests):
    expected = [q['question_id'] for q in questions]
    actual = [p['question_id'] for p in predictions]
    assert len(expected) == len(set(expected)), 'Duplicate IDs in questions'
    assert len(actual) == len(set(actual)), 'Duplicate prediction IDs'
    assert set(actual) == set(expected), 'Missing or extra question IDs'
    documents = {m['id']:m for m in manifests}
    qdoc = {q['question_id']:q['document_id'] for q in questions}
    for p in predictions:
        assert set(p) == {'question_id', 'answer', 'evidence'}, p['question_id']
        assert isinstance(p['question_id'],str)
        assert isinstance(p['answer'],str) and p['answer'].strip(), p['question_id']
        assert isinstance(p['evidence'],list)
        for e in p['evidence']:
            assert set(e) == {'page','bbox'}, p['question_id']
            assert type(e['page']) is int and 1 <= e['page'] <= len(documents[qdoc[p['question_id']]]['image_paths'])
            assert isinstance(e['bbox'],list) and len(e['bbox']) == 4
            assert all(type(v) in (int,float) and math.isfinite(v) for v in e['bbox'])
            x1,y1,x2,y2=e['bbox']
            assert 0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1, p['question_id']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,required=True,help='Directory containing manifest.jsonl and questions.jsonl')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--expected-questions',type=int,required=True)
    ap.add_argument('--checkpoint',type=Path,default=ROOT/'artifacts/models/bold_pair_resnet18.pt')
    args=ap.parse_args()
    data=args.data.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    checkpoint=args.checkpoint.resolve()
    source=ROOT/'notebooks/submission_pipeline_bold_grid_clean.ipynb'
    nb=json.loads(source.read_text(encoding='utf-8'))
    b={'ROOT':ROOT,'__name__':'submission_bold_grid_clean'}
    exec(''.join(nb['cells'][3]['source']),b)
    b['torch'].set_num_threads(2)
    b['torch'].use_deterministic_algorithms(True,warn_only=True)
    b['DEVICE']=b['torch'].device('cpu')
    for i,c in enumerate(nb['cells']):
        if c['cell_type']=='code' and i not in {3,5,45,47}:
            exec(compile(''.join(c['source']),f'notebook_cell_{i}','exec'),b)
    b['BOLD_PAIR_CHECKPOINT']=checkpoint
    if not checkpoint.is_file():raise FileNotFoundError(checkpoint)
    assert b['load_bold_pair_model']() is not None, 'Checkpoint incompatible with pipeline'
    questions,layouts=b['load_split'](data)
    manifests=read(data/'manifest.jsonl')
    assert len(questions)==args.expected_questions, (len(questions),args.expected_questions)
    types=Counter();fallbacks=[];current={}
    original=b['pairwise_bold_winner']
    def track(*a):
        winner=original(*a)
        fallbacks.append(dict(question_id=current['id'],winner=winner))
        return winner
    b['pairwise_bold_winner']=track
    start=time.monotonic();predictions=[]
    log=[f'UTC {datetime.now(timezone.utc).isoformat()}',f'data={data}',f'source={source}',f'checkpoint_sha256={sha(checkpoint)}']
    for i,q in enumerate(questions):
        current['id']=q['question_id']
        intent=b['parse_intent'](q['question']);types[intent.reasoning_type]+=1
        result=b['solve'](intent,layouts[q['document_id']])
        answer,evidence=result if result is not None else ('không xác định',[])
        predictions.append(dict(question_id=q['question_id'],answer=answer,evidence=evidence))
        if (i+1)%250==0:
            line=f'{i+1}/{len(questions)} completed';log.append(line);print(line,flush=True)
    validate(predictions,questions,manifests)
    path=out/'predictions.jsonl'
    with path.open('w',encoding='utf-8') as f:
        for p in predictions:f.write(json.dumps(p,ensure_ascii=False,sort_keys=True)+'\n')
    archive=out/'private_submission_bold_grid_clean.zip'
    # A fixed member timestamp makes repeated packaging of identical predictions deterministic.
    member=zipfile.ZipInfo('predictions.jsonl',date_time=(2026,9,25,0,0,0))
    member.compress_type=zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(archive,'w') as z:z.writestr(member,path.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.namelist()==['predictions.jsonl']
        loaded=[json.loads(s) for s in z.read('predictions.jsonl').decode('utf-8').splitlines()]
        assert loaded==predictions
        validate(loaded,questions,manifests)
    metadata=dict(created_utc=datetime.now(timezone.utc).isoformat(),data_directory=str(data),documents=len(manifests),questions=len(questions),types=dict(types),unresolved=sum(p['answer']=='không xác định' for p in predictions),empty_evidence=sum(not p['evidence'] for p in predictions),resnet_calls=fallbacks,checkpoint_sha256=sha(checkpoint),notebook_sha256=sha(source),runner_sha256=sha(Path(__file__)),questions_sha256=sha(data/'questions.jsonl'),manifest_sha256=sha(data/'manifest.jsonl'),predictions_sha256=sha(path),submission_sha256=sha(archive),seconds=round(time.monotonic()-start,3),environment=dict(python=platform.python_version(),torch=b['torch'].__version__,opencv=b['cv2'].__version__),validation='Unique IDs exactly match questions; strict keys, nonempty answers, normalized bboxes and document page limits verified; ZIP re-read successfully.',external_submission=False)
    (out/'run.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copyfile(source,out/source.name)
    shutil.copyfile(Path(__file__),out/Path(__file__).name)
    log+=['VALIDATION PASSED',f'ZIP={archive}',f'SHA256={sha(archive)}']
    (out/'run.log').write_text('\n'.join(log)+'\n',encoding='utf-8')
    print(json.dumps(metadata,ensure_ascii=False,indent=2))
    print('READY:',archive)

if __name__=='__main__':main()
