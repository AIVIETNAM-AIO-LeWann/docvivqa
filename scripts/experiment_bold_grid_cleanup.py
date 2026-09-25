"""A/B check on all Bold questions, plus unchanged-prediction checks on other tasks."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import html

from bold_grid_cleanup import cell_stroke_width

# Definition cells from the pinned upstream notebook; no dependency on local audit scripts.
CELLS = [3, 7, 9, 12, 14, 16, 18, 21, 23, 25, 27, 29, 31, 34, 36, 38, 41]

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/'outputs/baseline-full-error-analysis'
OUT = ROOT/'outputs/bold-grid-cleanup'
DATA = ROOT/'data/training_set'


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = OLD/'source/submission_pipeline.ipynb'
    checkpoint = OLD/'artifacts/models/bold_pair_resnet18.pt'
    run = json.loads((OLD/'training-run.json').read_text())
    assert digest(checkpoint)==run['checkpoint_sha256']
    nb = json.loads(source.read_text())
    b = {'ROOT':OLD, '__name__':'baseline_grid_cleanup'}
    exec(''.join(nb['cells'][3]['source']), b)
    b['torch'].set_num_threads(2); b['DEVICE']=b['torch'].device('cpu')
    for i in CELLS[1:]: exec(''.join(nb['cells'][i]['source']), b)
    assert b['load_bold_pair_model']() is not None
    spec=importlib.util.spec_from_file_location('official', OLD/'source/evaluate_predictions.py')
    ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
    questions,layouts=b['load_split'](DATA)
    labels={r['question_id']:r for r in read(DATA/'labels.jsonl')}
    before={r['question_id']:r for r in read(OLD/'predictions.jsonl')}
    val=set(run['validation_question_ids'])
    train=set(run['train_question_ids'])
    assert not val & train
    original_stroke=b['cell_stroke_width']
    neural=b['pairwise_bold_winner'];calls=[]
    def tracked_neural(*args):
        result=neural(*args);calls.append(result);return result
    b['pairwise_bold_winner']=tracked_neural
    def solve(q, fn):
        calls.clear();b['cell_stroke_width']=fn
        result=b['solve'](b['parse_intent'](q['question']),layouts[q['document_id']])
        answer,evidence=result if result is not None else ('không xác định',[])
        return dict(question_id=q['question_id'],answer=answer,evidence=evidence),len(calls)
    comparisons=[];predictions=[];unchanged=0
    for i,q in enumerate(questions):
        qid=q['question_id'];label=labels[qid]
        if label['reasoning_type']=='visual_bold_lookup':
            # Rerun the original on all 535 to ensure the historical reference is valid.
            original,old_calls=solve(q,original_stroke)
            assert original==before[qid],qid
            improved,new_calls=solve(q,cell_stroke_width)
            old_ok=original['answer'] in label['answers'];new_ok=improved['answer'] in label['answers']
            row=dict(question_id=qid,document_id=q['document_id'],question=q['question'],split='validation' if qid in val else 'train',expected=' | '.join(label['answers']),before=original['answer'],after=improved['answer'],before_correct=old_ok,after_correct=new_ok,change='fixed' if not old_ok and new_ok else 'regression' if old_ok and not new_ok else 'unchanged_correct' if new_ok else 'still_wrong',before_resnet=old_calls,after_resnet=new_calls)
            for prefix,pred in [('before',original),('after',improved)]:
                row[prefix+'_anls']=ev.anls(pred['answer'] if pred['answer']!='không xác định' else None,label['answers'])
                row[prefix+'_evidence_f1']=ev.evidence_scores(pred['evidence'],label['evidence'])[2]
                row[prefix+'_score']=.85*row[prefix+'_anls']+.15*row[prefix+'_evidence_f1']
                row[prefix+'_answered']=pred['answer']!='không xác định'
            comparisons.append(row)
        else:
            improved,_=solve(q,cell_stroke_width)
            assert improved==before[qid],f'Non-Bold changed: {qid}'
            unchanged+=1
        predictions.append(improved)
        if (i+1)%1000==0: print(f'{i+1}/{len(questions)}',flush=True)
    assert len(comparisons)==535 and len(predictions)==11000 and unchanged==10465
    summaries=[]
    for split in ['all','train','validation']:
        rows=[r for r in comparisons if split=='all' or r['split']==split]
        s=dict(split=split,total=len(rows),fixed=sum(r['change']=='fixed' for r in rows),regressions=sum(r['change']=='regression' for r in rows))
        for prefix in ['before','after']:
            for field in ['correct','resnet','answered']:
                s[prefix+'_'+field]=sum(r[prefix+'_'+field] for r in rows)
            for field in ['anls','evidence_f1','score']:
                s[prefix+'_'+field]=sum(r[prefix+'_'+field] for r in rows)/len(rows)
        summaries.append(s)
    with (OUT/'comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(comparisons[0]));writer.writeheader();writer.writerows(comparisons)
    for name,rows in [('comparison.jsonl',comparisons),('predictions-training_set.jsonl',predictions)]:
        with (OUT/name).open('w',encoding='utf-8') as f:
            for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    summary=dict(metrics=summaries,non_bold_predictions_identical=unchanged,source_sha256=digest(source),checkpoint_sha256=digest(checkpoint),implementation_sha256=digest(ROOT/'scripts/bold_grid_cleanup.py'),scope='Retrospective train/validation A/B; validation previously monitored during training and error diagnosis. No independent test claim.',environment=dict(torch=b['torch'].__version__,opencv=b['cv2'].__version__))
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    esc=lambda v:html.escape(str(v))
    body='<meta charset="utf-8"><style>body{font:16px system-ui;max-width:1200px;margin:32px auto}td,th{border:1px solid #ccd;padding:8px}table{border-collapse:collapse}pre{white-space:pre-wrap}a{color:#1769aa}</style><h1>Bold: baseline và bỏ đường kẻ</h1><p>535 câu, cùng checkpoint và cùng ngưỡng. Đánh giá hồi cứu; validation đã được xem khi train và chẩn đoán lỗi.</p><pre>'+esc(json.dumps(summary,ensure_ascii=False,indent=2))+'</pre><h2>Câu thay đổi hoặc còn sai</h2><table><tr><th>ID</th><th>Split</th><th>Trước</th><th>Sau</th><th>Nhãn</th><th>Thay đổi</th></tr>'
    for r in comparisons:
        if r['change']=='unchanged_correct':continue
        case=OLD/'cases'/f"{r['question_id']}.html"
        link=f'../baseline-full-error-analysis/cases/{r["question_id"]}.html' if case.exists() else '../baseline-full-error-analysis/index.html'
        body+=f'<tr><td><a href="{link}">{r["question_id"]}</a><br>{esc(r["question"])}</td>'+''.join('<td>'+esc(r[k])+'</td>' for k in ['split','before','after','expected','change'])+'</tr>'
    body+='</table>'
    (OUT/'index.html').write_text(body,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
