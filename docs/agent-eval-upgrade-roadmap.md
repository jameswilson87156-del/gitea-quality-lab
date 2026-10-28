# PromptOps Studio Upgrade Roadmap

PromptOps Studio remains the AI Agent evaluation project. Gitea Quality Lab adds conventional API/UI/permission/persistence automation; it does not replace the Agent Eval project or turn its local simulator into a production system.

## Next engineering steps

1. **Verify the current baseline from artifacts.** Keep deterministic Mock Agent results clearly labeled; preserve current intentional failing synthetic cases. Re-run the existing Maven, frontend build, local production-like Compose, monitoring, soak, and k6 checks before changing the baseline.
2. **Add a no-paid-call real model path.** First inspect local CPU/GPU/RAM and supported provider interfaces. Prefer a local model if the machine can run one. Cloud-compatible providers stay opt-in, read credentials only from environment variables, and require an explicit per-run budget setting before a request is sent.
3. **Make every model run reproducible.** Persist dataset version, exact case ID, prompt/agent snapshot or hash, provider/model identifier, decoding parameters, runtime version, timestamp, and trace. Keep model outputs and failures as observed data; never label a Mock output as a real model response.
4. **Add repeated-run drift analysis.** Execute the same fixed dataset more than once for a selected provider/configuration; report per-case output differences, assertion changes, latency samples, and any actual request/cost counters the provider supplies. Avoid inventing aggregate accuracy or cost where there is no measurement.
5. **Strengthen regression gates.** Gate a release candidate on named critical cases, schema/business invariants, protected-tool behavior, and explicit run completion. Keep comparison output tied to actual stored V1/V2 run IDs and configuration snapshots.
6. **Integrate real business systems only with authorization.** Production monitoring, broad load tests, or business-system evaluation require a named staging target, owner approval, traffic ceiling, schedule, stop condition, and rollback/contact plan. The local order/refund simulator and local k6 runs must remain described as local simulation evidence.

## Honest portfolio split

| Project | Evidence it can support | Claims it cannot support |
|---|---|---|
| PromptOps Studio | Agent dataset execution, deterministic Mock evaluation, traces, local order/refund simulator, local monitoring/soak/load checks that have corresponding run artifacts | Real model quality or cost unless actual provider calls were measured; company production monitoring or production-scale traffic |
| Gitea Quality Lab | Local black-box API, authorization, Chromium workflow, SQLite persistence, JSON/JUnit/HTML reports, and local CI configuration | Company-specific business behavior, production incidents, or production capacity |

This division gives a Test Development internship portfolio one AI-evaluation system and one conventional application-testing project, with evidence boundaries stated for both.
