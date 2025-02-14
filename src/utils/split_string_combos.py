
def split_string_combos(string: str) -> list[tuple[str, str]]:
    result = []
    for i in range(1, len(string)):
        result.append((string[:i], string[i:]))

    return result

print(split_string_combos("U"))