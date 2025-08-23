# ---- Primitive condition functions (stubs/real) ----

def is_nikud(context, pos, nikuds):
    # TODO: בדיקה אמיתית על הייצוג שלך
    return True

def not_is_letter(context, pos, letters):
    # TODO
    return True

def in_list(context, list=None, words=None):
    """
    יקר: לעיתים דורש נרמול/לממטיזציה/ניתוח מורפולוגי.
    - list: שם רשימה חיצונית (context.lists[name] => set)
    - words: רשימת מילים inline (set)
    ה־context אמור להכיל מילה/טוקן לעבודה (לפי העיצוב שלך).
    """
    target = context.current_word_norm()  # למשל מילה מנורמלת/לממה
    if list:
        s = context.lookup_list(list)  # set או מבנה מיוחד
        return target in s
    if words:
        s = context.inline_words_cache(tuple(words))  # המרה ל־set עם cache
        return target in s
    return False

def is_syntactic_feature(context, feature):
    # יקר: דוגמא – טעינת ניתוח תחבירי/מורפו עם cache עצלני
    ana = context.get_analysis()
    return ana.has_feature(context.cur_index, feature)

# ---- ACTION dispatcher ----

def call_action(name, context, args):
    if name == "add_after":
        return add_after(context, **args)
    # הוסף פעולות אחרות
    raise NotImplementedError(name)

def add_after(context, letter):
    context.builder_add_after(letter)  # אתה מגדיר איך משנים את הפלט
    return True

# ---- CONDITION evaluator with cost ordering ----

def _leaf_cost(node, func_cost):
    return func_cost.get(node["function"], 0)

def _est_cost(node, func_cost):
    t = node["type"]
    if t == "leaf":
        return _leaf_cost(node, func_cost)
    if t == "not":
        return _est_cost(node["child"], func_cost)
    # לאופרטורים: נמיין ילדים לפי עלות משוערת
    costs = [_est_cost(ch, func_cost) for ch in node["children"]]
    return min(costs) if costs else 0

def eval_cond(node, context, func_cost):
    t = node["type"]
    if t == "leaf":
        fn = globals()[node["function"]]
        ok = fn(context, **node.get("args", {}))
        return (not ok) if node.get("negate", False) else ok

    if t == "not":
        return not eval_cond(node["child"], context, func_cost)

    if t == "all":
        # סדר לפי עלות (זול→יקר), ועצירה מוקדמת
        children = sorted(node["children"], key=lambda n: _est_cost(n, func_cost))
        for ch in children:
            if not eval_cond(ch, context, func_cost):
                return False
        return True

    if t == "any":
        # גם ב-ANY מריצים זול→יקר כדי להגיע ל-True מהר
        children = sorted(node["children"], key=lambda n: _est_cost(n, func_cost))
        for ch in children:
            if eval_cond(ch, context, func_cost):
                return True
        return False

    raise ValueError(f"Unknown node type: {t}")
