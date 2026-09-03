# add-step — Incremental Step Authoring

<required_reading>

- `conventions.md`
- `template-structure.md`

</required_reading>

<process>

Add a scaffolder step to an existing template without rebuilding from scratch.

## Step 1: Identify action

Ask what the step should do only when the request is underspecified. Otherwise,
map the requested behavior directly to a scaffolder action:

| Intent | Typical action |
|--------|----------------|
| Copy/template files | `fetch:template` |
| Fetch plain files | `fetch:plain` |
| Publish to GitHub | `publish:github` |
| Register catalog entity | `catalog:register` |
| Run custom action | `custom:<action-name>` |

Action IDs are camelCase. When unsure of installed actions, use the `list-actions` command to query the live instance.
When the request already names the action and complete inputs, continue without an
additional clarification round.

## Surgical insertion (fully specified prompt)

When the user names one `template.yaml` path, a step `id`, an `action`, and the
step `input` fields, and says to make no other changes:

1. Load `template-structure.md` and open only the named template file.
2. Insert **only** the requested step. Reuse existing `parameters` entries; do
   not add new form fields unless the user asked for them.
3. Wire credential-sensitive inputs to existing parameters (for example
   `repoUrl: ${{ parameters.repoUrl }}`). Never add `token`, `password`, `secret`,
   or literal credential values to the step `input`.
4. Do not edit skeleton files, README files, or other templates.
5. Run `fix_gotchas.py` on the edited template only when the reference workflow
   calls for it; otherwise stop after the single reviewed edit.

## Step 2: Choose position

Steps run **in series**. Ask where to insert:

- Before publish (materialize content)
- After publish (register, notify, trigger CI)

Assign unique `id` (kebab-case) and human-readable `name`.

## Step 3: Build input

Reference parameters and prior step outputs:

```yaml
- id: notify-team
  name: Notify platform team
  action: notification:send
  input:
    recipients: entity:group:default/platform-team
    title: New component ${{ parameters.componentId }}
    info: ${{ steps.publish.output.remoteUrl }}
```

For publishing or other credential-sensitive actions, use an existing parameter or
the platform's documented secret mechanism. Never add a literal token, password,
or credential to `template.yaml`, its skeleton, or the step input.

## Step 4: Update output (if needed)

If the step produces user-facing results, add `spec.output.links` referencing `${{ steps.<id>.output.* }}`.

## Step 5: Verify wiring

Checklist:

- [ ] `id` unique among all steps
- [ ] `action` uses correct camelCase ID
- [ ] All `${{ parameters.* }}` exist in form
- [ ] All `${{ steps.*.output.* }}` reference prior step IDs
- [ ] `fetch:template` steps include complete `values` map

## Step 6: fix-gotchas

```bash
python <skill-dir>/scripts/fix_gotchas.py --path <template.yaml> [--apply] [--json]
```

</process>

<success_criteria>

- New step inserted at correct position with unique `id`
- Action ID and inputs match conventions.md
- Downstream steps and `output` updated if they depend on new step
- fix-gotchas reports no critical action-casing or expression errors

</success_criteria>
