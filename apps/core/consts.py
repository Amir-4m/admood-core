class Bank:
    TEJARAT = "Tejarat"
    SAMAN = "Saman"

    BANK_CHOICES = (
        (TEJARAT, "Tejarat"),
        (SAMAN, "Saman"),
    )


class CostModel:
    CPA = 1
    CPC = 2
    CPV = 3
    CPI = 4
    CPR = 5

    COST_MODEL_CHOICES = (
        (CPA, "cpa"),
        (CPC, "cpc"),
        (CPV, "cpv"),
        (CPI, "cpi"),
        (CPR, "cpr"),

    )
