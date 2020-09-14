class Bank:
    TEJARAT = "Tejarat"
    SAMAN = "Saman"

    BANK_CHOICES = (
        (TEJARAT, "Tejarat"),
        (SAMAN, "Saman"),
    )


class CostModel:
    CPA = "cpa"
    CPC = "cpc"
    CPM = "cpm"

    COST_MODEL_CHOICES = (
        (CPA, "cpa"),
        (CPC, "cpc"),
        (CPM, "cpm"),
    )