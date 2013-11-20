if (!window.ziply){
    window.ziply = {};
}

ziply.canvas = null;
ziply.stage = null;
ziply.resize = function()
{           
    //console.log( window.innerWidth + " " + window.innerHeight );
    ziply.stage.canvas.width = window.innerWidth;
    ziply.stage.canvas.height = window.innerHeight-10;
    ziply.nextButton.x = ziply.stage.canvas.width-95;
    ziply.nextButton.y = ziply.stage.canvas.height-55;
    ziply.email_text.y = ziply.stage.canvas.height-60

    ziply.signature_box.graphics.clear();
    ziply.signature_box.graphics.beginFill( '#FFFFFF' );
    ziply.signature_box.graphics.drawRect( 0 , 0 , ziply.stage.canvas.width , ziply.stage.canvas.height  );
    ziply.signature_box.graphics.setStrokeStyle( 2 , "round" ).beginStroke( '#000000' );
    ziply.signature_box.graphics.drawRect( 10 , 10 , ziply.stage.canvas.width - 20 , ziply.stage.canvas.height-20  );
    ziply.signature_box.graphics.moveTo( 30 , ziply.stage.canvas.height - 80 ).lineTo( ziply.stage.canvas.width - 30, ziply.stage.canvas.height - 80 );
    
    window.ziply.stage.update();
}
ziply.init = function( e )
{
    ziply.imageData = [];
    ziply.textData = [];
    ziply.current = 0;

    ziply.item_id = document.getElementById( 'item_id' ).value;
    ziply.item_userid = document.getElementById( 'item_userid' ).value;
    ziply.item_name = document.getElementById( 'item_name' ).value;
    ziply.textData = document.getElementById( 'item_signers' ).value.split( '\n' );

    ziply.canvas = document.getElementById( "signature_canvas" );
    ziply.stage = new createjs.Stage( ziply.canvas );

    ziply.stage.enableDOMEvents( true );
    createjs.Touch.enable( ziply.stage );

    ziply.signature_box = new createjs.Shape();
    ziply.stage.addChild( ziply.signature_box );

    ziply.nextButton = new createjs.Container();
    
    ziply.buttonShape = new createjs.Shape();
    ziply.buttonShape.graphics.setStrokeStyle( 2 ,"round" ).beginStroke( '#000000' );
    ziply.buttonShape.graphics.beginFill( '#428bca' );
    ziply.buttonShape.graphics.drawRoundRect( 0 , 0 , 80 , 40 , 5 );
    ziply.nextButton.addChild( ziply.buttonShape );
    
    ziply.buttonText = new createjs.Text( "", "24px Arial, Helvetica, sans-serif", "#FFF" );
    ziply.buttonText.x = 16;
    ziply.buttonText.y = 6;
    ziply.buttonText.text = "next";
    ziply.buttonText.textAlign = "left";
    ziply.buttonText.textBaseline = "top";
    ziply.nextButton.addChild( ziply.buttonText );

    ziply.email_text = new createjs.Text( "", "18px Arial, Helvetica, sans-serif", "#000" );
    ziply.email_text.x = 20;
    ziply.email_text.lineHeight = 22;
    var a = ziply.textData[ ziply.current ].split(",")
    ziply.email_text.text = a.shift() + "\n" + a.join(",").replace(/^\s+/,"");
    ziply.email_text.textAlign = "left";
    ziply.email_text.textBaseline = "top";
    ziply.stage.addChild( ziply.email_text );

    ziply.doc_text = new createjs.Text( "", "18px Arial, Helvetica, sans-serif", "#000" );
    ziply.doc_text.x = 20;
    ziply.doc_text.y = 20;
    ziply.doc_text.lineHeight = 20;
    ziply.doc_text.text = ziply.item_name + "\n" + new Date().toString();
    ziply.doc_text.textAlign = "left";
    ziply.doc_text.textBaseline = "top";
    ziply.stage.addChild( ziply.doc_text );

    ziply.signature = new createjs.Shape();
    ziply.stage.addChild( ziply.signature );

    ziply.stage.addChild( ziply.nextButton );

    createjs.Ticker.setFPS( 32 );
    createjs.Ticker.addEventListener( "tick" , ziply.stage );
    window.addEventListener( 'resize' , ziply.resize , false );
    ziply.stage.addEventListener( "pressmove" , ziply.signature_pressmove );
    ziply.stage.addEventListener( "pressup" , ziply.signature_pressup );
    ziply.stage.addEventListener( "mouseover" , ziply.signature_mouseover );
    ziply.stage.addEventListener( "mouseout" , ziply.signature_mouseout );
    ziply.stage.addEventListener( "mousedown" , ziply.signature_mousedown );

    ziply.nextButton.addEventListener( "pressmove" , ziply.nextButton_pressmove );
    ziply.nextButton.addEventListener( "pressup" , ziply.nextButton_pressup );
    ziply.nextButton.addEventListener( "mouseover" , ziply.nextButton_mouseover );
    ziply.nextButton.addEventListener( "mouseout" , ziply.nextButton_mouseout );
    ziply.nextButton.addEventListener( "mousedown" , ziply.nextButton_mousedown );

    ziply.resize();
}
ziply.nextButton_pressmove = function( event ){
    event.stopImmediatePropagation();
    console.log("nextButton_pressmove");
}
ziply.nextButton_pressup = function( event ){
    event.stopImmediatePropagation();
    console.log("nextButton_pressup");
}
ziply.nextButton_mouseover = function( event ){
    event.stopImmediatePropagation();
    console.log("nextButton_mouseover");
}
ziply.nextButton_mouseout = function( event ){
    event.stopImmediatePropagation();
    console.log("nextButton_mouseout");
}
ziply.nextButton_mousedown = function( event ){
    event.stopImmediatePropagation();
    console.log("nextButton_mousedown");
    //capture canvas
    ziply.nextButton.visible = false;
    ziply.stage.update();
    ziply.stage.cache( 0 , 0 , ziply.stage.canvas.width , ziply.stage.canvas.height , 1 );
    ziply.imageData.push( ziply.stage.getCacheDataURL() );
    ziply.stage.uncache();
    ziply.nextButton.visible = true;
    //clear canvas
    ziply.signature.graphics.clear();
    ziply.stage.update();
    ziply.current++;
    if( ziply.textData.length <= ziply.current ){
        ziply.finalText = new createjs.Text( "", "40px Arial, Helvetica, sans-serif", "#000" );
        ziply.finalText.text = "Uploading...";
        ziply.stage.addChild( ziply.finalText );
        ziply.finalText.snapToPixel = true;
        ziply.finalText.textAlign = "center";
        ziply.finalText.textBaseline = "middle";
        ziply.finalText.x = ziply.stage.canvas.width/2;
        ziply.finalText.y = ziply.stage.canvas.height/2;
    
        ziply.email_text.visible = false;
        ziply.doc_text.visible = false;
        ziply.signature_box.graphics.clear();
        ziply.signature_box.graphics.beginFill( '#FFFFFF' );
        ziply.signature_box.graphics.drawRect( 0 , 0 , ziply.stage.canvas.width , ziply.stage.canvas.height  );
        ziply.nextButton.visible = false;
        ziply.signature.graphics.clear();
        ziply.stage.update();
        var formData = new FormData();
        var len = ziply.imageData.length;
        formData.append( "signature_length" , len );
        for ( var i=0 ; i<len ; i++ ){ 
            formData.append( "s_" + i , ziply.imageData[i] );
        }
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange=function(){
            if( xhr.readyState==4 && xhr.status==200){
                ziply.finalText.text = "Complete";
                window.location.href = "/agreements";
            }
        }
        xhr.open( "POST" , '/draft/complete/' + ziply.item_id , true );
        xhr.send( formData );



    }else{
        var a = ziply.textData[ ziply.current ].split(",");
        ziply.email_text.text = a.shift() + "\n" + a.join(",").replace(/^\s+/,"");
    }
}

ziply.signature_pressmove = function( event ){
    console.log("signature_pressmove");
    var midPt = new createjs.Point( ziply.oldPt.x + ziply.stage.mouseX>>1, ziply.oldPt.y + ziply.stage.mouseY>>1);
    ziply.signature.graphics.setStrokeStyle( 2 , 'round', 'round').beginStroke("#000").moveTo( midPt.x , midPt.y ).curveTo( ziply.oldPt.x , ziply.oldPt.y , ziply.oldMidPt.x , ziply.oldMidPt.y );
    ziply.oldPt.x = ziply.stage.mouseX;
    ziply.oldPt.y = ziply.stage.mouseY;
    ziply.oldMidPt.x = midPt.x;
    ziply.oldMidPt.y = midPt.y;
    ziply.stage.update();
}
ziply.signature_pressup = function( event ){
    console.log("signature_pressup");
}
ziply.signature_mouseover = function( event ){
    console.log("signature_mouseover");
}
ziply.signature_mouseout = function( event ){
    console.log("signature_mouseout");
}
ziply.signature_mousedown = function( event ){
    console.log("signature_mousedown");
    ziply.oldPt = new createjs.Point( ziply.stage.mouseX , ziply.stage.mouseY );
    ziply.oldMidPt = ziply.oldPt;
}

$(document).ready(function() {
    ziply.init();
    document.ontouchmove = function(e) {e.preventDefault()};
});