class AND(list):
    def __repr__(self):
        return "AND(" + ", ".join(repr(x) for x in self) + ")"


class OR(list):
    def __repr__(self):
        return "OR(" + ", ".join(repr(x) for x in self) + ")"


class Rule:
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        self.consequent = consequent

    def __repr__(self):
        return "IF " + str(self.antecedent) + " THEN " + str(self.consequent)


def is_variable(word):
    return word.startswith("(?") and word.endswith(")") and len(word) > 3


def match(pattern, datum):
    p_words = pattern.split()
    d_words = datum.split()

    if len(p_words) != len(d_words):
        return None

    bindings = {}

    for p_word, d_word in zip(p_words, d_words):
        if is_variable(p_word):
            if p_word in bindings:
                if bindings[p_word] != d_word:
                    return None
            else:
                bindings[p_word] = d_word

        elif p_word != d_word:
            return None

    return bindings


def populate(template, bindings):
    if isinstance(template, str):
        words = template.split()
        res = []

        for w in words:
            if w in bindings:
                res.append(bindings[w])
            else:
                res.append(w)

        return " ".join(res)

    elif isinstance(template, AND):
        res = []

        for item in template:
            res.append(populate(item, bindings))

        return AND(res)

    elif isinstance(template, OR):
        res = []

        for item in template:
            res.append(populate(item, bindings))

        return OR(res)

    return template


def simplify(tree):
    if not isinstance(tree, (AND, OR)):
        return tree

    t = type(tree)
    flattened = []

    for child in tree:
        s_child = simplify(child)

        if isinstance(s_child, t):
            flattened.extend(s_child)
        else:
            flattened.append(s_child)

    cleaned = []

    for item in flattened:
        if item not in cleaned:
            cleaned.append(item)

    if len(cleaned) == 1:
        return cleaned[0]

    return t(cleaned)


def backchain_to_goal_tree(rules, hypothesis):
    goals = [hypothesis]

    for r in rules:
        b = match(r.consequent, hypothesis)

        if b is not None:
            ant = populate(r.antecedent, b)

            if isinstance(ant, str):
                sub = backchain_to_goal_tree(rules, ant)
                goals.append(sub)

            elif isinstance(ant, AND):
                subgoals = []

                for stmt in ant:
                    sub = backchain_to_goal_tree(rules, stmt)
                    subgoals.append(sub)

                goals.append(AND(subgoals))

            elif isinstance(ant, OR):
                subgoals = []

                for stmt in ant:
                    sub = backchain_to_goal_tree(rules, stmt)
                    subgoals.append(sub)

                goals.append(OR(subgoals))

    return simplify(OR(goals))


if __name__ == "__main__":
    zookeeper_rules = [
        Rule(
            AND([
                "(?x) gives milk",
                "(?x) has hair"
            ]),
            "(?x) is a mammal"
        ),

        Rule(
            AND([
                "(?x) eats meat",
                "(?x) is a mammal"
            ]),
            "(?x) is a carnivore"
        ),

        Rule(
            AND([
                "(?x) is a bird",
                "(?x) cannot fly",
                "(?x) swims"
            ]),
            "(?x) is a penguin"
        ),

        Rule(
            OR([
                "(?x) has feathers",
                "(?x) lays eggs"
            ]),
            "(?x) is a bird"
        )
    ]

    hypothesis = "opus is a penguin"
    tree = backchain_to_goal_tree(zookeeper_rules, hypothesis)
    print("Test 1 - Hypothesis:", hypothesis)
    print(tree)
    print()

    hypothesis2 = "opus likes fish"
    tree2 = backchain_to_goal_tree(zookeeper_rules, hypothesis2)
    print("Test 2 - Hypothesis:", hypothesis2)
    print(tree2)
    print()

    hypothesis3 = "opus is a bird"
    tree3 = backchain_to_goal_tree(zookeeper_rules, hypothesis3)
    print("Test 3 - Hypothesis:", hypothesis3)
    print(tree3)
    print()

    hypothesis4 = "leo is a carnivore"
    tree4 = backchain_to_goal_tree(zookeeper_rules, hypothesis4)
    print("Test 4 - Hypothesis:", hypothesis4)
    print(tree4)
