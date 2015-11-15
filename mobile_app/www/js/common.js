document.addEventListener('open.fndtn.offcanvas', function () {
    var menuHeight = $('#canvas-menu').height()+10 /*10px margin*/;
    var canvasContainer = $('#canvas-container');
    if(menuHeight > canvasContainer.height())
        canvasContainer.height(menuHeight);
    alert("Zdrizhne!!11");
});

document.addEventListener('close.fndtn.offcanvas', function () {
    $('#tcon-trigger > .tcon').removeClass('tcon-transform');
    $('#canvas-container').css('height', 'auto');
});

$(window).resize(function(){
    $('.off-canvas-wrap').foundation('offcanvas', 'hide', 'move-right');
});