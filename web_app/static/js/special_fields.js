function SpecialField(id, init_draw=false, fill_shape_value=false, max_nodes_value=100){
    this.canvas = document.getElementById(id);
    
    this.reOffset = function(){
        var BB= this.canvas.getBoundingClientRect();
        this.offsetX=BB.left;
        this.offsetY=BB.top;        
    }
    this.reOffset();
    var that = this;
    //window.onscroll=function(e){
    //    window.onscroll(e);
    //    that.reOffset(); 
    //}
    this.on_max_nodes_f = function(){
        
    }
    this.on_each_node_f = function(){

    }
    this.on_init_nodes = function(){

    }


    // handle mouseup events
    this.myUp = function(e){
        // tell the browser we're handling this mouse event
        e.preventDefault();
        e.stopPropagation();

        // clear all the dragging flags
        that.dragok = false;
        for(var i=0;i<that.shapes.length;i++){
            that.shapes[i].isDragging=false;
        }
        that.on_each_node_f();
        if(that.shapes.length == that.max_nodes)
        that.on_max_nodes_f();
    }

    // handle mousedown events
    this.myDown = function(e){

        // tell the browser we're handling this mouse event
        e.preventDefault();
        e.stopPropagation();

        // get the current mouse position
        var mx=parseInt(e.clientX-that.offsetX);
        var my=parseInt(e.clientY-that.offsetY);

        // test each shape to see if mouse is inside
        that.dragok=false;
        for(var i=0;i<that.shapes.length;i++){
            var s = that.shapes[i];
            // decide if the shape is a rect or circle               
            if(s.width){
            // test if the mouse is inside this rect
            if(mx>s.x && mx<s.x+s.width && my>s.y && my<s.y+s.height){
                // if yes, set that rects isDragging=true
                that.dragok=true;
                s.isDragging=true;
            }
            }else{
            var dx=s.x-mx;
            var dy=s.y-my;
            // test if the mouse is inside this circle
            if(dx*dx+dy*dy<s.r*s.r){
                that.dragok=true;
                s.isDragging=true;
            }
            }
        }
        if (!that.dragok && that.shapes.length <that.max_nodes){
            that.shapes.push({x:mx,y:my,r:7,fill:"#0c64e8",isDragging:false});
            that.myDown(e);
        }
        // save the current mouse position
        that.startX=mx;
        that.startY=my;

        // draw results
        that.draw();
    }

    // handle mouse moves
    this.myMove = function(e){
        // if we're dragging anything...
        if (that.dragok){

            // tell the browser we're handling this mouse event
            e.preventDefault();
            e.stopPropagation();

            // get the current mouse position
            var mx=parseInt(e.clientX-that.offsetX);
            var my=parseInt(e.clientY-that.offsetY);

            // calculate the distance the mouse has moved
            // since the last mousemove
            var dx=mx-that.startX;
            var dy=my-that.startY;

            // move each rect that isDragging 
            // by the distance the mouse has moved
            // since the last mousemove
            for(var i=0;i<that.shapes.length;i++){
                var s=that.shapes[i];
                if(s.isDragging){
                    s.x+=dx;
                    s.y+=dy;
                }
            }

            // redraw the scene with the new rect positions
            that.draw();

            // reset the starting mouse position for the next mousemove
            that.startX=mx;
            that.startY=my;

        }
    };

    // redraw the scene
    this.draw = function() {
        this.clear();
        if(this.shapes.length ==0)return;
        this.ctx.beginPath();
        this.ctx.moveTo(this.shapes[0].x, this.shapes[0].y);
        var max_length = this.max_nodes>0? Math.min(this.shapes.length,this.max_nodes):this.shapes.length;
        for(var index=1; index<max_length;index++) {
            this.ctx.lineTo(this.shapes[index].x, this.shapes[index].y);
        }
        if(this.fill_shape){
            this.ctx.fillStyle = "rgba(0, 0, 0, 0.5)"
            this.ctx.fill();
        }
        this.ctx.stroke();
        this.ctx.closePath();
        
        for(var index=0; index<this.shapes.length;index++) {
            this.circle(this.shapes[index]);
        }
    };

    // clear the canvas
    this.clear = function(clear_shapes=false) {
        if(clear_shapes)
            this.shapes = [];
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    };
    // draw a single rect
    this.circle = function(c) {
        this.ctx.fillStyle=c.fill;
        this.ctx.beginPath();
        this.ctx.arc(c.x,c.y,c.r,0,Math.PI*2);
        this.ctx.closePath();
        this.ctx.fill();
    };
    
    
    // listen for mouse events
    this.canvas.onmousedown = this.myDown;
    this.canvas.onmouseup = this.myUp;
    this.canvas.onmousemove = this.myMove;

    this.ctx = this.canvas.getContext("2d");
    this.ctx.lineWidth=2;
    this.ctx.strokeStyle='blue';

    // drag related variables
    this.dragok = false;
    this.startX;
    this.startY;

    // an array of objects that define different shapes
    this.shapes = [];

    this.fill_shape = fill_shape_value;
    this.max_nodes = max_nodes_value;
    
    if(init_draw) this.draw();
    
}