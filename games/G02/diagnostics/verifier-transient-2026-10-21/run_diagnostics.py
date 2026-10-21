"""Bounded isolated diagnostic. Does not edit any frozen G02 delivery file."""
import datetime
import hashlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
REPO = PROJECT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name,value):
    (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    manifest = json.loads((PROJECT/"package-manifest.json").read_text(encoding="utf-8"))
    expected = {row["path"]:row["sha256"] for row in manifest["files"]}
    expected["package-manifest.json"] = sha(PROJECT/"package-manifest.json")
    for name,digest in expected.items():
        assert sha(PROJECT/name) == digest, (name,"live frozen file changed")
    archive = PROJECT/"G02_Preparation_2026-10-21.zip"
    frozen_before = {**expected, archive.name:sha(archive),
                     "verification/package-check.json":sha(PROJECT/"verification/package-check.json")}
    # Preserve the root controller's incident record; never write to validation/.
    incident = REPO/"validation/G02-transient-failure.json"
    if incident.is_file():
        shutil.copyfile(incident,HERE/"root-transient-failure.snapshot.json")
    runs = []
    env = dict(os.environ,PYTHONUTF8="1")
    for i in range(1,6):
        target = HERE/f"isolated-run-{i}"/"G02"
        assert not target.exists(), "Use a new diagnostics directory instead of deleting prior evidence"
        target.mkdir(parents=True)
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                path = Path(member.filename)
                assert path.parts[0] == "G02" and ".." not in path.parts
                if member.is_dir():
                    continue
                dest = target.joinpath(*path.parts[1:])
                assert dest.resolve().is_relative_to(HERE)
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(z.read(member))
        assert all(sha(target/name)==digest for name,digest in expected.items())
        started = datetime.datetime.now(datetime.timezone.utc)
        result = subprocess.run([sys.executable,"-B",str(target/"tools/verify.py"),"--all"],
            cwd=target,env=env,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120)
        ended = datetime.datetime.now(datetime.timezone.utc)
        (HERE/f"run-{i}.stdout.log").write_text(result.stdout,encoding="utf-8")
        (HERE/f"run-{i}.stderr.log").write_text(result.stderr,encoding="utf-8")
        payload = json.loads((target/"verification/verification-report.json").read_text(encoding="utf-8"))
        dump(f"run-{i}.verification.json",payload)
        runs.append({"run":i,"started_utc":started.isoformat(),"ended_utc":ended.isoformat(),
            "exit_code":result.returncode,"overall_status":payload.get("overall_status"),
            "elapsed_seconds":(ended-started).total_seconds(),"source_files_match_frozen_manifest":True,
            "error":payload.get("message"),"stdout":f"run-{i}.stdout.log","stderr":f"run-{i}.stderr.log"})
        dump("progress.json",runs)
        print(f"isolated run {i}/5: exit={result.returncode}, {payload.get('overall_status')}",flush=True)
    # A separate single call checks the mutation probe's namespace effects.
    # No sixth full verification is performed.
    diagnostic_code = r'''
import builtins, hashlib, importlib.util, json, sys
from pathlib import Path
root=Path.cwd()
sys.path.insert(0,str(root/'tools'))
spec=importlib.util.spec_from_file_location('g02_diagnostic_frozen_verify',root/'tools/verify.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def snapshot():
    return {'global_names':sorted(m.__dict__),
        'actions_id':id(m.actions),'actions_code_id':id(m.actions.__code__),
        'enumerate_id':id(builtins.enumerate),'enumerate_repr':repr(builtins.enumerate),
        'global_enumerate_present':'enumerate' in m.__dict__,
        'enumerate_sample':list(enumerate([('A',),('B',)])),
        'trace':repr(sys.gettrace()),'profile':repr(sys.getprofile())}
before=snapshot()
vectors=m.rule_vectors()
after=snapshot()
print(json.dumps({'before':before,'after':after,'same_namespace_and_builtin':before==after,
    'rule_vector_count':len(vectors),'full_verify_called':False},ensure_ascii=False,indent=2))
'''
    probe = subprocess.run([sys.executable,"-B","-c",diagnostic_code],cwd=target,env=env,
        capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=30)
    (HERE/"namespace-probe.stderr.log").write_text(probe.stderr,encoding="utf-8")
    namespace = json.loads(probe.stdout) if probe.returncode == 0 else {"error":probe.stderr}
    dump("namespace-probe.json",namespace)
    frozen_after = {name:sha(PROJECT/name) for name in frozen_before}
    assert frozen_before == frozen_after, "diagnosis must not change frozen files"
    data = {"date":"2026-10-21","scope":"BOUNDED_DIAGNOSIS_NOT_A_NEW_DELIVERY_OR_GAME_TEST",
        "incident_record":str(incident),"incident_record_sha256":sha(incident) if incident.is_file() else None,
        "python_executable":sys.executable,"python_version":sys.version,
        "python_executable_sha256":sha(Path(sys.executable)),"jsonschema":importlib.metadata.version("jsonschema"),
        "subprocess_environment_change":{"PYTHONUTF8":"1"},"fresh_processes":5,
        "runs":runs,"namespace_probe_exit":probe.returncode,
        "namespace_probe_unchanged":namespace.get("same_namespace_and_builtin"),
        "frozen_files_checked":len(frozen_before),"all_frozen_hashes_unchanged":frozen_before==frozen_after,
        "archive_sha256":frozen_before[archive.name],"cause":"UNKNOWN",
        "conclusion":"NOT_REPRODUCED_IN_5_ISOLATED_RUNS" if all(x["exit_code"]==0 for x in runs) else "REPRODUCED_SEE_RUN_REPORTS",
        "source_observation":"Reported failure in ablation solve occurs before rule_vectors() and its exec mutation probe in verify() evaluation order. No attribution to interpreter/environment is established.",
        "changes_to_frozen_source":False,"repackaged":False,
        "limitation":"No locals/core dump preserved from the original transient failure; repeated PASS does not determine its cause or prove impossibility."}
    dump("diagnosis.json",data)
    print(data["conclusion"],flush=True)


if __name__ == "__main__":
    main()
