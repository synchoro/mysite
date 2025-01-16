$(function () {
    $('#contents div[id != "tab1"]').hide();

    tabID = window.location.href.slice(-5);
    $('#contents div').hide();
    $(tabID).show();
    $(".current").removeClass("current");
    $('a[href="' + tabID + '"]').addClass("current");

    // タブをクリック
    $("a").click(function () {
        // 一度全てのコンテンツを非表示にする
        $("#contents div").hide();

        // 選択されたコンテンツを再表示する
        $($(this).attr("href")).show();

        // 現在のcurrentクラスを削除
        $(".current").removeClass("current");

        // 選択されたタブ（自分自身）にcurrentクラスを追加
        $(this).addClass("current");


        return false;
    });

});