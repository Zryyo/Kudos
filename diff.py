"""Word-diff consecutive revisions and attribute surviving contributions to editors."""

import difflib
from typing import TypedDict

# Below this many words, a block matching elsewhere is treated as coincidental
# word overlap ("the", "and", ...) rather than a genuine moved paragraph.
MIN_MOVE_BLOCK_WORDS = 4
MOVE_MATCH_RATIO = 0.85

# Adjacent insert/replace opcodes separated only by an equal run this short are
# stitched into one contribution — SequenceMatcher spuriously aligns unrelated
# paragraphs on stray shared words ("to", "and", "is"), fragmenting one edit
# into many tiny ones that read as low-effort in isolation.
MAX_MERGE_GAP_WORDS = 3


class Contribution(TypedDict):
    editor_email: str
    added_text: str
    timestamp: str
    word_count: int
    survived: float


def _is_moved(inserted_words: list[str], deleted_blocks: list[list[str]]) -> bool:
    """Guard 1: an inserted block that's really a relocation of deleted text earns no credit."""
    if len(inserted_words) < MIN_MOVE_BLOCK_WORDS:
        return False
    for deleted_words in deleted_blocks:
        if len(deleted_words) < MIN_MOVE_BLOCK_WORDS:
            continue
        ratio = difflib.SequenceMatcher(None, inserted_words, deleted_words, autojunk=False).ratio()
        if ratio >= MOVE_MATCH_RATIO:
            return True
    return False


def _survived_fraction(added_words: list[str], final_words: list[str]) -> float:
    """Guard 2: fraction of the added *sequence* still matched (as sequence, not just membership) in the final text."""
    if not added_words:
        return 0.0
    matcher = difflib.SequenceMatcher(None, added_words, final_words, autojunk=False)
    matched = sum(block.size for block in matcher.get_matching_blocks())
    return matched / len(added_words)


def _merge_insert_spans(curr_words: list[str], opcodes: list[tuple]) -> list[list[str]]:
    spans: list[tuple[int, int]] = []
    active_start: int | None = None
    active_end: int | None = None

    for tag, _i1, _i2, j1, j2 in opcodes:
        if tag in ("insert", "replace"):
            if active_start is None:
                active_start = j1
            active_end = j2
        elif tag == "equal":
            if active_start is not None and (j2 - j1) <= MAX_MERGE_GAP_WORDS:
                active_end = j2  # absorb the short connective gap into the span
            else:
                if active_start is not None:
                    spans.append((active_start, active_end))
                active_start = active_end = None
        # 'delete' opcodes carry no curr-side words, so they don't break a span.

    if active_start is not None:
        spans.append((active_start, active_end))

    return [curr_words[start:end] for start, end in spans]


def attribute_contributions(revisions: list[dict]) -> list[Contribution]:
    """revisions: list of dicts with at least id, editor_email, modifiedTime, text, sorted oldest to newest."""
    final_words = revisions[-1]["text"].split() if revisions else []
    contributions: list[Contribution] = []

    prev_words: list[str] = []
    for rev in revisions:
        curr_words = rev["text"].split()
        opcodes = difflib.SequenceMatcher(None, prev_words, curr_words, autojunk=False).get_opcodes()

        deleted_blocks = [prev_words[i1:i2] for tag, i1, i2, j1, j2 in opcodes if tag in ("delete", "replace")]
        inserted_blocks = _merge_insert_spans(curr_words, opcodes)

        for inserted_words in inserted_blocks:
            if not inserted_words or _is_moved(inserted_words, deleted_blocks):
                continue
            contributions.append(
                {
                    "editor_email": rev["editor_email"],
                    "added_text": " ".join(inserted_words),
                    "timestamp": rev["modifiedTime"],
                    "word_count": len(inserted_words),
                    "survived": _survived_fraction(inserted_words, final_words),
                }
            )

        prev_words = curr_words

    return contributions


def _load_revisions_with_text(source) -> list[dict]:
    revisions = source.list_revisions()
    for rev in revisions:
        rev["text"] = source.get_revision_text(rev["id"])
    return revisions


if __name__ == "__main__":
    from sources import MockSource

    revisions = _load_revisions_with_text(MockSource())
    contributions = attribute_contributions(revisions)

    surviving_words_by_editor: dict[str, float] = {}
    total_words_by_editor: dict[str, int] = {}
    for c in contributions:
        surviving_words_by_editor[c["editor_email"]] = surviving_words_by_editor.get(c["editor_email"], 0.0) + c["word_count"] * c["survived"]
        total_words_by_editor[c["editor_email"]] = total_words_by_editor.get(c["editor_email"], 0) + c["word_count"]

    total_surviving = sum(surviving_words_by_editor.values())
    print(f"{'editor':<20}{'added':>8}{'surviving':>12}{'share':>8}")
    for editor in sorted(surviving_words_by_editor, key=lambda e: -surviving_words_by_editor[e]):
        surviving = surviving_words_by_editor[editor]
        share = surviving / total_surviving if total_surviving else 0.0
        print(f"{editor:<20}{total_words_by_editor[editor]:>8}{surviving:>12.1f}{share:>8.1%}")
