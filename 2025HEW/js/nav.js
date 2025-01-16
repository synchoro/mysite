$(".open__btn").click(function () {//ボタンがクリックされたら
    $(this).toggleClass('active');//ボタン自身に activeクラスを付与し
    $(".header__navigation").toggleClass('panelactive');//ナビゲーションにpanelactiveクラスを付与
});

$(".header__navigation a").click(function () {//ナビゲーションのリンクがクリックされたら
    $(".open__btn").removeClass('active');//ボタンの activeクラスを除去し
    $(".header__navigation").removeClass('panelactive');//ナビゲーションのpanelactiveクラスも除去
});