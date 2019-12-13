from collections import defaultdict
import common
import itertools

values_dct = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K",
              14: "A"}


def check_straight_flush(hand):
    values = common.get_hand_values(hand)

    if check_flush(hand)[0] and check_straight(hand)[0]:
        return True, hand, [max(values)], 0

    return False, [], [], 0


def check_four_of_a_kind(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if sorted(value_counts.values()) == [1, 4]:
        for key in value_counts:
            if value_counts[key] == 4:
                ans = key

        cards = [card for card in hand if common.get_hand_values([card])[0] == ans]
        return True, cards, [ans], 1
    return False, [], [], 1


def check_full_house(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if sorted(value_counts.values()) == [2, 3]:
        ans = [0, 0]
        for key in value_counts:
            if value_counts[key] == 3:
                ans[0] = key
            elif value_counts[key] == 2:
                ans[1] = key

        return True, hand, ans, 0
    return False, [], [], 0


def check_flush(hand):
    suits = common.get_hand_suits(hand)
    if len(set(suits)) == 1:
        return True, hand, sorted(common.get_hand_values(hand), reverse=True), 0

    return False, [], [], 0


def check_straight(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    value_range = max(values) - min(values)
    if value_range == 4 and len(set(value_counts.values())) == 1:
        return True, hand, [max(values)], 0

    # check straight with low Ace
    if set(values) == {14, 2, 3, 4, 5}:
        return True, hand, [5], 0

    return False, [], [], 0


def check_three_of_a_kind(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if 3 in value_counts.values():
        for key in value_counts:
            if value_counts[key] == 3:
                ans = key

        cards = [card for card in hand if common.get_hand_values([card])[0] == ans]
        return True, cards, [ans], 2

    return False, [], [], 2


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
                if pair1 == 0:
                    pair1 = key
                else:
                    pair2 = key

        cards = [card for card in hand if common.get_hand_values([card])[0] in [pair1, pair2]]
        return True, cards, sorted([pair1, pair2], reverse=True), 1
    return False, [], [], 1


def check_one_pair(hand):
    values = common.get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1

    if 2 in value_counts.values():
        for key in value_counts:
            if value_counts[key] == 2:
                ans = key

        cards = [card for card in hand if common.get_hand_values([card])[0] == ans]
        return True, cards, [ans], 3
    return False, [], [], 3


def check_hand(hand):
    flag, cards, ans, kickers_amount = check_straight_flush(hand)
    if flag:
        return 9, cards, ans, kickers_amount

    flag, cards, ans, kickers_amount = check_four_of_a_kind(hand)
    if flag:
        return 8, cards, ans, kickers_amount

    flag, cards, ans, kickers_amount = check_full_house(hand)
    if flag:
        return 7, cards, ans, kickers_amount

    flag, cards, ans, kickers_amount = check_flush(hand)
    if flag:
        return 6, cards, ans, kickers_amount

    flag, cards, ans, kickers_amount = check_straight(hand)
    if flag:
        return 5, cards, ans, kickers_amount

    flag, cards, ans, kickers_amount = check_three_of_a_kind(hand)
    if flag:
        return 4, cards, ans, kickers_amount

    flag, cards, ans, kickers_amount = check_two_pairs(hand)
    if flag:
        return 3, cards, ans, kickers_amount

    flag, cards, ans, kickers_amount = check_one_pair(hand)
    if flag:
        return 2, cards, ans, kickers_amount

    return 1, [], [], 5


def get_hand_score(hand, table_cards):
    combinations = itertools.combinations(hand + table_cards, 5)
    score = 0
    cards = []
    ans = []
    kickers_amount = 0

    for combination in combinations:
        curr_score, cards_curr, ans_curr, kickers_amount_curr = check_hand(combination)
        if curr_score > score:
            score = curr_score
            ans = ans_curr
            cards = cards_curr
            kickers_amount = kickers_amount_curr

    kickers = []
    for card in hand + table_cards:
        if card not in cards:
            kickers.append(card)

    kickers = sorted(kickers, reverse=True)[:kickers_amount]
    return score, cards, ans, kickers


def choose_winner(left_hand, right_hand, table_cards):
    left_score, left_cards, left_ans, left_kickers = get_hand_score(left_hand, table_cards)
    right_score, right_cards, right_ans, right_kickers = get_hand_score(right_hand, table_cards)

    combination_lst = ["no combination", "one pair", "two pairs", "three of a kind", "straight", "flush", "full house",
                       "four of a kind",
                       "straight flush"]

    print("===================================================================================")
    print(f"Alice has combination '{combination_lst[left_score - 1]}' with main card values:")
    common.print_cards_in_lst(left_cards)
    print("and kickers")
    common.print_cards_in_lst(left_kickers)

    print(f"Bob has combination '{combination_lst[right_score - 1]}' with main card values:")
    common.print_cards_in_lst(right_cards)
    print("and kickers")
    common.print_cards_in_lst(right_kickers)

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
    left_hand = [10, 39]
    right_hand = [33, 51]
    table = [23, 47, 48, 34, 32]
    common.print_cards_in_lst(left_hand)
    common.print_cards_in_lst(right_hand)
    common.print_cards_in_lst(table)

    print(choose_winner(left_hand, right_hand, table))
