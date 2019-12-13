from collections import defaultdict
import common
import itertools


def check_straight_flush(hand):
    values = common.get_hand_values(hand)

    if check_flush(hand)[0] and check_straight(hand)[0]:
        return True, [max(values)], 0

    return False, [], 0


def check_four_of_a_kind(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if sorted(value_counts.values()) == (1, 4):
        for key in value_counts:
            if value_counts[key] == 4:
                ans = key

        return True, [ans], 1
    return False, [], 1


def check_full_house(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if sorted(value_counts.values()) == (2, 3):
        ans = [0, 0]
        for key in value_counts:
            if value_counts[key] == 3:
                ans[0] = key
            elif value_counts[key] == 2:
                ans[1] = key

        return True, ans, 0
    return False, [], 0


def check_flush(hand):
    suits = common.get_hand_suits(hand)
    if len(set(suits)) == 1:
        return True, sorted(common.get_hand_values(hand), reverse=True), 0

    return False, [], 0


def check_straight(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    value_range = max(values) - min(values)
    if value_range == 4:
        return True, [max(values)], 0

    # check straight with low Ace
    if set(values) == {14, 2, 3, 4, 5}:
        return True, [5], 0

    return False, [], 0


def check_three_of_a_kind(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if 3 in value_counts.values():
        for key in value_counts:
            if value_counts[key] == 3:
                ans = key

        return True, [ans], 2

    return False, [], 2


def check_two_pairs(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if sorted(value_counts.values()) == [1, 2, 2]:
        pair1 = 0
        pair2 = 0

        for key in value_counts:
            if value_counts[key] == 2:
                if key != pair1:
                    pair1 = key
                else:
                    pair2 = key

        return True, sorted([pair1, pair2], reverse=True), 1
    return False, [], 1


def check_one_pair(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if 2 in value_counts.values():
        for key in value_counts:
            if value_counts[key] == 2:
                ans = key

        return True, [ans], 3
    return False, [], 3


def check_hand(hand):
    flag, ans, kickers_amount = check_straight_flush(hand)
    if flag:
        return 9, ans, kickers_amount

    flag, ans, kickers_amount = check_four_of_a_kind(hand)
    if flag:
        return 8, ans, kickers_amount

    flag, ans, kickers_amount = check_full_house(hand)
    if flag:
        return 7, ans, kickers_amount

    flag, ans, kickers_amount = check_flush(hand)
    if flag:
        return 6, ans, kickers_amount

    flag, ans, kickers_amount = check_straight(hand)
    if flag:
        return 5, ans, kickers_amount

    flag, ans, kickers_amount = check_three_of_a_kind(hand)
    if flag:
        return 4, ans, kickers_amount

    flag, ans, kickers_amount = check_two_pairs(hand)
    if flag:
        return 3, ans, kickers_amount

    flag, ans, kickers_amount = check_one_pair(hand)
    if flag:
        return 2, ans, kickers_amount

    return 1, [], kickers_amount


def get_hand_score(hand, table_cards):
    combinations = itertools.combinations(hand + table_cards, 5)
    score = 0
    ans = []
    kickers_amount = 0

    for combination in combinations:
        curr_score, ans_curr, kickers_amount_curr = check_hand(combination)
        if curr_score > score:
            score = curr_score
            ans = ans_curr
            kickers_amount = kickers_amount_curr

    kickers = []
    for card in hand + table_cards:
        if card not in ans:
            kickers.append(card)

    kickers = sorted(kickers, reverse=True)[:kickers_amount]
    return score, ans, kickers


def choose_winner(left_hand, right_hand, table_cards):
    left_score, left_ans, left_kickers = get_hand_score(left_hand, table_cards)
    right_score, right_ans, right_kickers = get_hand_score(right_hand, table_cards)

    combination_lst = ["no combination", "one pair", "two pairs", "three of a kind", "straight", "flush", "full house",
                       "four of a kind",
                       "straight flush"]

    print(f"Left guy has combination '{combination_lst[left_score - 1]}' with main cards:")
    common.print_cards_in_lst(left_ans)
    print(" and kickers ")
    common.print_cards_in_lst(left_kickers)
    print()

    print(f"Right guy has combination '{combination_lst[right_score - 1]}' with main cards:")
    common.print_cards_in_lst(right_ans)
    print(" and kickers ")
    common.print_cards_in_lst(right_kickers)
    print()

    if left_score > right_score:
        return 1, 0
    elif left_score < right_score:
        return 0, 1

    for left_card, right_card in zip(left_ans, right_ans):
        if left_card > right_card:
            return 1, 0
        elif left_card < right_card:
            return 0, 1

    for left_kicker, right_kicker in zip(left_kickers, right_kickers):
        if left_kicker > right_kicker:
            return 1, 0
        elif left_kicker < right_kicker:
            return 0, 1

    return 0, 0


if __name__ == '__main__':
    left_hand = [53, 49]
    right_hand = [26, 50]
    table = [16, 20, 32, 40, 21]
    common.print_cards_in_lst(left_hand)
    common.print_cards_in_lst(right_hand)
    common.print_cards_in_lst(table)

    print(choose_winner(left_hand, right_hand, table))
