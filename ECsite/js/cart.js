
document.addEventListener('DOMContentLoaded', function () {
    var plusBtn1 = document.getElementById('plus1');
    var minusBtn1 = document.getElementById('minus1');
    var numberBox1 = document.getElementById('number1');
    var priceBox1 = document.querySelector('.item_price_total1');
    var countBox = document.getElementById('count');

    var number1 = 0;
    var pricePerItem1 = 999999999;
    numberBox1.value = number1;

    var priceSum1 = 0;
    priceBox1.textContent = '¥' + priceSum1.toLocaleString();

    plusBtn1.addEventListener('click', function () {
        if (number1 >= 0 && number1 <= 4) {
            number1++;
            numberBox1.value = number1;

            priceSum1 = number1 * pricePerItem1;
            priceBox1.textContent = '¥' + priceSum1.toLocaleString();

            updateTotalPrice();
        }
    });

    minusBtn1.addEventListener('click', function () {
        if (number1 > 0 && number1 <= 5) {
            number1--;
            numberBox1.value = number1;

            priceSum1 = number1 * pricePerItem1;
            priceBox1.textContent = '¥' + priceSum1.toLocaleString();

            updateTotalPrice();
        }
    });


    function updateTotalPrice() {
        var totalPrice = number1 * pricePerItem1 + number2 * pricePerItem2 + number3 * pricePerItem3;
        countBox.value = number1 + number2 + number3;
        document.getElementById('totle_price').value = '¥' + totalPrice.toLocaleString();
    }


    // 二番目の商品

    var plusBtn2 = document.getElementById('plus2');
    var minusBtn2 = document.getElementById('minus2');
    var numberBox2 = document.getElementById('number2');
    var priceBox2 = document.querySelector('.item_price_total2');
    var countBox = document.getElementById('count');

    var number2 = 0;
    var pricePerItem2 = 99999999;
    numberBox2.value = number2;

    var priceSum2 = 0;
    priceBox2.textContent = '¥' + priceSum2.toLocaleString();

    plusBtn2.addEventListener('click', function () {
        if (number2 >= 0 && number2 < 5) {
            number2++;
            numberBox2.value = number2;

            priceSum2 = number2 * pricePerItem2;
            priceBox2.textContent = '¥' + priceSum2.toLocaleString();

            updateTotalPrice();
        }
    });

    minusBtn2.addEventListener('click', function () {
        if (number2 > 0 && number2 <= 5) {
            number2--;
            numberBox2.value = number2;

            priceSum2 = number2 * pricePerItem2;
            priceBox2.textContent = '¥' + priceSum2.toLocaleString();

            updateTotalPrice();
        }
    });

    function updateTotalPrice() {
        var totalPrice = number1 * pricePerItem1 + number2 * pricePerItem2 + number3 * pricePerItem3;
        countBox.value = number1 + number2 + number3;
        document.getElementById('totle_price').value = '¥' + totalPrice.toLocaleString();
    }

    // 三番目の商品


    var plusBtn3 = document.getElementById('plus3');
    var minusBtn3 = document.getElementById('minus3');
    var numberBox3 = document.getElementById('number3');
    var priceBox3 = document.querySelector('.item_price_total3');
    var countBox = document.getElementById('count');

    var number3 = 0;
    var pricePerItem3 = 1;
    numberBox3.value = number3;

    var priceSum3 = 0;
    priceBox3.textContent = '¥' + priceSum3.toLocaleString();

    plusBtn3.addEventListener('click', function () {
        if (number3 >= 0 && number3 < 5) {
            number3++;
            numberBox3.value = number3;

            priceSum3 = number3 * pricePerItem3;
            priceBox3.textContent = '¥' + priceSum3.toLocaleString();

            updateTotalPrice();
        }
    });

    minusBtn3.addEventListener('click', function () {
        if (number3 > 0 && number3 <= 5) {
            number3--;
            numberBox3.value = number3;

            priceSum3 = number3 * pricePerItem3;
            priceBox3.textContent = '¥' + priceSum3.toLocaleString();

            updateTotalPrice();
        }
    });

    function updateTotalPrice() {
        var totalPrice = number1 * pricePerItem1 + number2 * pricePerItem2 + number3 * pricePerItem3;
        countBox.value = number1 + number2 + number3;
        document.getElementById('totle_price').value = '¥' + totalPrice.toLocaleString();
    }

    // 送信ボタン
    var checkoutButton = document.getElementById('checkout_button');
    var messageContainer = document.getElementById('messageContainer');
    var myImage = document.getElementById('myImage');

    checkoutButton.addEventListener('click', function () {
        var message = `合計${countBox.value}点、${document.getElementById('totle_price').value}円のお買い上げ、誠にありがとうございます！`;
        messageContainer.textContent = message;


    });


    checkoutButton.addEventListener('click', function () { myImage.style.display = "block"; })


});












