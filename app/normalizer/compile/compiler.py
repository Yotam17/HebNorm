import yaml
from pathlib import Path

def _normalize_cond_node(node):
    """הופך צורה מקוצרת לצורה אחידה של תנאי/אופרטור."""
    if isinstance(node, dict):
        if "function" in node:  # עלה
            return {"type": "leaf", "function": node["function"], "args": node.get("args", {}), "negate": False}
        if "not" in node:       # שלילה
            return {"type": "not", "child": _normalize_cond_node(node["not"])}
        if "all" in node:
            return {"type": "all", "children": [_normalize_cond_node(c) for c in node["all"]]}
        if "any" in node:
            return {"type": "any", "children": [_normalize_cond_node(c) for c in node["any"]]}
        # תמיכת shorthand לתוך exceptions: lists / words
        if "lists" in node:
            return {
                "type": "any",
                "children": [
                    {"type": "leaf", "function": "in_list", "args": {"list": lst}, "negate": False}
                    for lst in node["lists"]
                ],
            }
        if "words" in node:
            return {
                "type": "any",
                "children": [
                    {"type": "leaf", "function": "in_list", "args": {"words": node["words"]}, "negate": False}
                ],
            }
    raise ValueError(f"Unsupported condition node: {node}")

def _merge_conditions_and_exceptions(cond_block, exc_block):
    """מחזיר עץ לוגי אחד: ALL( conds_root , NOT(excs_root) ) אם יש exceptions."""
    if not cond_block:
        cond_root = {"type": "all", "children": []}
    elif "all" in cond_block or "any" in cond_block or "not" in cond_block:
        cond_root = _normalize_cond_node(cond_block)
    else:
        # ברירת מחדל: אם יש רק 'all' ברמה הזו
        cond_root = _normalize_cond_node({"all": cond_block.get("all", [])})

    if not exc_block:
        return cond_root

    # exceptions יכולים להיות any/all/words/lists או mix מקונן
    if "any" in exc_block or "all" in exc_block or "not" in exc_block or "lists" in exc_block or "words" in exc_block:
        exc_root = _normalize_cond_node(exc_block)
    else:
        # תמיכת shorthand נוספים בעתיד
        raise ValueError("Unsupported exceptions block")

    # עטיפה: ALL( cond_root , NOT(exc_root) )
    return {"type": "all", "children": [cond_root, {"type": "not", "child": exc_root}]}

def compile_rules(yaml_path: str, output_path: str):
    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    func_costs = data.get("function_costs", {})
    rules = data.get("rules", [])

    out = []
    out.append("# AUTO-GENERATED FILE (do not edit by hand)")
    out.append("from runtime.context import Context")
    out.append("from runtime.engine import eval_cond, call_action")
    out.append("")
    out.append(f"FUNC_COST = {repr(func_costs)}")
    out.append("")
    out.append("compiled_rules = []")
    out.append("")

    for r in rules:
        name = r["name"]
        desc = r.get("description", "")
        conds = r.get("conditions", {})
        excs  = r.get("exceptions", {})
        acts  = r.get("actions", [])

        combined = _merge_conditions_and_exceptions(conds, excs)

        out.append(f"# ---- {name} ----")
        out.append(f"{name}_COND = {repr(combined)}")
        out.append("")

        # פונקצית כלל
        out.append(f"def {name}(context):")
        out.append(f'    """{desc}"""')
        out.append(f"    if not eval_cond({name}_COND, context, FUNC_COST):")
        out.append("        return False")
        # actions
        if acts:
            out.append("    # actions:")
            for a in acts:
                fn = a["function"]
                args = a.get("args", {})
                out.append(f"    call_action({repr(fn)}, context, {repr(args)})")
        out.append("    return True")
        out.append("")
        out.append(f"compiled_rules.append({name})")
        out.append("")

    Path(output_path).write_text("\n".join(out), encoding="utf-8")
    print(f"✅ Compiled {len(rules)} rules → {output_path}")

if __name__ == "__main__":
    compile_rules("rules/vav_rules.yaml", "build/compiled_rules.py")
