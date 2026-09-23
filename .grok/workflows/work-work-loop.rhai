let meta = #{
    name: "work-work-loop",
    description: "Run one Work Work Loop phase: admit, author, score, gate, then stop",
    when_to_use: "One WWL phase for a run root. /work-work-loop, /workflow work-work-loop. The next phase is a new run.",
    phases: [
        #{ title: "Bind", detail: "Admit exactly one phase" },
        #{ title: "Author", detail: "Write this phase draft" },
        #{ title: "Score", detail: "Independent six-axis score" },
        #{ title: "Gate", detail: "Dry-run, then publish" },
    ],
};

fn trimmed(s) {
    if type_of(s) == "string" {
        s.trim();
        s
    } else {
        ""
    }
}

fn is_map(v) {
    type_of(v) == "map"
}

fn tally(r, known, sum) {
    if r == () || r.tokens_used == () {
        #{ known: false, sum: sum }
    } else {
        #{ known: known, sum: sum + r.tokens_used }
    }
}

let action = "";
let root = "";
let idea = "";
let spine = "BIBLE";
let locks_value = [];
let wake = "";
let skip_reason = ();

if args == () {
    pause("verification", "Pass args.action (start, continue or stop), args.wwl_root and args.idea when action is start.");
}
if args.action != () { action = trimmed(args.action); }
if args.wwl_root != () { root = trimmed(args.wwl_root); }
if args.idea != () { idea = args.idea; }
if args.spine != () { spine = trimmed(args.spine); }
if args.wake != () { wake = trimmed(args.wake); }
if args.skip_reason != () { skip_reason = args.skip_reason; }
if args.locks != () {
    if type_of(args.locks) == "string" {
        let lock_text = trimmed(args.locks);
        if lock_text != "" && lock_text != "none" {
            locks_value = lock_text;
        }
    } else if type_of(args.locks) == "array" {
        locks_value = args.locks;
    }
}
if action == "START" || action == "Start" { action = "start"; }
if action == "CONTINUE" || action == "Continue" { action = "continue"; }
if action == "STOP" || action == "Stop" { action = "stop"; }
if action == "" || root == "" {
    pause("verification", "Pass args.action and args.wwl_root.");
}
if action == "start" && (type_of(idea) != "string" || idea == "") {
    pause("verification", "start requires args.idea.");
}
if spine == "" { spine = "BIBLE"; }

let spec = #{
    root: root,
    action: action,
    idea: idea,
    locks: locks_value,
    spine: spine,
    skip_reason: skip_reason,
};
let spec_json = json_encode(spec);
let spec_file = root + "/.wwl-bind-spec.json";
let pkg_note = "Run from the clone that contains wwl_phase. Set the working directory and PYTHONPATH to that clone. If WWL_PACKAGE_ROOT is set, use that directory instead. ";

phase("Bind");
let bind_prompt = "You are the Work Work Loop binder. Use the write tool and the shell. Do not describe the phase.";
bind_prompt += " Write this JSON exactly to " + spec_file + " : ";
bind_prompt += spec_json;
bind_prompt += " Then " + pkg_note;
bind_prompt += "python -c \"import json; from pathlib import Path; from wwl_phase.bind import bind; spec=json.loads(Path(r'" + spec_file + "').read_text(encoding='utf-8')); print(json.dumps(bind(spec['root'], action=spec['action'], idea=spec.get('idea') or None, locks=spec.get('locks'), spine=spec.get('spine'), skip_reason=spec.get('skip_reason'))))\"";
bind_prompt += " Return that command's JSON object as your final answer. If the command fails, return {\"success\":false,\"error\":\"bind command failed\",\"retryable\":true,\"action\":\"stop\"}.";

let bind_schema = #{
    "type": "object",
    "required": ["success", "action"],
    "properties": #{
        "success": #{ "type": "boolean" },
        "error": #{ "type": "string" },
        "retryable": #{ "type": "boolean" },
        "action": #{ "type": "string" },
        "wwl_root": #{ "type": "string" },
        "idea": #{ "type": "string" },
        "locks": #{ "type": "array" },
        "spine": #{ "type": "string" },
        "phase": #{ "type": "integer" },
        "phase_name": #{ "type": "string" },
        "slug": #{ "type": "string" },
        "job": #{ "type": "string" },
        "of": #{ "type": "integer" },
        "mode": #{ "type": "string" },
        "skip_reason": #{ "type": "string" },
        "artifact": #{ "type": "string" },
        "draft_path": #{ "type": "string" },
        "publish_path": #{ "type": "string" },
        "kernel_path": #{ "type": "string" },
        "harness_path": #{ "type": "string" },
    },
};
let bound = agent(bind_prompt, #{ label: "bind", capability_mode: "execute", output_schema: bind_schema });
let bound_ok = bound != () && bound.success == true && is_map(bound.output) && bound.output.success == true;
if !bound_ok {
    log("FAILED bind");
    complete(#{ status: "FAILED", stage: "bind", summary: "Bind did not admit a phase." });
}
if bound.output.action == "stop" || bound.output.action == "unload" {
    log("SUCCESS " + bound.output.action);
    complete(#{ status: "SUCCESS", stage: bound.output.action, summary: bound.output.action });
}
if bound.output.phase == () || bound.output.draft_path == () || bound.output.publish_path == () {
    log("FAILED bind missing phase");
    complete(#{ status: "FAILED", stage: "bind", summary: "Bind JSON had no phase." });
}

let phase_no = bound.output.phase;
let phase_name = bound.output.phase_name;
let job = bound.output.job;
let slug = bound.output.slug;
let draft_path = bound.output.draft_path;
let publish_path = bound.output.publish_path;
let mode = bound.output.mode;
let run_idea = bound.output.idea;
let run_spine = bound.output.spine;
let run_of = bound.output.of;
let run_locks = json_encode(bound.output.locks);
let kernel = "docs/WORK_WORK_LOOP_DRAFT_V1.txt";
log("SUCCESS bind phase " + phase_no.to_string());

let known = true;
let token_sum = 0;
let noted = tally(bound, known, token_sum);
known = noted.known;
token_sum = noted.sum;

let attempt = 0;
let published = false;
let feedback = "";
let delivery = "";
let last_action = "";
let angel_note = "";

let gate_schema = #{
    "type": "object",
    "required": ["success", "action", "retryable"],
    "properties": #{
        "success": #{ "type": "boolean" },
        "action": #{ "type": "string" },
        "retryable": #{ "type": "boolean" },
        "error": #{ "type": "string" },
        "exit_code": #{ "type": "integer" },
    },
};
let close_schema = #{
    "type": "object",
    "required": ["success"],
    "properties": #{
        "success": #{ "type": "boolean" },
        "error": #{ "type": "string" },
        "retryable": #{ "type": "boolean" },
        "action": #{ "type": "string" },
        "gate_line": #{ "type": "string" },
        "token": #{ "type": "string" },
        "next_spine": #{ "type": "string" },
    },
};
let score_schema = #{
    "type": "object",
    "required": ["success", "scores", "evidence"],
    "properties": #{
        "success": #{ "type": "boolean" },
        "evidence": #{ "type": "string" },
        "scores": #{
            "type": "object",
            "required": ["S1_intent", "S2_scope", "S3_evidence", "S4_completeness", "S5_fit", "S6_next"],
            "properties": #{
                "S1_intent": #{ "type": "number" },
                "S2_scope": #{ "type": "number" },
                "S3_evidence": #{ "type": "number" },
                "S4_completeness": #{ "type": "number" },
                "S5_fit": #{ "type": "number" },
                "S6_next": #{ "type": "number" },
            },
        },
    },
};

while attempt < 3 && published == false {
    attempt += 1;
    if attempt == 1 && (phase_no == 5 || phase_no == 10) {
        phase("Author");
        let angel_jobs = [];
        angel_jobs.push(#{
            prompt: "Read " + kernel + " from the clone with read_file. If WWL_KERNEL_PATH is set, read that file instead. Propose the safe ShoulderAngels path for phase "
                + phase_no.to_string() + " " + phase_name + ". Idea: " + json_encode(run_idea)
                + ". Stay inside this phase. Return one paragraph.",
            label: "angel-safe",
            capability_mode: "read-only",
        });
        angel_jobs.push(#{
            prompt: "Read " + kernel + " from the clone with read_file. If WWL_KERNEL_PATH is set, read that file instead. Propose the bold ShoulderAngels path for phase "
                + phase_no.to_string() + " " + phase_name + ". Idea: " + json_encode(run_idea)
                + ". Stay inside this phase. Return one paragraph.",
            label: "angel-bold",
            capability_mode: "read-only",
        });
        let angels = parallel(angel_jobs);
        angel_note = "";
        let ai = 0;
        for angel in angels {
            noted = tally(angel, known, token_sum);
            known = noted.known;
            token_sum = noted.sum;
            if angel != () && angel.success == true && type_of(angel.output) == "string" && angel.output != "" {
                angel_note += angel.output;
                angel_note += "\n";
            } else {
                log("SKIPPED angel " + ai.to_string());
            }
            ai += 1;
        }
    }

    phase("Author");
    let author_prompt = "Read " + kernel + " from the clone with read_file before you write. If WWL_KERNEL_PATH is set, read that file instead. Author Work Work Loop phase ";
    author_prompt += phase_no.to_string() + " " + phase_name + " only. Job: " + job + ". Mode: " + mode + ".";
    author_prompt += " Idea: " + json_encode(run_idea) + ". Locks: " + run_locks + ".";
    author_prompt += " Write one UTF-8 markdown file at exactly " + draft_path + ".";
    author_prompt += " The file must be at least 100 bytes. Do not use a TODO or placeholder marker.";
    author_prompt += " Do not write any other file. Do not publish. Do not start another phase.";
    author_prompt += " Ground claims in files, ids, or sources you opened. Tag the rest UNGROUNDED.";
    if mode == "skip" {
        author_prompt += " This is a trim. The file states the SKIP_REASON and does not do the rest of the phase.";
    }
    if angel_note != "" {
        author_prompt += " Lock one path using these safe and bold notes: " + json_encode(angel_note);
    }
    if feedback != "" {
        author_prompt += " The previous gate rejected the draft. Fix this and rewrite the file: " + json_encode(feedback);
    }
    author_prompt += " Final answer JSON: {\"success\":true,\"delivery\":\"the user-visible phase result\"}.";
    let author = agent(author_prompt, #{ label: "author", capability_mode: "read-write" });
    noted = tally(author, known, token_sum);
    known = noted.known;
    token_sum = noted.sum;
    if author == () || author.success != true {
        log("FAILED author attempt " + attempt.to_string());
        feedback = "author returned no draft";
    } else {
        if is_map(author.output) && author.output.delivery != () {
            delivery = author.output.delivery;
        } else if type_of(author.output) == "string" {
            delivery = author.output;
        }

        phase("Score");
        let score_prompt = "Read the draft at " + draft_path + " with read_file. Do not edit it.";
        score_prompt += " Score this Work Work Loop phase only. Idea: " + json_encode(run_idea) + ".";
        score_prompt += " Return integers 0-100 for S1_intent, S2_scope, S3_evidence, S4_completeness, S5_fit, S6_next.";
        score_prompt += " S3_evidence stays under 99 when the draft has no file path, id, source, or an UNGROUNDED tag.";
        score_prompt += " evidence is one sentence naming what you read. success is true only after you have read the draft.";
        let scorer = agent(score_prompt, #{
            label: "score",
            capability_mode: "read-only",
            output_schema: score_schema,
        });
        noted = tally(scorer, known, token_sum);
        known = noted.known;
        token_sum = noted.sum;
        if scorer == () || scorer.success != true || !is_map(scorer.output) || scorer.output.success != true || !is_map(scorer.output.scores) {
            log("FAILED score attempt " + attempt.to_string());
            feedback = "scorer did not return six axes";
        } else {
            phase("Gate");
            let scores_json = json_encode(scorer.output.scores);
            let scores_file = root + "/drafts/scores.json";
            let gate_prompt = "Write this JSON exactly to " + scores_file + " : " + scores_json;
            gate_prompt += " Then " + pkg_note + "Run python -m wwl_phase gate";
            gate_prompt += " --root " + json_encode(root);
            gate_prompt += " --draft " + json_encode(draft_path);
            gate_prompt += " --phase " + phase_no.to_string();
            gate_prompt += " --slug " + slug;
            gate_prompt += " --scores-file " + json_encode(scores_file);
            gate_prompt += " --publish " + json_encode(publish_path);
            gate_prompt += " --dry-run";
            gate_prompt += " Return the command JSON unchanged. Do not copy the draft yourself.";
            let gated = agent(gate_prompt, #{ label: "gate-dry", capability_mode: "execute", output_schema: gate_schema });
            noted = tally(gated, known, token_sum);
            known = noted.known;
            token_sum = noted.sum;
            last_action = "";
            if gated != () && gated.success == true && is_map(gated.output) && gated.output.action != () {
                last_action = gated.output.action;
            }
            if last_action == "dry_run" {
                let publish_prompt = pkg_note + "Run python -m wwl_phase gate";
                publish_prompt += " --root " + json_encode(root);
                publish_prompt += " --draft " + json_encode(draft_path);
                publish_prompt += " --phase " + phase_no.to_string();
                publish_prompt += " --slug " + slug;
                publish_prompt += " --scores-file " + json_encode(scores_file);
                publish_prompt += " --publish " + json_encode(publish_path);
                publish_prompt += " Do not pass --dry-run. Return the command JSON unchanged.";
                let pub = agent(publish_prompt, #{ label: "gate-publish", capability_mode: "execute", output_schema: gate_schema });
                noted = tally(pub, known, token_sum);
                known = noted.known;
                token_sum = noted.sum;
                if pub != () && pub.success == true && is_map(pub.output) && pub.output.success == true {
                    published = true;
                    last_action = "publish";
                    log("SUCCESS publish phase " + phase_no.to_string());
                } else {
                    last_action = "publish";
                    feedback = "publish failed";
                    if pub != () && is_map(pub.output) && pub.output.error != () {
                        feedback = pub.output.error;
                    }
                    if pub != () && is_map(pub.output) && pub.output.retryable == false {
                        log("FAILED publish");
                        complete(#{ status: "FAILED", stage: "publish", summary: feedback, phase: phase_no });
                    }
                    log("FAILED publish attempt " + attempt.to_string());
                }
            } else if last_action == "rewrite" {
                feedback = "gate asked for a rewrite";
                if gated != () && is_map(gated.output) && gated.output.error != () {
                    feedback = gated.output.error;
                }
                log("FAILED rewrite attempt " + attempt.to_string());
            } else {
                if last_action == "" { last_action = "stop"; }
                log("FAILED gate " + last_action);
                complete(#{
                    status: "FAILED",
                    stage: "gate",
                    action: last_action,
                    summary: feedback,
                    phase: phase_no,
                });
            }
        }
    }
}

if published != true {
    log("FAILED phase " + phase_no.to_string());
    complete(#{
        status: "FAILED",
        stage: "gate",
        action: last_action,
        summary: feedback,
        phase: phase_no,
        attempts: attempt,
    });
}

let tokens_in = "UNKNOWN";
let tokens_out = "UNKNOWN";
let tokens_used = "UNKNOWN";
if known == true { tokens_used = token_sum.to_string(); }
phase("Gate");
let close_prompt = pkg_note + "Run python -m wwl_phase close";
close_prompt += " --phase " + phase_no.to_string();
close_prompt += " --spine " + run_spine;
close_prompt += " --locks " + run_locks;
close_prompt += " --tokens-in " + tokens_in;
close_prompt += " --tokens-out " + tokens_out;
if wake != "" {
    close_prompt += " --wake " + wake;
}
close_prompt += " Return the command JSON unchanged.";
let closed = agent(close_prompt, #{ label: "close", capability_mode: "execute", output_schema: close_schema });
noted = tally(closed, known, token_sum);
if closed == () || closed.success != true || !is_map(closed.output) || closed.output.success != true {
    log("FAILED close");
    complete(#{
        status: "FAILED",
        stage: "close",
        summary: "Phase is published. Close did not render the card.",
        phase: phase_no,
        artifact: publish_path,
        delivery: delivery,
    });
}

log("SUCCESS phase " + phase_no.to_string() + " of " + run_of.to_string());
let report = delivery + "\n\n" + closed.output.gate_line + "\n\n```\n" + closed.output.token + "\n```\n";
let report_path = write_scratch_file("wwl-phase.md", report);
complete(#{
    status: "SUCCESS",
    stage: "close",
    summary: closed.output.gate_line,
    phase: phase_no,
    of: run_of,
    artifact: publish_path,
    path: report_path,
    tokens_used: tokens_used,
    report: report,
});
