from otree.api import *  # Import oTree module for building the experiment
import random  # Import random module to randomize choices


# Constants class for defining experiment settings
class C(BaseConstants):
    NAME_IN_URL = 'Volatility_New'  # URL name of the app
    PLAYERS_PER_GROUP = 4  # Number of players per group
    NUM_ROUNDS = 20  # Total number of rounds for the game
    TREATMENTS = [  # Different income distributions for the treatments
        [1000, 1000, 1000, 1000, 1000],  # Treatment 1
        [548, 813, 1024, 1205, 1410],  # Treatment 2
        [219, 512, 1006, 1354, 1909],  # Treatment 3
        [500, 500, 500, 500, 500],  # Treatment 4
        [308, 409, 477, 553, 753],  # Treatment 5
        [151, 250, 454, 656, 989],  # Treatment 6
    ]


class Subsession(BaseSubsession):
    pass
def creating_session(subsession: Subsession):
    # Only assign treatment for the first round and carry it over in subsequent rounds
    if subsession.round_number == 1:
        treatment_indices = list(range(len(C.TREATMENTS)))  # List of treatment indices
        for player in subsession.get_players():
            # Assign a random treatment index
            player.treatment = random.choice(treatment_indices)
            # Set the assigned income distribution for the first round
            player.assigned_income_distribution = str(C.TREATMENTS[player.treatment])
    else:
        # For subsequent rounds, retrieve the treatment and income distribution from round 1
        for player in subsession.get_players():
            player.treatment = player.in_round(1).treatment
            player.assigned_income_distribution = player.in_round(1).assigned_income_distribution


class Group(BaseGroup):
    median_tax = models.FloatField()  # Field for median tax
    total_tax_revenue = models.CurrencyField()  # Field for total tax revenue


class Player(BasePlayer):
    treatment = models.IntegerField()  # Treatment index assigned to the player
    tax_choice = models.FloatField(
        min=0, max=100, label="Choose your tax rate (0-100%)"
    )
    current_income = models.CurrencyField() # Current round income
    tax_deducted = models.CurrencyField() # Tax paid
    after_tax_income = models.CurrencyField()  # Income after tax
    transfers = models.CurrencyField()  # Share of tax revenue received
    final_income = models.CurrencyField()  # Final income after tax revenue distribution
    assigned_income_distribution = models.StringField()  # Field to store assigned income distribution as a string


# FUNCTIONS
def set_group_tax(group: Group):
    players = group.get_players()
    tax_choices = [p.tax_choice for p in players if p.tax_choice is not None]  # Collect tax choices

    if not tax_choices:  # Handle case with no valid choices
        print("No tax choices submitted.")
        return

    group.median_tax = sorted(tax_choices)[len(tax_choices) // 2]  # Calculate median tax rate

    # Calculate current income for each player based on their treatment
    for p in players:
        if p.treatment is not None:  # Ensure treatment is assigned
            # Randomly choose income from the assigned treatment
            p.current_income = random.choice(C.TREATMENTS[p.treatment])

            # Calculate disposable income after tax
            p.tax_deducted= (group.median_tax / 100) * p.current_income
            disposable_income = p.current_income - p.tax_deducted
            p.after_tax_income = disposable_income

    # Calculate total tax revenue for the group
    group.total_tax_revenue = sum((group.median_tax / 100) * p.current_income for p in players)

    # Distribute total tax revenue equally among group members to get final income
    for p in players:
        p.transfers= (group.total_tax_revenue / C.PLAYERS_PER_GROUP)
        p.final_income = p.after_tax_income + p.transfers


# PAGES
class Instructions1(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Show this page only in the first round
        return player.round_number == 1
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'num_rounds': C.NUM_ROUNDS,
            'players_per_group': C.PLAYERS_PER_GROUP,
        }

class Instructions2(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Show this page only in the first round
        return player.round_number == 1
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'num_rounds': C.NUM_ROUNDS,
            'players_per_group': C.PLAYERS_PER_GROUP,
        }

class Instructions3(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Show this page only in the first round
        return player.round_number == 1
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'num_rounds': C.NUM_ROUNDS,
            'players_per_group': C.PLAYERS_PER_GROUP,
        }

class Instructions4(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Show this page only in the first round
        return player.round_number == 1
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'num_rounds': C.NUM_ROUNDS,
            'players_per_group': C.PLAYERS_PER_GROUP,
        }

class Instructions5(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Show this page only in the first round
        return player.round_number == 1
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'num_rounds': C.NUM_ROUNDS,
            'players_per_group': C.PLAYERS_PER_GROUP,
        }




class TaxChoice(Page):
    form_model = 'player'
    form_fields = ['tax_choice']

    @staticmethod
    def vars_for_template(player: Player):
        # Access assigned income distribution for this player
        assigned_income = player.assigned_income_distribution
        print("assigned_income_distribution", assigned_income)
        return {
            'assigned_income_distribution': assigned_income,
        }


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_group_tax  # Calculate taxes after all players submit


class Results(Page):
    def vars_for_template(player: Player):
        return {
            'median_tax': player.group.median_tax,
            'current_income': player.current_income,
            'tax_deducted': player.tax_deducted,
            'after_tax_income': player.after_tax_income,
            'final_income': player.final_income,
            'transfers': player.transfers,
        }


page_sequence = [Instructions1,Instructions2,Instructions3,Instructions4,Instructions5,  TaxChoice, ResultsWaitPage, Results]
