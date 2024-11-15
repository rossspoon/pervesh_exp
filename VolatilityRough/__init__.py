from otree.api import *  # Import oTree module for building experiment
import random  # Import random module to randomize choices

# Constants class for defining experiment settings
class C(BaseConstants):
    NAME_IN_URL = 'VolatilityRough'  # URL name of the app
    PLAYERS_PER_GROUP = 3  # Number of players per group
    NUM_ROUNDS = 20  # Total number of rounds for the game
    TREATMENTS = [  # Different income distributions for the treatments
        [1000,1000,1000,1000,1000],  # Treatment 1
        [548, 813, 1024, 1205, 1410],  # Treatment 2
        [219, 512, 1006, 1354, 1909],  # Treatment 3
        [500, 500, 500, 500, 500],  # Treatment 4
        [308, 409, 477, 553, 753],  # Treatment 5
        [151, 250, 454, 656, 989],     # Treatment 6
    ]

# Subsession class for setting up initial conditions and configurations
class Subsession(BaseSubsession):
    pass

def creating_session(self):
    if self.round_number == 1:  # Only assign treatments at the start of the experiment
        treatment_indices = list(range(len(C.TREATMENTS)))
        random.shuffle(treatment_indices)  # Shuffle to assign treatments randomly
        for i, player in enumerate(self.get_players()):
            player.treatment = treatment_indices[i % len(C.TREATMENTS)] + 1  # Assign a treatment to each player

# Group class for handling group-level logic and calculations
class Group(BaseGroup):
    median_tax_rate = models.FloatField()  # Field to store the median tax rate of the group

    # Method to set the median tax rate based on players' choices
    def set_median_tax(self):
        tax_choices = [p.tax_choice for p in self.get_players()]  # Collect tax choices from players
        self.median_tax_rate = sorted(tax_choices)[len(tax_choices) // 2]  # Calculate median

    # Method to calculate and distribute tax revenue among players
    def distribute_revenue(self):
        total_tax_revenue = sum(
            (p.realized_income * self.median_tax_rate / 100) for p in self.get_players()
        )  # Calculate total revenue collected
        revenue_per_player = total_tax_revenue / len(self.get_players())  # Revenue shared per player

        # Loop through players to set final income details
        for p in self.get_players():
            tax_deducted = p.realized_income * self.median_tax_rate / 100  # Tax deducted from income
            p.income_after_tax = p.realized_income - tax_deducted + revenue_per_player  # Calculate post-tax income
            p.tax_deducted = tax_deducted
            p.transferred_revenue = revenue_per_player

# Player class for individual player properties and methods
class Player(BasePlayer):
    treatment = models.IntegerField()  # Field to store the assigned treatment
    tax_choice = models.FloatField(min=0, max=100, label="Choose a tax percentage (0% to 100%)")  # Player's tax choice
    realized_income = models.IntegerField()  # Realized income for the round
    income_after_tax = models.CurrencyField()  # Final income after tax deduction and revenue sharing
    tax_deducted = models.CurrencyField()  # Amount of tax deducted
    transferred_revenue = models.CurrencyField()  # Revenue received from pooled tax

    # Method to randomly set the income from the treatment distribution
    def set_realized_income(self):
        treatment_index = self.treatment - 1  # Adjust treatment for zero-indexed list
        self.realized_income = random.choice(C.TREATMENTS[treatment_index])  # Random income assignment

from ._builtin import Page, WaitPage  # Import base classes for oTree pages

# Page for players to make their tax choices
class TaxChoice(Page):
    form_model = 'player'  # Use Player model to store form data
    form_fields = ['tax_choice']  # Form field to capture tax choice

    # Method to set realized income and distribute revenue after tax choice

    def before_next_page(player: Player, timeout_happened):
        player.set_realized_income()  # Assign income for the round
        player.group.set_median_tax()  # Calculate the median tax rate
        if player.id_in_group == 1:  # Ensure only one player triggers revenue distribution
            player.group.distribute_revenue()

    # Variables to pass to the template for display
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'round_number': player.subsession.round_number,  # Current round number
            'previous_rounds': player.in_previous_rounds(),  # Data from previous rounds
        }

# Page to display the results of the round
class Results(Page):
    def vars_for_template(self):
        return {
            'tax_choice': self.player.tax_choice,  # Player's tax choice
            'realized_income': self.player.realized_income,  # Realized income for the round
            'tax_deducted': self.player.tax_deducted,  # Amount of tax deducted
            'transferred_revenue': self.player.transferred_revenue,  # Revenue shared with the player
            'income_after_tax': self.player.income_after_tax,  # Final income after deductions
        }

# Sequence of pages in the experiment
page_sequence = [TaxChoice, Results]
