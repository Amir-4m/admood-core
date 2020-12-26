function numberWithCommas(x) {
    return numeral(x).format("0,0")
}

window.addEventListener('load', function () {
    var dailyBudgetInput = document.getElementById('id_daily_budget');
    var totalBudgetInput = document.getElementById('id_total_budget');

    if (dailyBudgetInput != null && dailyBudgetInput.value != null) {
        dailyBudgetInput.value = numberWithCommas(dailyBudgetInput.value)
    }
    if (totalBudgetInput != null && totalBudgetInput.value != null) {
        totalBudgetInput.value = numberWithCommas(totalBudgetInput.value)
    }
    dailyBudgetInput.addEventListener('keyup', function () {
        dailyBudgetInput.value = numberWithCommas(document.getElementById('id_daily_budget').value.replace(',', ''));
    });
    totalBudgetInput.addEventListener('keyup', function () {
        totalBudgetInput.value = numberWithCommas(document.getElementById('id_total_budget').value.replace(',', ''));
    })

});
