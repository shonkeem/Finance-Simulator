from pydantic import BaseModel, model_validator, field_validator
from datetime import date
from enum import Enum

# FRAMING

class TimeStep(str, Enum):
    monthly = "monthly"

class FramingInput(BaseModel):
    label: str
    start_date: date
    end_date: date
    time_step: TimeStep

    @model_validator(mode="after")
    def end_after_start(self) -> "FramingInput":
        if self.start_date >= self.end_date:
            raise ValueError("end_date must be after start_date")
        return self
    
    @model_validator(mode="after")
    def is_first_of_month(self) -> "FramingInput":
        if self.start_date.day != 1:
            raise ValueError("start_date must be the first of the month")
        elif self.end_date.day != 1:
            raise ValueError("end_date must be the first of the month")
        return self
    
    @model_validator(mode="after")
    def period_less_than_600(self) -> "FramingInput":
        if 12 * (self.end_date.year - self.start_date.year) + (self.end_date.month - self.start_date.month) > 600:
            raise ValueError("Start and end dates must be within 600 months of each other")
        return self

# LOADS

class IncomeLoad(BaseModel):
    name: str
    monthly_gross: float
    annual_growth_rate: float
    start_date: date
    end_date: date | None = None

    @field_validator("monthly_gross")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("monthly_gross must be > 0")
        return v
    
class ExpenseLoad(BaseModel):
    name: str
    monthly_amount: float
    category: str
    inflation_linked: bool

    @field_validator("monthly_amount")
    @classmethod
    def must_be_nonnegative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("monthly_amount must be >= 0")
        return v
    
    @field_validator("category")
    @classmethod
    def must_be_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("category must be a non-empty string")
        return v
    
class DebtLoad(BaseModel):
    name: str
    current_balance: float
    annual_rate: float
    minimum_monthly_payment: float
    extra_monthly_payment: float

    @field_validator("current_balance", "minimum_monthly_payment")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be > 0")
        return v
    
    @field_validator("annual_rate")
    @classmethod
    def must_be_percentage(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("annual_rate must be between 0 and 1")
        return v
    
    @field_validator("extra_monthly_payment")
    @classmethod
    def must_be_nonnegative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("extra_monthly_payment must be >= 0")
        return v
    
class InvestmentLoad(BaseModel):
    name: str
    account_type: str
    current_balance: float
    monthly_contribution: float
    employer_match_rate: float
    employer_match_cap_pct_salary: float
    assumed_annual_return: float

    @field_validator("current_balance", "monthly_contribution")
    @classmethod
    def must_be_nonnegative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("must be >= 0")
        return v
    
    @field_validator("employer_match_rate", "employer_match_cap_pct_salary")
    @classmethod
    def must_be_percentage(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("must be between 0 and 1")
        return v
    
class LoadsInput(BaseModel):
    income: list[IncomeLoad]
    expenses: list[ExpenseLoad]
    investments: list[InvestmentLoad]
    debts: list[DebtLoad]

    @model_validator(mode="after")
    def unique_income_names(self) -> "LoadsInput":
        names = [i.name for i in self.income]
        if len(names) != len(set(names)):
            raise ValueError("Income names must be unique")
        return self
    
    @model_validator(mode="after")
    def unique_expense_names(self) -> "LoadsInput":
        names = [i.name for i in self.expenses]
        if len(names) != len(set(names)):
            raise ValueError("Expense names must be unique")
        return self
    
    @model_validator(mode="after")
    def unique_debt_names(self) -> "LoadsInput":
        names = [i.name for i in self.debts]
        if len(names) != len(set(names)):
            raise ValueError("Debt names must be unique")
        return self
    
    @model_validator(mode="after")
    def unique_investment_names(self) -> "LoadsInput":
        names = [i.name for i in self.investments]
        if len(names) != len(set(names)):
            raise ValueError("Investment names must be unique")
        return self
    
# SETTINGS
class DebtStrategies(str, Enum):
    MINIMUM_ONLY = "minimum_only"
    AVALANCHE = "avalanche"
    SNOWBALL = "snowball"

class SettingsInput(BaseModel):
    inflation_rate: float = 0.0
    income_tax_rate: float = 0.0
    apply_income_tax: bool = False
    apply_inflation_to_expenses: bool = False
    debt_payoff_strategy: DebtStrategies = DebtStrategies.SNOWBALL
    starting_cash: float = 0.0

    @field_validator("income_tax_rate")
    @classmethod
    def must_be_percentage(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("income_tax_rate must be between 0 and 1")
        return v
    
    @field_validator("starting_cash")
    @classmethod
    def must_be_nonnegative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("starting_cash must be >= 0")
        return v
